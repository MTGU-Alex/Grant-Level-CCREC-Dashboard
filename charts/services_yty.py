"""
Charts for the Services Year-to-Year page.
"""

import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure

from constants import SERVICE_COLUMNS, MONTH_MAP, FISCAL_MONTH_ORDER
from charts.common import safe_chart


@safe_chart("No service time data available")
def get_yty_service_time_by_type(ay: pd.DataFrame) -> Figure:
    """Stacked bar chart: percentage of service time by type across years."""
    available_cols = [c for c in SERVICE_COLUMNS if c in ay.columns]
    data = ay.groupby('High School AY')[available_cols].sum().reset_index()
    data['Total'] = data[available_cols].sum(axis=1)

    pct_cols = []
    for col in available_cols:
        pct_col = f'{col} %'
        data[pct_col] = round((data[col] / data['Total']) * 100, 2)
        pct_cols.append(pct_col)

    melted = data.melt(
        id_vars='High School AY',
        value_vars=pct_cols,
        var_name='Service Type',
        value_name='Percent',
    )

    # Order by total percentage
    type_totals = melted.groupby('Service Type')['Percent'].sum().sort_values(ascending=False)
    type_order = type_totals.index.tolist()

    return px.bar(
        melted, x='High School AY', y='Percent', color='Service Type',
        category_orders={'Service Type': type_order},
        title='Percentage of Time Spent by Service Category',
    )


@safe_chart("No enrollment data available")
def get_yty_enrollments(ay: pd.DataFrame) -> Figure:
    """Bar chart of enrollment count by year."""
    data = ay.groupby('High School AY').size().to_frame('Students').reset_index()
    return px.bar(
        data, x='High School AY', y='Students',
        labels={'High School AY': 'School Year'},
        text_auto=True, title='Enrollment Count by Year',
    )


@safe_chart("No participation data available")
def get_participation_by_month(
    ay: pd.DataFrame,
    duration_by_student_month_type: pd.DataFrame,
    threshold: float,
    service_types: list,
) -> Figure:
    """Line chart of monthly service participation percentage by year."""
    students_per_year = ay.groupby('High School AY').size().to_frame('Student Count').reset_index()
    months_df = pd.DataFrame({'Month': list(range(1, 13))})
    students_per_month = students_per_year.merge(months_df, how='cross')

    # Filter by service types
    filtered = duration_by_student_month_type[
        duration_by_student_month_type['Service Type Code'].isin(service_types)
    ]
    grouped = (
        filtered
        .groupby(['High School AY', 'Month', 'National CCREC Student ID'])['Total Time']
        .sum()
        .reset_index()
    )
    grouped['Total Time'] = grouped['Total Time'] / 60

    # Apply threshold
    if threshold > 0:
        grouped = grouped[grouped['Total Time'] >= threshold]
    else:
        grouped = grouped[grouped['Total Time'] > 0]

    participation = (
        grouped
        .groupby(['High School AY', 'Month'])['National CCREC Student ID']
        .nunique()
        .reset_index()
        .rename(columns={'National CCREC Student ID': 'Participant Count'})
    )

    merged = participation.merge(
        students_per_month, how='right', on=['High School AY', 'Month']
    ).fillna(0)
    merged['Participation Percent'] = round(
        (merged['Participant Count'] / merged['Student Count']) * 100, 2
    )
    merged['Month'] = merged['Month'].map(MONTH_MAP)
    merged['Month'] = pd.Categorical(merged['Month'], categories=FISCAL_MONTH_ORDER, ordered=True)
    merged.sort_values('Month', inplace=True)

    return px.line(
        merged, x='Month', y='Participation Percent', color='High School AY',
        markers=True, title='Service Participation Percentage by Month',
        category_orders={'High School AY': sorted(merged['High School AY'].drop_duplicates().to_list())},
    )


@safe_chart("No service data available")
def get_hours_per_student_by_month(
    ay: pd.DataFrame,
    duration_by_student_month_type: pd.DataFrame,
    service_types: list,
) -> Figure:
    """Line chart of average service hours per enrolled student by month."""
    students_per_year = ay.groupby('High School AY').size().to_frame('Student Count').reset_index()
    months_df = pd.DataFrame({'Month': list(range(1, 13))})
    students_per_month = students_per_year.merge(months_df, how='cross')

    filtered = duration_by_student_month_type[
        duration_by_student_month_type['Service Type Code'].isin(service_types)
    ]
    total_mins = (
        filtered
        .groupby(['High School AY', 'Month'])['Total Time']
        .sum()
        .reset_index()
        .rename(columns={'Total Time': 'Total Minutes'})
    )

    merged = total_mins.merge(
        students_per_month, how='right', on=['High School AY', 'Month']
    ).fillna(0)
    merged['Hours per Student'] = round(
        (merged['Total Minutes'] / merged['Student Count']) / 60, 2
    )
    merged['Month'] = merged['Month'].map(MONTH_MAP)
    merged['Month'] = pd.Categorical(merged['Month'], categories=FISCAL_MONTH_ORDER, ordered=True)
    merged.sort_values('Month', inplace=True)

    return px.line(
        merged, x='Month', y='Hours per Student', color='High School AY',
        markers=True, title='Average Service Hours per Student by Month',
        category_orders={'High School AY': sorted(merged['High School AY'].drop_duplicates().to_list())}
    )