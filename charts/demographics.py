"""
Charts for the Demographics page.
"""

import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure

from charts.common import safe_chart, sort_by_grade


@safe_chart("No enrollment data available")
def get_enrollment_by_district(ay: pd.DataFrame) -> Figure:
    """Bar chart of enrollment counts by school/rename."""
    data = (
        ay.groupby('School Display Name').size()
        .to_frame('Student Count')
        .reset_index()
        .sort_values('Student Count')
    )
    return px.bar(
        data, x='School Display Name', y='Student Count',
        text_auto=True, title='Enrollment by School/School Group'
    ).update_xaxes(
        title_text=""
    ).update_layout(
        margin=dict(b=110, r=50)
    )


@safe_chart("No enrollment data available")
def get_enrollment_by_gender(ay: pd.DataFrame) -> Figure:
    """Pie chart of enrollment by gender."""
    data = ay.groupby('Gender Code').size().to_frame('Count').reset_index()
    return px.pie(
        data, names='Gender Code', values='Count',
        title='Enrollment by Gender'
    )


@safe_chart("No enrollment data available")
def get_enrollment_by_ethnicity(ay: pd.DataFrame) -> Figure:
    """Pie chart of enrollment by ethnicity."""
    data = ay.groupby('Ethnicity Code').size().to_frame('Count').reset_index()
    return px.pie(
        data, names='Ethnicity Code', values='Count',
        title='Enrollment by Ethnicity'
    )


@safe_chart("No enrollment data available")
def get_enrollment_by_grade(ay: pd.DataFrame) -> Figure:
    """Bar chart of enrollment by grade level."""
    data = ay.groupby('Grade Level').size().to_frame('Enrollment Count').reset_index()
    data['Grade Level'] = data['Grade Level'].astype(str)
    data = sort_by_grade(data)
    return px.bar(
        data, x='Grade Level', y='Enrollment Count',
        text_auto=True, title='Enrollment by Grade'
    ).update_xaxes(
        type='category'
    )


@safe_chart("No enrollment data available")
def get_enrollment_by_race(ay: pd.DataFrame) -> Figure:
    """Horizontal bar chart of enrollment by race."""
    data = (
        ay.groupby('Race Code').size()
        .to_frame('Enrollment Count')
        .reset_index()
        .sort_values('Enrollment Count')
    )
    return px.bar(
        data, y='Race Code', x='Enrollment Count',
        labels={'Race Code': 'Race'},
        text_auto=True, title='Enrollment by Race'
    ).update_layout(
        margin=dict(l=190),
        yaxis_title=None
    )