"""
Data ingestion module for the CCREC Dashboard.
Handles file selection, CSV reading, data cleaning, and enrichment.
"""

import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
from tabulate import tabulate
import os
import sys

from constants import (
    SERVICE_CODE_TO_TYPE,
    CODE_MAPPINGS,
    SERVICE_COLUMN_RENAME,
    AY_COLUMNS_TO_KEEP,
    SERVICE_COLUMNS
)

import district_names

def print_data_overview(ay_df: pd.DataFrame, agg_services: pd.DataFrame) -> None:
    """Print a summary table of data counts by year."""
    students_per_year = ay_df.groupby('High School AY')['National CCREC Student ID'].nunique()
    students_with_service_per_year = (
        agg_services.groupby('High School AY')['National CCREC Student ID'].nunique()
        if 'National CCREC Student ID' in agg_services.columns
        else pd.Series(dtype='int64')
    )
    overview_df = pd.merge(
        students_per_year, students_with_service_per_year,
        left_index=True, right_index=True, how='outer'
    ).fillna(0)
    overview_df.rename(columns={
        'National CCREC Student ID_x': 'Students in AY file(s)',
        'National CCREC Student ID_y': 'Students in service file(s)',
    }, inplace=True)
    overview_df.reset_index(inplace=True)
    print('---------------------')
    print('Data counts:')
    print(tabulate(overview_df, showindex=False, tablefmt='rounded_outline', headers='keys'))


def create_service_aggregation(service_df: pd.DataFrame) -> tuple:
    """
    Aggregate raw service data by month/type and by student/month/type.

    Parameters
    ----------
    service_df : pd.DataFrame
        Raw service data with columns: Academic Year, Service Date,
        Service Type Code, Service Time, National CCREC Student ID.

    Returns
    -------
    tuple of (pd.DataFrame, pd.DataFrame)
        - Aggregated services by year/month/type (total minutes, student count)
        - Duration by student/month/type (for threshold filtering)
    """
    print('- Aggregating service data')
    service_df = service_df.copy()
    service_df['Service Date'] = pd.to_datetime(service_df['Service Date'])
    service_df['Service Type Code'] = service_df['Service Type Code'].map(SERVICE_CODE_TO_TYPE)

    aggregated_services = (
        service_df
        .groupby(['Academic Year', service_df['Service Date'].dt.month, 'Service Type Code'])
        .agg(service_mins=('Service Time', 'sum'), students=('National CCREC Student ID', 'nunique'))
        .reset_index()
        .rename(columns={
            'Academic Year': 'High School AY',
            'Service Date': 'Month',
            'service_mins': 'Total Minutes',
            'students': 'Student Count',
        })
    )

    duration_by_student_month_type = (
        service_df
        .groupby([
            'Academic Year',
            service_df['Service Date'].dt.month,
            'Service Type Code',
            'National CCREC Student ID',
            'Secondary School Name',
        ])['Service Time']
        .sum()
        .reset_index()
        .rename(columns={
            'Academic Year': 'High School AY',
            'Service Date': 'Month',
            'Service Time': 'Total Time',
        })
    )

    return aggregated_services, duration_by_student_month_type

def create_college_visits_df(ay_df: pd.DataFrame) -> pd.DataFrame:
    """Extract and process college visit IPEDS data."""
    college_visits = ay_df[~ay_df['IPEDS numbers of the Schools Visited'].isna()][
        ['National CCREC Student ID', 'IPEDS numbers of the Schools Visited']
    ].copy()
    college_visits['IPEDS numbers of the Schools Visited'] = (
        college_visits['IPEDS numbers of the Schools Visited'].str.split(',')
    )
    college_visits = college_visits.explode('IPEDS numbers of the Schools Visited')
    college_visits['IPEDS numbers of the Schools Visited'] = (
        college_visits['IPEDS numbers of the Schools Visited'].str.strip()
    )
    college_visits = (
        college_visits
        .groupby('National CCREC Student ID')['IPEDS numbers of the Schools Visited']
        .agg(list)
        .reset_index()
    ).rename(columns={
        'IPEDS numbers of the Schools Visited': 'Full IPEDs Visited List'
    })
    return college_visits

def _get_school_groups(ay_df: pd.DataFrame) -> dict:
    '''Looks at ay_df and returns dict of any school groupings/renames.'''
    rename_counts_by_school = ay_df.groupby(['Secondary School Name', 'School Group Name'], dropna=False).size().reset_index().rename(columns={0: 'Row Count'})
    rename_counts_by_school.sort_values(by=['Secondary School Name', 'Row Count'], inplace=True, ascending=[True, False])
    rename_counts_by_school.drop_duplicates(subset='Secondary School Name', keep='first', inplace=True)
    rename_counts_by_school.dropna(subset='School Group Name', inplace=True)
    rename_dict = rename_counts_by_school.set_index('Secondary School Name')['School Group Name'].to_dict()
    return rename_dict


def _get_data_path(filename: str) -> str:
    """Get path to bundled data file (supports PyInstaller)."""
    if hasattr(sys, '_MEIPASS'):
        bundle_dir = sys._MEIPASS
    else:
        bundle_dir = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(bundle_dir, filename)


def _get_locale(ay_df: pd.DataFrame) -> pd.DataFrame:
    """Enrich AY data with locale information from NCES lookup."""
    print('- Finding locale based on NCES ID')
    ay_len = len(ay_df)

    locale_pickle_path = _get_data_path('locale_data.pkl')
    nces_df = pd.read_pickle(locale_pickle_path)
    ay_df = ay_df.merge(nces_df, how='left', left_on='School NCES ID', right_on='NCESSCH')

    missing_ay = ay_df[ay_df['NCESSCH'].isna()].copy()
    missing_len = len(missing_ay)
    missing_ay[['LOCALE_NAME', 'LOCAL_CATEGORY']] = 'Unknown'
    if missing_len > 0:
        print(f'  {missing_len} of {ay_len} records missing NCES ID for locale lookup.')

    ay_df['Year of School Year Start'] = ay_df['High School AY'].str[:4].astype('int')
    ay_df = ay_df[
        (ay_df['Year of School Year Start'] >= ay_df['START_YEAR'])
        & (ay_df['Year of School Year Start'] <= ay_df['END_YEAR'])
    ]

    ay_df = pd.concat([ay_df, missing_ay])
    ay_df.drop(columns=['NCESSCH', 'START_YEAR', 'END_YEAR'], inplace=True, errors='ignore')
    ay_df.rename(columns={
        'LOCALE': 'Locale Code',
        'LOCALE_NAME': 'Full Locale',
        'LOCAL_CATEGORY': 'Locale',
    }, inplace=True)

    final_len = len(ay_df)
    if final_len != ay_len:
        print(f'  WARNING: {final_len} records after locale merge (expected {ay_len}).')

    return ay_df


def _get_district(ay_df: pd.DataFrame) -> pd.DataFrame:
    """Enrich AY data with district information from NCES lookup."""
    print('- Finding district based on NCES ID')
    ay_len = len(ay_df)

    district_pickle_path = _get_data_path('district_data.pkl')
    district_df = pd.read_pickle(district_pickle_path)
    ay_df = ay_df.merge(district_df, how='left', left_on='School NCES ID', right_on='NCESSCH')

    missing_ay = ay_df[ay_df['NCESSCH'].isna()].copy()
    missing_len = len(missing_ay)
    missing_ay['DISTRICT_NAME'] = 'Unknown'
    if missing_len > 0:
        print(f'  {missing_len} of {ay_len} records missing NCES ID for district lookup.')

    ay_df = ay_df[
        (ay_df['Year of School Year Start'] >= ay_df['START_YEAR'])
        & (ay_df['Year of School Year Start'] <= ay_df['END_YEAR'])
    ]

    ay_df = pd.concat([ay_df, missing_ay])
    ay_df.drop(columns=['NCESSCH', 'START_YEAR', 'END_YEAR'], inplace=True, errors='ignore')
    ay_df.rename(columns={'DISTRICT_NAME': 'District'}, inplace=True)

    final_len = len(ay_df)
    if final_len != ay_len:
        print(f'  WARNING: {final_len} records after district merge (expected {ay_len}).')

    return ay_df


def _map_codes_to_strings(ay_df: pd.DataFrame) -> pd.DataFrame:
    """Map numeric codes to human-readable strings."""
    for col, mapping in CODE_MAPPINGS.items():
        if col in ay_df.columns:
            ay_df[col] = ay_df[col].map(mapping).fillna(ay_df[col])
    return ay_df


def _get_individual_df(file_type: str, file_pattern: str, file_path_list: list):
    """Search file list for a matching pattern and return DataFrame or error string."""
    dir_name = file_path_list[0].split('/')[-2] if file_path_list else 'unknown'

    matching_files = [
        fp for fp in file_path_list
        if file_pattern in fp.split('/')[-1].lower() and fp.endswith('.csv')
    ]

    if not matching_files:
        return f'ERROR: {file_type} file not found in folder: {dir_name}'

    if len(matching_files) > 1:
        print(f'  Multiple {file_type} files found. Using: {matching_files[0].split("/")[-1]}')

    return pd.read_csv(matching_files[0], low_memory=False)


def _get_ay_and_service(file_path_list: list):
    """Extract AY and service DataFrames from a file list."""
    ay_search = _get_individual_df('AY', 'aydata', file_path_list)
    service_search = _get_individual_df('Service', 'servicedata', file_path_list)

    errors = []
    if isinstance(ay_search, str):
        errors.append(ay_search)
    if isinstance(service_search, str):
        errors.append(service_search)

    if errors:
        return '\n'.join(errors)

    return {'ay_df': ay_search, 'service_df': service_search}


def _process_subdirs(subdir_list: list):
    """Process multiple subdirectories containing AY/service file pairs."""
    ay_df = pd.DataFrame()
    service_df = pd.DataFrame()

    for subdir in subdir_list:
        file_path_list = [
            subdir + '/' + f
            for f in os.listdir(subdir)
            if not os.path.isdir(subdir + '/' + f)
        ]
        result = _get_ay_and_service(file_path_list)
        if isinstance(result, str):
            return result
        ay_df = pd.concat([ay_df, result['ay_df']])
        service_df = pd.concat([service_df, result['service_df']])

    return {'ay_df': ay_df, 'service_df': service_df}


def load_data(input_path: str) -> dict:
    """
    Load and process CCREC data from a folder.

    Parameters
    ----------
    input_path : str
        Path to data folder, or 'default' for file dialog.

    Returns
    -------
    dict or str
        Dictionary with keys: 'ay_df', 'agg_services_df',
        'duration_by_student_month_type', 'college_visits'.
        Returns error string on failure.
    """
    if input_path == 'default':
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        root.update()
        try:
            selected_dir = filedialog.askdirectory(
                parent=root, title='Please select source file folder'
            )
        finally:
            root.destroy()

        if not selected_dir:
            return 'ERROR: No source file folder selected.'
        print(f'- Reading data from: {selected_dir}')
    else:
        if os.path.isdir(input_path):
            selected_dir = input_path
        else:
            return 'ERROR: The input path is not a valid folder.'

    # Scan directory
    files = []
    subdirs = []
    for element in os.listdir(selected_dir):
        element_path = os.path.join(selected_dir, element)
        if os.path.isdir(element_path):
            subdirs.append(element_path)
        else:
            files.append(element_path)

    # Determine file structure and load
    has_ay = any('aydata' in f.split('/')[-1].lower() for f in files if f.endswith('.csv'))
    has_service = any('servicedata' in f.split('/')[-1].lower() for f in files if f.endswith('.csv'))

    if has_ay and has_service:
        print(f'- AY and service files found in {selected_dir}')
        raw_dfs = _get_ay_and_service(files)
    elif subdirs:
        print(f'- Searching through {len(subdirs)} subdirectories in {selected_dir}')
        raw_dfs = _process_subdirs(subdirs)
    else:
        return (
            f'ERROR: Files not found in {selected_dir}. '
            'Ensure AY filename contains "aydata" and service filename contains "servicedata" (CSV format).'
        )

    if isinstance(raw_dfs, str):
        return raw_dfs

    ay_df = raw_dfs['ay_df']
    service_df = raw_dfs['service_df']
    print('- AY and service DataFrames loaded from CSV files')

    # Select and rename columns
    available_columns = [c for c in AY_COLUMNS_TO_KEEP if c in ay_df.columns]
    ay_df = ay_df[available_columns].copy()
    ay_df.rename(columns={'School NCES ID': 'School NCES ID INT'}, inplace=True)
    ay_df['School NCES ID'] = ay_df['School NCES ID INT'].astype('string').str.pad(
        width=12, side='left', fillchar='0'
    )
    ay_df.drop(columns='School NCES ID INT', inplace=True)

    # Enrich with locale and district
    #ay_df = _get_locale(ay_df)
    #ay_df = _get_district(ay_df)

    # Fill NaN service columns and rename
    service_cols = [c for c in ay_df.columns if c.startswith('Service ') and 'Total' in c]
    for col in service_cols:
        ay_df[col] = ay_df[col].fillna(0)
    ay_df.rename(columns=SERVICE_COLUMN_RENAME, inplace=True)

    # Map codes to strings
    ay_df = _map_codes_to_strings(ay_df)
    ay_df['Grade Level'] = ay_df['Grade Level'].astype('string')

    # Pre-compute total service time
    available_service_cols = [c for c in SERVICE_COLUMNS if c in ay_df.columns]
    ay_df['Total Service Time'] = ay_df[available_service_cols].sum(axis=1) / 60

    # Aggregate services
    aggregated_services, student_duration_by_month = create_service_aggregation(service_df)

    # College visits
    ay_df['First College Attended IPEDS'] = ay_df['First College Attended IPEDS'].astype(str).str.replace('.0', '')

    college_visits = create_college_visits_df(ay_df)
    ay_df = ay_df.merge(college_visits, how='left', on='National CCREC Student ID')

    ay_df['Went on College Visit'] = ~ay_df['Full IPEDs Visited List'].isna()
    enrollment_null = ay_df['First College Attended IPEDS'].isna()
    visits_and_enrollment_not_null = ay_df['Went on College Visit'] & ~enrollment_null

    enrolled_was_visited = np.array([
        v in l if isinstance(l, list) else False
        for l,v in zip(ay_df['Full IPEDs Visited List'], ay_df['First College Attended IPEDS'])
    ])

    conditions = [
        ~ay_df['Went on College Visit'] & enrollment_null,
        ay_df['Went on College Visit'] & enrollment_null,
        ~ay_df['Went on College Visit'] & ~enrollment_null,
        visits_and_enrollment_not_null & enrolled_was_visited,
        visits_and_enrollment_not_null & ~enrolled_was_visited
    ]

    choices = [
        'Did not go on college visit, did not enroll in post secondary',
        'Went on college visit(s), did not enroll in post secondary',
        'Did not go on college visit, enrolled in post secondary',
        'Went on college visit(s), enrolled in post secondary at a visited school',
        'Went on college visit(s), enrolled in post secondary at a NON visited school',
    ]

    ay_df['College Visits and PSE'] = np.select(conditions, choices, default='Check your conditions Alex...')
    ay_df['Went on College Visit'] = ay_df['Went on College Visit'].map({True: 'Went on a college visit', False: 'Did not go on a college visit'})

    # Check for any saved school grouping and setting school display name
    if 'School Group Name' not in ay_df.columns:
        ay_df['School Group Name'] = None
    groups = _get_school_groups(ay_df)
    if len(groups) == 0:
        print('- No school rename/groupings found')
    else:
        print(f'- {len(groups)} schools with a rename/grouping found:')
        print(tabulate(groups.items(), headers=['Original School Name', 'Rename/Group Name'], tablefmt='rounded_outline'))

    ay_df['School Display Name'] = ay_df['Secondary School Name'].map(groups).fillna(ay_df['Secondary School Name'])

    print('- Data load complete!')
    print_data_overview(ay_df, student_duration_by_month)

    return {
        'ay_df': ay_df,
        'agg_services_df': aggregated_services,
        'duration_by_student_month_type': student_duration_by_month,
        'college_visits': college_visits,
        'renames': groups
    }


if __name__ == '__main__':
    pass