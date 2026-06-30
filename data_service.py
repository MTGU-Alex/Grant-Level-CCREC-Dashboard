"""
Data access layer for the CCREC Dashboard.
Provides filtered data access and computed statistics.
"""

import pandas as pd
from typing import Optional
from constants import SERVICE_COLUMNS, UNKNOWN_NCES_ID


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

    def __init__(
        self,
        ay_df: pd.DataFrame,
        agg_services_df: pd.DataFrame,
        duration_by_student_month_type: pd.DataFrame,
        college_visits: pd.DataFrame,
    ):
        self._ay_df = ay_df
        self._agg_services_df = agg_services_df
        self._duration_by_student_month_type = duration_by_student_month_type
        self._college_visits = college_visits

    @property
    def years(self) -> list:
        """Get sorted list of all academic years in the data."""
        return sorted(self._ay_df['High School AY'].unique().tolist())

    @property
    def districts(self) -> list:
        """Get sorted list of all districts."""
        return sorted(self._ay_df['District'].dropna().unique().tolist())

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