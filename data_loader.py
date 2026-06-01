# "data_loader.py"
"""
data_loader.py
Handles folder/file selection, CSV ingestion, NCES enrichment,
code-to-string mapping, and service aggregation.
Returns a dict of cleaned DataFrames consumed by the Dash app.
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog

import pandas as pd
from tabulate import tabulate

from constants import SERVICE_CODE_TO_TYPE


# ── Overview helper ────────────────────────────────────────────────────────────

def print_data_overview(ay_df: pd.DataFrame, agg_services: pd.DataFrame) -> None:
    """Print a summary table of student counts per academic year."""
    students_per_year = ay_df.groupby('High School AY')['National CCREC Student ID'].nunique()
    students_with_service = agg_services.groupby('High School AY')['National CCREC Student ID'].nunique()
    overview_df = pd.merge(
        students_per_year, students_with_service,
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


# ── Service aggregation ────────────────────────────────────────────────────────

def create_service_aggregation(
    service_df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Aggregate service records by academic year, calendar month, and service type.

    Returns
    -------
    aggregated_services
        Total minutes and unique student count per year / month / type.
    service_duration_by_student_month_type
        Per-student total service time per year / month / type.
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
            'Academic Year':    'High School AY',
            'Service Date':     'Month',
            'service_mins':     'Total Minutes',
            'students':         'Student Count',
        })
    )

    service_duration_by_student_month_type = (
        service_df
        .groupby([
            'Academic Year',
            service_df['Service Date'].dt.month,
            'Service Type Code',
            'National CCREC Student ID',
        ])['Service Time']
        .sum()
        .reset_index()
        .rename(columns={
            'Academic Year': 'High School AY',
            'Service Date':  'Month',
            'Service Time':  'Total Time',
        })
    )

    return aggregated_services, service_duration_by_student_month_type


# ── College visits ─────────────────────────────────────────────────────────────

def create_college_visits_df(ay_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a per-student list of visited IPEDS IDs from the AY data.

    Returns a DataFrame with:
        National CCREC Student ID | IPEDS numbers of the Schools Visited  (list)
    """
    college_visits = ay_df.loc[
        ~ay_df['IPEDS numbers of the Schools Visited'].isna(),
        ['National CCREC Student ID', 'IPEDS numbers of the Schools Visited'],
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
    )
    return college_visits


# ── NCES enrichment ────────────────────────────────────────────────────────────

def get_locale(ay_df: pd.DataFrame) -> pd.DataFrame:
    """Merge locale information onto ay_df using School NCES ID."""
    print('- Finding locale based on NCES ID')
    ay_len = len(ay_df)

    nces_df = pd.read_pickle(get_data_path('locale_data.pkl'))
    ay_df = ay_df.merge(nces_df, how='left', left_on='School NCES ID', right_on='NCESSCH')

    missing_ay = ay_df[ay_df['NCESSCH'].isna()].copy()
    missing_len = len(missing_ay)
    missing_ay.loc[:, ['LOCALE_NAME', 'LOCAL_CATEGORY']] = 'Unknown'
    if missing_len > 0:
        print(f'- {missing_len} of {ay_len} records are missing a matching NCES ID for locale lookup.')

    ay_df['Year of School Year Start'] = ay_df['High School AY'].str[:4].astype('int')
    ay_df = ay_df[
        (ay_df['Year of School Year Start'] >= ay_df['START_YEAR']) &
        (ay_df['Year of School Year Start'] <= ay_df['END_YEAR'])
    ]

    ay_df = pd.concat([ay_df, missing_ay], ignore_index=True)
    ay_df.drop(columns=['NCESSCH', 'START_YEAR', 'END_YEAR'], inplace=True)
    ay_df.rename(columns={
        'LOCALE':       'Locale Code',
        'LOCALE_NAME':  'Full Locale',
        'LOCAL_CATEGORY': 'Locale',
    }, inplace=True)

    final_len = len(ay_df)
    if final_len != ay_len:
        print(f'WARNING: {final_len} records after locale merge, expected {ay_len}.')

    return ay_df


def get_district(ay_df: pd.DataFrame) -> pd.DataFrame:
    """Merge district name onto ay_df using School NCES ID."""
    print('- Finding district based on NCES ID')
    ay_len = len(ay_df)

    district_df = pd.read_pickle(get_data_path('district_data.pkl'))
    ay_df = ay_df.merge(district_df, how='left', left_on='School NCES ID', right_on='NCESSCH')

    missing_ay = ay_df[ay_df['NCESSCH'].isna()].copy()
    missing_len = len(missing_ay)
    missing_ay.loc[:, 'DISTRICT_NAME'] = 'Unknown'
    if missing_len > 0:
        print(f'- {missing_len} of {ay_len} records are missing a matching NCES ID for district lookup.')

    ay_df = ay_df[
        (ay_df['Year of School Year Start'] >= ay_df['START_YEAR']) &
        (ay_df['Year of School Year Start'] <= ay_df['END_YEAR'])
    ]

    ay_df = pd.concat([ay_df, missing_ay], ignore_index=True)
    ay_df.drop(columns=['NCESSCH', 'START_YEAR', 'END_YEAR'], inplace=True)
    ay_df.rename(columns={'DISTRICT_NAME': 'District'}, inplace=True)

    final_len = len(ay_df)
    if final_len != ay_len:
        print(f'WARNING: {final_len} records after district merge, expected {ay_len}.')

    return ay_df


# ── Code → string mapping ──────────────────────────────────────────────────────

def map_codes_to_strings(ay_df: pd.DataFrame) -> pd.DataFrame:
    """Replace integer codes in ay_df with human-readable string labels."""
    code_mappings: dict[str, dict] = {
        'Gender Code': {
            1: 'Female',
            2: 'Male',
            3: 'Unknown',
            4: 'Gender Neutral',
        },
        'Ethnicity Code': {
            0: 'Not Hispanic or Latino',
            1: 'Hispanic or Latino',
            2: 'Unknown',
        },
        'Race Code': {
            1: 'American Indian or Alaskan Native',
            2: 'Asian',
            3: 'Black or African American',
            4: 'Native Hawaiian or Pacific Islander',
            5: 'White',
            6: 'Two or More Races',
            7: 'Unknown',
        },
        'HS Grad Status code': {
            1: 'Graduated',
            2: 'Did Not Graduate',
            3: 'Graduation Status Unknown',
            4: 'N/A',
            5: 'In Grade 13',
        },
        'FAFSA status code': {
            1: 'FAFSA Completed',
            2: 'FAFSA Not Completed',
            3: 'Not Collected',
            4: 'N/A',
        },
        'Algebra 1 Status': {
            1: 'Enrolled and Completed',
            2: 'Enrolled But Not Completed',
            3: 'Not Enrolled',
            4: 'N/A',
        },
    }
    for col, mapping in code_mappings.items():
        ay_df[col] = ay_df[col].map(mapping).fillna('Unknown')
    return ay_df


# ── Path helper (PyInstaller compatible) ───────────────────────────────────────

def get_data_path(filename: str) -> str:
    """Return the absolute path to a bundled data file."""
    bundle_dir = (
        sys._MEIPASS if hasattr(sys, '_MEIPASS')
        else os.path.abspath(os.path.dirname(__file__))
    )
    return os.path.join(bundle_dir, filename)


# ── File discovery helpers ─────────────────────────────────────────────────────

def get_individual_df(
    file_type: str,
    file_pattern: str,
    file_path_list: list[str],
) -> pd.DataFrame | str:
    """
    Search *file_path_list* for a CSV whose name contains *file_pattern*.

    Returns the loaded DataFrame, or an error string if not found / wrong format.
    """
    dir_name = file_path_list[0].split('/')[-2] if file_path_list else 'unknown'
    file_found = any(file_pattern in fp.split('/')[-1].lower() for fp in file_path_list)

    if file_found:
        valid_paths = [
            fp for fp in file_path_list
            if file_pattern in fp.split('/')[-1].lower() and fp.endswith('.csv')
        ]
        if not valid_paths:
            return f'ERROR: {file_type} file found in {dir_name} but not in CSV format.'
        if len(valid_paths) > 1:
            print(f'Multiple {file_type} files found in {dir_name}. '
                  f'Using {valid_paths[0].split("/")[-1]}.')
        return pd.read_csv(valid_paths[0], low_memory=False)

    return f'ERROR: {file_type} file not found in folder: {dir_name}.'


def get_ay_and_service(file_path_list: list[str]) -> dict | str:
    """
    Locate and load the AY and service CSV files from *file_path_list*.

    Returns ``{'ay_df': ..., 'service_df': ...}`` or a combined error string.
    """
    errors: list[str] = []
    ay_search      = get_individual_df('AY',      'aydata',      file_path_list)
    service_search = get_individual_df('Service', 'servicedata', file_path_list)

    if isinstance(ay_search, str):
        errors.append(ay_search)
    if isinstance(service_search, str):
        errors.append(service_search)
    if errors:
        return '\n'.join(errors)

    return {'ay_df': ay_search, 'service_df': service_search}


def process_subdirs(subdir_list: list[str]) -> dict | str:
    """
    Walk each subdirectory, loading and concatenating AY + service files.

    Returns a combined dict or an error string.
    """
    ay_frames: list[pd.DataFrame]      = []
    service_frames: list[pd.DataFrame] = []

    for subdir in subdir_list:
        file_path_list = [
            f'{subdir}/{f}' for f in os.listdir(subdir)
            if not os.path.isdir(f'{subdir}/{f}')
        ]
        result = get_ay_and_service(file_path_list)
        if isinstance(result, str):
            return result
        ay_frames.append(result['ay_df'])
        service_frames.append(result['service_df'])

    return {
        'ay_df':      pd.concat(ay_frames,      ignore_index=True),
        'service_df': pd.concat(service_frames, ignore_index=True),
    }


# ── Main entry point ───────────────────────────────────────────────────────────

def load_data(input: str) -> dict | str:
    """
    Load, clean, and enrich CCREC data from a user-selected or CLI-supplied folder.

    Parameters
    ----------
    input
        ``'default'`` opens a tkinter folder-selection dialog.
        Any other value is treated as an absolute folder path.

    Returns
    -------
    dict
        Keys: ``ay_df``, ``agg_services_df``,
        ``duration_by_student_month_type``, ``college_visits``.
    str
        An error message beginning with ``'ERROR:'`` on failure.
    """
    if input == 'default':
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        root.update()
        try:
            selected_dir = filedialog.askdirectory(
                parent=root,
                title='Please select source file folder',
            )
        finally:
            root.destroy()

        if not selected_dir:
            return 'ERROR: No source file folder selected.'
        print(f'- Reading data from: {selected_dir}')
    else:
        if not os.path.isdir(input):
            return 'ERROR: The path passed via the terminal is not a folder.'
        selected_dir = input

    files:   list[str] = []
    subdirs: list[str] = []
    for element in os.listdir(selected_dir):
        element_path = f'{selected_dir}/{element}'
        (subdirs if os.path.isdir(element_path) else files).append(element_path)

    has_ay      = any('aydata'      in f.split('/')[-1].lower() for f in files if f.endswith('.csv'))
    has_service = any('servicedata' in f.split('/')[-1].lower() for f in files if f.endswith('.csv'))

    if has_ay and has_service:
        print(f'- AY and service files found in {selected_dir}')
        raw_dfs = get_ay_and_service(files)
    elif subdirs:
        print(f'- Searching through {len(subdirs)} subfolders in {selected_dir}')
        raw_dfs = process_subdirs(subdirs)
    else:
        return (
            f'ERROR: Files not found in {selected_dir}. '
            'Ensure the AY file name contains "aydata", '
            'the service file contains "servicedata", '
            'and both are CSV files.'
        )

    if isinstance(raw_dfs, str):
        return raw_dfs

    ay_df: pd.DataFrame      = raw_dfs['ay_df']
    service_df: pd.DataFrame = raw_dfs['service_df']
    print('- AY and service DataFrames successfully loaded')

    # ── Column selection and NCES ID formatting ────────────────────────────────
    ay_df = ay_df[[
        'High School AY', 'Program Model Code', 'School NCES ID',
        'National CCREC Student ID', 'Student Type code', 'Gender Code',
        'Ethnicity Code', 'Race Code', 'Grade Level', 'Enrollment Status Code',
        'Service 1 Total',  'Service 2 Total',  'Service 3 Total',
        'Service 4 Total',  'Service 5 Total',  'Service 6 Total',
        'Service 7 Total',  'Service 8 Total',  'Service 9 Total',
        'Service 10 Total', 'Service 11 Total', 'Service 12 Total',
        'Service 13 Total', 'HS Grad Status code', 'FAFSA status code',
        'Algebra 1- Grade of Completion', 'Final Term GPA', 'Cumulative GPA',
        'IPEDS numbers of the Schools Visited', 'First College Attended Name',
        'First College Attended IPEDS', 'Graduated Y/N', 'Degree Title',
        'Dual Enrollment', 'Dual Enrollment Degree',
    ]].rename(columns={'School NCES ID': 'School NCES ID INT'})

    ay_df['School NCES ID'] = (
        ay_df['School NCES ID INT']
        .astype('string')
        .str.pad(width=12, side='left', fillchar='0')
    )
    ay_df.drop(columns='School NCES ID INT', inplace=True)

    # ── NCES enrichment ────────────────────────────────────────────────────────
    ay_df = get_locale(ay_df)
    ay_df = get_district(ay_df)

    # ── Service totals: fill NaN → 0, then rename to human-readable labels ─────
    for col in [c for c in ay_df.columns if 'Service' in c]:
        ay_df[col] = ay_df[col].fillna(0)

    ay_df.rename(columns={
        'Service 1 Total':  'Tutoring/Homework Assistance',
        'Service 2 Total':  'Mentoring',
        'Service 3 Total':  'Financial Aid Counseling/Advising',
        'Service 4 Total':  'Counseling/Advising',
        'Service 5 Total':  'College Visit',
        'Service 6 Total':  'Job Site Visit/Job Shadowing',
        'Service 7 Total':  'Summer Programs',
        'Service 8 Total':  'Educational Field Trips',
        'Service 9 Total':  'Student Workshops',
        'Service 10 Total': 'Parent/Family Workshops',
        'Service 11 Total': 'Family Counseling/ Advising',
        'Service 12 Total': 'Family College Visit',
        'Service 13 Total': 'Other Family Events',
        'Algebra 1- Grade of Completion': 'Algebra 1 Status',
    }, inplace=True)

    ay_df = map_codes_to_strings(ay_df)
    ay_df['Grade Level'] = ay_df['Grade Level'].astype('string')

    # ── Service aggregation and college visits ─────────────────────────────────
    aggregated_services, student_service_duration_by_month = create_service_aggregation(service_df)
    college_visits = create_college_visits_df(ay_df)

    print('- Data load complete!')
    print_data_overview(ay_df, student_service_duration_by_month)

    return {
        'ay_df':                          ay_df,
        'agg_services_df':                aggregated_services,
        'duration_by_student_month_type': student_service_duration_by_month,
        'college_visits':                 college_visits,
    }