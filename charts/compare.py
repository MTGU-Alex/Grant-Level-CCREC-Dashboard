"""
Charts for the Compare page (district vs program comparisons).
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.graph_objects import Figure

from constants import SERVICE_COLUMNS, Colors
from charts.common import safe_chart, get_empty_figure


@safe_chart("No service data available")
def get_service_time_pie(ay: pd.DataFrame, title_text: str) -> Figure:
    """Pie chart of service time distribution by category."""
    available_cols = [c for c in SERVICE_COLUMNS if c in ay.columns]
    data = ay[available_cols].sum().to_frame('Hours').reset_index()
    data.rename(columns={'index': 'Service Category'}, inplace=True)
    total = data['Hours'].sum()

    if total == 0:
        return get_empty_figure("No service hours recorded")

    data['Percent'] = round((data['Hours'] / total) * 100, 1)
    data = data[data['Percent'] > 0]

    return px.pie(data, names='Service Category', values='Percent', title=title_text)


def _get_participation_ranges(
    ay: pd.DataFrame, low: float, high: float
) -> pd.DataFrame:
    """Calculate participation range percentages by grade."""
    available_cols = [c for c in SERVICE_COLUMNS if c in ay.columns]
    ay = ay.copy()
    ay['Service Hours'] = ay[available_cols].sum(axis=1) / 60

    conditions = [
        ay['Service Hours'] == 0,
        (ay['Service Hours'] > 0) & (ay['Service Hours'] <= low),
        (ay['Service Hours'] > low) & (ay['Service Hours'] <= high),
        ay['Service Hours'] > high,
    ]
    choices = [
        'No Participation',
        f'Low: ≤ {low}',
        f'Medium: {low} - {high}',
        f'High: > {high}',
    ]
    ay['Range'] = np.select(conditions, choices, default='Unknown')

    counts = ay.groupby(['Grade Level', 'Range']).size().to_frame('Count').reset_index()
    counts['Percent'] = counts.groupby('Grade Level')['Count'].transform(
        lambda x: round(x / x.sum() * 100, 1)
    )
    return counts.pivot(index='Grade Level', columns='Range', values='Percent').reset_index().fillna(0)


def _get_formatting(groups: int) -> tuple:
    """Get formatting parameters for double-stacked bar chart labels."""
    configs = {
        1: (10, 35, 2, -105),
        2: (5, 9, 9, -50),
        3: (4, 7, 7, -42),
        4: (2, 3, 4, -25),
        5: (2, 3, 4, -25),
    }
    return configs.get(groups, (1, 0, 4, -15))


@safe_chart("No participation data available")
def get_service_participation_compare(
    ay: pd.DataFrame, district_ay: pd.DataFrame,
    low: float, high: float
) -> Figure:
    """Double-stacked bar chart comparing participation ranges: program vs district."""
    program = _get_participation_ranges(ay, low, high)
    district = _get_participation_ranges(district_ay, low, high)

    district_grades = district['Grade Level'].tolist()
    program = program[program['Grade Level'].isin(district_grades)]

    stack_cols = [f'Low: ≤ {low}', f'Medium: {low} - {high}', f'High: > {high}', 'No Participation']
    color_map = {
        f'Low: ≤ {low}': Colors.SECONDARY,
        f'Medium: {low} - {high}': Colors.PRIMARY,
        f'High: > {high}': Colors.TERTIARY,
        'No Participation': Colors.LIGHT_GREY,
    }

    fig = go.Figure()

    for group_idx, df in enumerate([program, district]):
        group_name = 'Program' if group_idx == 0 else 'District'
        for col in stack_cols:
            if col not in df.columns:
                continue
            fig.add_trace(go.Bar(
                x=df['Grade Level'], y=df[col],
                offsetgroup=group_idx, legendgroup=col,
                showlegend=(group_idx == 0),
                marker_color=color_map[col],
                name=col,
                text=df[col].apply(lambda v: f'{v}%' if v > 0 else ''),
                hovertemplate=f'{group_name} | {col}<br>Grade: %{{x}}<br>%{{y}}%<extra></extra>',
            ))

    breaks, nudges, prespaces, standoff = _get_formatting(len(district_grades))

    fig.update_layout(
        barmode='stack',
        title='Service Participation: Program vs District',
        bargroupgap=0.05,
        xaxis=dict(
            tickvals=district_grades,
            ticktext=[
                f'{"&nbsp;" * nudges}{" " * prespaces}{g} - district{"<br>" * breaks}{g} - program'
                for g in district_grades
            ],
            tickangle=45,
            ticklabelstandoff=standoff,
        ),
    )

    return fig


@safe_chart("No GPA data available")
def get_gpa_compare(ay: pd.DataFrame, district_ay: pd.DataFrame, gpa_type: str) -> Figure:
    """Grouped bar chart comparing average GPA by grade: program vs district."""
    def _avg_gpa(df, label):
        gpas = df[['Grade Level', gpa_type]].copy()
        gpas = gpas[~gpas['Grade Level'].isin(['7', '8', '13'])]
        gpas = gpas[(gpas[gpa_type].notna()) & (gpas[gpa_type] != 9.99) & (gpas[gpa_type] != 0)]
        result = gpas.groupby('Grade Level')[gpa_type].mean().to_frame('Average GPA').reset_index()
        result['Average GPA'] = result['Average GPA'].round(2)
        result['Group'] = label
        return result

    combined = pd.concat([_avg_gpa(ay, 'Program'), _avg_gpa(district_ay, 'District')])

    return px.bar(
        combined, x='Grade Level', y='Average GPA', color='Group',
        barmode='group', text_auto=True,
        title=f'Average GPA by Grade ({gpa_type})',
    )


def _get_percent_by_group(df: pd.DataFrame, col: str, label: str) -> pd.DataFrame:
    """Calculate percentage distribution of a column's values."""
    counts = df.groupby(col).size().to_frame('Count').reset_index()
    counts['Percent'] = round(counts['Count'] / counts['Count'].sum() * 100, 1)
    counts['Group'] = label
    return counts


@safe_chart("No FAFSA data available")
def get_fafsa_compare(ay: pd.DataFrame, district_ay: pd.DataFrame) -> Figure:
    """Stacked bar comparing FAFSA status: program vs district."""
    combined = pd.concat([
        _get_percent_by_group(ay, 'FAFSA status code', 'Program'),
        _get_percent_by_group(district_ay, 'FAFSA status code', 'District'),
    ])
    return px.bar(
        combined, x='Group', y='Percent', color='FAFSA status code',
        barmode='stack', text_auto=True, title='FAFSA Completion Comparison',
    ).update_traces(texttemplate='%{y}%')


@safe_chart("No graduation data available")
def get_graduation_compare(ay: pd.DataFrame, district_ay: pd.DataFrame) -> Figure:
    """Stacked bar comparing graduation status: program vs district."""
    combined = pd.concat([
        _get_percent_by_group(ay, 'HS Grad Status code', 'Program'),
        _get_percent_by_group(district_ay, 'HS Grad Status code', 'District'),
    ])
    return px.bar(
        combined, x='Group', y='Percent', color='HS Grad Status code',
        barmode='stack', text_auto=True, title='Graduation Status Comparison',
    ).update_traces(texttemplate='%{y}%')


@safe_chart("No PSE data available")
def get_pse_compare(ay: pd.DataFrame, district_ay: pd.DataFrame) -> Figure:
    """Stacked bar comparing post-secondary enrollment: program vs district."""
    ay = ay.copy()
    district_ay = district_ay.copy()
    ay['PSE'] = np.where(
        (ay['First College Attended Name'].isna()) | (ay['First College Attended Name'].str.lower() == 'not found'),
        'Did Not Enroll', 'Enrolled'
    )
    district_ay['PSE'] = np.where(
        (district_ay['First College Attended Name'].isna()) | (district_ay['First College Attended Name'].str.lower() == 'not found'),
        'Did Not Enroll', 'Enrolled'
    )
    combined = pd.concat([
        _get_percent_by_group(ay, 'PSE', 'Program'),
        _get_percent_by_group(district_ay, 'PSE', 'District'),
    ])
    return px.bar(
        combined, x='Group', y='Percent', color='PSE',
        barmode='stack', text_auto=True, title='Post-Secondary Enrollment Comparison',
    ).update_traces(texttemplate='%{y}%')