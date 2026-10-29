"""
Data access layer for the CCREC Dashboard.
Provides filtered data access and computed statistics.
"""
import base64
import io
import pandas as pd
import numpy as np
from typing import Optional
from tabulate import tabulate
from constants import SERVICE_COLUMNS, UNKNOWN_NCES_ID, AY_COLUMNS_TO_KEEP, SERVICE_COLUMN_RENAME, CODE_MAPPINGS, SERVICE_CODE_TO_TYPE

def _map_codes_to_strings(ay_df: pd.DataFrame) -> pd.DataFrame:
    """Map numeric codes to human-readable strings."""
    for col, mapping in CODE_MAPPINGS.items():
        if col in ay_df.columns:
            ay_df[col] = ay_df[col].map(mapping).fillna(ay_df[col])
    return ay_df

def _get_school_groups(ay_df: pd.DataFrame) -> dict:
    '''Looks at ay_df and returns dict of any school groupings/renames.'''
    rename_counts_by_school = ay_df.groupby(['Secondary School Name', 'School Group Name'], dropna=False).size().reset_index().rename(columns={0: 'Row Count'})
    rename_counts_by_school.sort_values(by=['Secondary School Name', 'Row Count'], inplace=True, ascending=[True, False])
    rename_counts_by_school.drop_duplicates(subset='Secondary School Name', keep='first', inplace=True)
    rename_counts_by_school.dropna(subset='School Group Name', inplace=True)
    rename_dict = rename_counts_by_school.set_index('Secondary School Name')['School Group Name'].to_dict()
    return rename_dict

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

def _load_ay(ay_df: pd.DataFrame):
    
    # Select and rename columns
    available_columns = [c for c in AY_COLUMNS_TO_KEEP if c in ay_df.columns]
    ay_df = ay_df[available_columns].copy()
    ay_df.rename(columns={'School NCES ID': 'School NCES ID INT'}, inplace=True)
    ay_df['School NCES ID'] = ay_df['School NCES ID INT'].astype('string').str.pad(
        width=12, side='left', fillchar='0'
    )
    ay_df.drop(columns='School NCES ID INT', inplace=True)

    # fill NaN service columns and rename
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
    return ay_df, college_visits

def _create_service_aggregation(service_df: pd.DataFrame) -> tuple:
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

class DashboardData:
    """
    Encapsulates all dashboard data with filtering and query capabilities.
    
    Parameters
    ----------
    ay_df : pd.DataFrame
        Academic year student-level data.
    agg_services_df : pd.DataFrame
        Aggregated service data by year/month/type.
    duration_by_student_month_type : pd.DataFrame
        Student-level service durations by month and type.
    college_visits : pd.DataFrame
        College visit IPEDS data per student.
    """

    @property
    def years(self) -> list:
        """Get sorted list of all academic years in the data."""
        return sorted(self._ay_df['High School AY'].unique().tolist())

    @property
    def districts(self) -> list:
        """Get sorted list of all districts."""
        return sorted(self._ay_df['District'].dropna().unique().tolist())

    def load_upload(
        self, file_name: str, file_contents: str, file_type: str
    ):
        file_good = True
        return_message = ''

        if file_name[-3:] != 'csv':
                file_good = False
                return_message += f'{file_type} file must be a csv file'
                return file_good, return_message, None, None

        contents_string = file_contents.split(',')[1]
        decoded_contents = base64.b64decode(contents_string)
        df = pd.read_csv(io.StringIO(decoded_contents.decode('utf-8-sig')), low_memory=False)

        str_cols = df.select_dtypes(include="object").columns
        df[str_cols] = df[str_cols].apply(lambda s: s.str.strip())

        if file_type == 'AY':
            processed_ay_df, college_visits = _load_ay(df)
            self._ay_df = processed_ay_df
            self._college_visits = college_visits
        else:
            aggregated_services, student_duration_by_month = _create_service_aggregation(df)
            self._agg_services_df = aggregated_services
            self._duration_by_student_month_type = student_duration_by_month

        return file_good, return_message, None

    def get_years(self):
        years = self._ay_df['High School AY'].drop_duplicates().to_list()
        return sorted(years)[::-1]

    def get_filtered_ay(
        self, filters: dict, year: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Apply demographic filters and optional year filter to AY data.

        Parameters
        ----------
        filters : dict
            Dictionary of column_name: value pairs for filtering.
        year : str, optional
            Academic year to filter to (e.g., '2023-2024').

        Returns
        -------
        pd.DataFrame
            Filtered copy of the AY DataFrame.
        """
        df = self._ay_df.copy()
        for key, val in filters.items():
            if key in df.columns:
                df = df[df[key] == val]
        if year:
            df = df[df['High School AY'] == year]
        return df

    def get_filtered_duration_by_student(
        self, filters: dict
    ) -> pd.DataFrame:
        """
        Get student-level service durations filtered to students matching
        the demographic filters.

        Parameters
        ----------
        filters : dict
            Demographic filters applied to AY data to determine student set.

        Returns
        -------
        pd.DataFrame
            Filtered duration_by_student_month_type DataFrame.
        """
        filtered_ay = self.get_filtered_ay(filters)
        student_ids = filtered_ay['National CCREC Student ID'].unique()
        return self._duration_by_student_month_type[
            self._duration_by_student_month_type['National CCREC Student ID'].isin(student_ids)
        ].copy()

    def get_filtered_agg_services(self, filters: dict) -> pd.DataFrame:
        """
        Get aggregated service data filtered to years/students matching filters.
        
        Note: Since agg_services is pre-aggregated, we can only filter by year
        based on years present in the filtered AY data.

        Parameters
        ----------
        filters : dict
            Demographic filters.

        Returns
        -------
        pd.DataFrame
            Filtered aggregated services DataFrame.
        """
        filtered_ay = self.get_filtered_ay(filters)
        years = filtered_ay['High School AY'].unique()
        return self._agg_services_df[
            self._agg_services_df['High School AY'].isin(years)
        ].copy()

    def get_header_stats(self, filters: dict, year: str, group: str) -> dict:
        """
        Compute header statistics for the filtered dataset.

        Parameters
        ----------
        filters : dict
            Active demographic filters.
        year : str
            Selected academic year.

        Returns
        -------
        dict
            Keys: 'total_hours', 'total_students', 'total_schools'
        """
        df = self.get_filtered_ay(filters, year)
        if group != 'All':
            df = df[df['School Display Name'] == group]
        available_service_cols = [c for c in SERVICE_COLUMNS if c in df.columns]
        total_hours = round(df[available_service_cols].sum().sum() / 60, 2)
        total_students = len(df)
        total_schools = (
            df[df['School NCES ID'] != UNKNOWN_NCES_ID]['School NCES ID']
            .nunique()
        )
        return {
            'total_hours': total_hours,
            'total_students': total_students,
            'total_schools': total_schools,
        }
    
    def group_schools(self, group_dict: dict):
        self._ay_df['School Group Name'] = self._ay_df['Secondary School Name'].map(group_dict)
        self._ay_df['School Display Name'] = self._ay_df['School Group Name'].fillna(self._ay_df['Secondary School Name'])
        self._duration_by_student_month_type['School Group Name'] = self._duration_by_student_month_type['Secondary School Name'].map(group_dict)
        self._duration_by_student_month_type['School Display Name'] = self._duration_by_student_month_type['School Group Name'].fillna(self._duration_by_student_month_type['Secondary School Name'])