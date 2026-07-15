"""
Charts for the Objectives Year-to-Year page.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.graph_objects import Figure

from constants import Colors
from charts.common import safe_chart, get_empty_figure


def get_benchmark_line(
    years: list, benchmark: float, increase: float,
    benchmark_year: str, offset=None
) -> go.Scatter:
    """
    Create a benchmark line trace that extends from benchmark_year
    with a given yearly increase.

    Parameters
    ----------
    years : list
        All available academic years.
    benchmark : float
        Starting benchmark value.
    increase : float
        Yearly increase/decrease.
    benchmark_year : str
        Year where benchmark starts (e.g., '2020-2021').
    offset : str or None
        Offset group for positioning.

    Returns
    -------
    go.Scatter
    """
    benchmark_df = pd.DataFrame({'Year': years})
    benchmark_df['Benchmark'] = np.nan
    benchmark_df = benchmark_df.set_index('Year')

    if benchmark_year in benchmark_df.index:
        benchmark_df.loc[benchmark_year, 'Benchmark'] = benchmark

    # Extend forward and backward
    for direction in [1, -1]:
        running_val = benchmark
        running_year = benchmark_year
        while True:
            parts = running_year.split('-')
            new_start = int(parts[0]) + direction
            new_end = int(parts[1]) + direction
            running_year = f'{new_start}-{new_end}'
            if running_year in benchmark_df.index:
                running_val += increase * direction
                benchmark_df.loc[running_year, 'Benchmark'] = running_val
            else:
                break

    benchmark_df = benchmark_df.reset_index()
    benchmark_df = benchmark_df.dropna(subset=['Benchmark'])

    return go.Scatter(
        x=benchmark_df['Year'], y=benchmark_df['Benchmark'],
        mode='lines+markers', zorder=2, name='Benchmark',
        line_dash='dash', line_color=Colors.BENCHMARK,
        offsetgroup=offset,
    )


@safe_chart("No GPA data available")
def get_yty_gpa(
    ay: pd.DataFrame, years: list, gpa_type: str,
    benchmark_val, increase_val, benchmark_year
) -> Figure:
    """Dual-axis chart: GPA data availability stacked bars + average GPA + benchmark."""
    gpa_df = ay[['High School AY', gpa_type]].copy()
    gpa_df['Availability'] = np.where(
        (gpa_df[gpa_type].isna()) | (gpa_df[gpa_type] > 6), 'Missing', 'Available'
    )

    # Availability percentages
    avail = gpa_df.groupby(['High School AY', 'Availability']).size().to_frame('Count').reset_index()
    avail['Percent'] = avail.groupby('High School AY')['Count'].transform(
        lambda x: round(x / x.sum() * 100, 1)
    )
    avail_pivot = avail.pivot(index='High School AY', columns='Availability', values='Percent').reset_index().fillna(0)

    # Average GPA
    avg = (
        gpa_df[gpa_df['Availability'] == 'Available']
        .groupby('High School AY')[gpa_type]
        .mean()
        .to_frame('Average GPA')
        .reset_index()
    )
    avg['Average GPA'] = avg['Average GPA'].round(2)

    combined = avail_pivot.merge(avg, on='High School AY', how='left').fillna(0)

    fig = make_subplots(specs=[[{'secondary_y': True}]])

    # Availability bars (secondary y-axis)
    for col, color in [('Available', Colors.TERTIARY), ('Missing', Colors.LIGHT_GREY)]:
        if col in combined.columns:
            fig.add_trace(
                go.Bar(
                    x=combined['High School AY'], y=combined[col],
                    name=col, text=combined[col].apply(lambda v: f'{v}%'),
                    marker_color=color,
                ),
                secondary_y=True,
            )

    # Average GPA bars (primary y-axis)
    fig.add_trace(
        go.Bar(
            x=combined['High School AY'], y=combined['Average GPA'],
            name='Average GPA', offsetgroup=1,
            text=combined['Average GPA'],
            marker_color=Colors.PRIMARY,
        ),
        secondary_y=False,
    )

    fig.update_layout(barmode='stack', title=f'GPA Missingness and Average by Year ({gpa_type})')
    fig.update_yaxes(showticklabels=False, showgrid=False, secondary_y=True)
    fig.update_yaxes(title_text='Average GPA', range=[0, 4], secondary_y=False)

    # Benchmark line
    if benchmark_val and increase_val is not None and benchmark_year:
        line = get_benchmark_line(years, benchmark_val, increase_val, benchmark_year, '1')
        fig.add_trace(line)
        fig.update_layout(scattermode='group')

    return fig


@safe_chart("No FAFSA data available")
def get_yty_fafsa(
    ay: pd.DataFrame, years: list,
    benchmark_val, increase_val, benchmark_year
) -> Figure:
    """Stacked bar chart of FAFSA completion by year with optional benchmark."""
    fafsa_df = ay[ay['Grade Level'].isin(['12'])][['High School AY', 'FAFSA status code']]

    if len(fafsa_df) == 0:
        return get_empty_figure("No seniors in data")

    counts = fafsa_df.groupby(['High School AY', 'FAFSA status code']).size().to_frame('Count').reset_index()
    counts['Percent'] = counts.groupby('High School AY')['Count'].transform(
        lambda x: round(x / x.sum() * 100, 1)
    )
    counts.sort_values('High School AY', inplace=True)

    fig = px.bar(
        counts, x='High School AY', y='Percent', color='FAFSA status code',
        barmode='stack', text_auto=True, title='FAFSA Completion by Year (Seniors Only)',
        category_orders={'FAFSA status code': ['FAFSA Completed', 'FAFSA Not Completed', 'Not Collected', 'N/A']},
        color_discrete_map={
            'N/A': Colors.LIGHT_GREY,
            'Not Collected': Colors.LIGHT_GREY,
            'FAFSA Not Completed': Colors.SECONDARY,
            'FAFSA Completed': Colors.PRIMARY
        },
    ).update_traces(texttemplate='%{y}%').update_layout(legend_title_text=None)

    if benchmark_val and increase_val is not None and benchmark_year:
        fig.add_trace(get_benchmark_line(years, benchmark_val, increase_val, benchmark_year, None))

    return fig


@safe_chart("No graduation data available")
def get_yty_graduation(
    ay: pd.DataFrame, years: list,
    benchmark_val, increase_val, benchmark_year
) -> Figure:
    """Stacked bar chart of graduation status by year with optional benchmark."""
    grad_df = ay[ay['Grade Level'].isin(['12'])][['High School AY', 'HS Grad Status code']]

    if len(grad_df) == 0:
        return get_empty_figure("No seniors in data")

    counts = grad_df.groupby(['High School AY', 'HS Grad Status code']).size().to_frame('Count').reset_index()
    counts['Percent'] = counts.groupby('High School AY')['Count'].transform(
        lambda x: round(x / x.sum() * 100, 1)
    )

    fig = px.bar(
        counts, x='High School AY', y='Percent', color='HS Grad Status code',
        barmode='stack', text_auto=True, title='Graduation Status by Year (Seniors Only)',
        category_orders={'HS Grad Status code': ['Graduated', 'Did Not Graduate', 'Graduation Status Unknown', 'N/A']},
        color_discrete_map={
            'Graduated': Colors.PRIMARY,
            'Did Not Graduate': Colors.SECONDARY, 
            'Graduation Status Unknown': Colors.LIGHT_GREY, 
            'N/A': Colors.LIGHT_GREY
        },
    ).update_traces(texttemplate='%{y}%').update_layout(legend_title_text=None)

    if benchmark_val and increase_val is not None and benchmark_year:
        fig.add_trace(get_benchmark_line(years, benchmark_val, increase_val, benchmark_year, None))

    return fig


@safe_chart("No PSE data available")
def get_yty_pse(
    ay: pd.DataFrame, years: list,
    benchmark_val, increase_val, benchmark_year
) -> Figure:
    """Stacked bar chart of post-secondary enrollment by year with optional benchmark."""
    pse_df = ay[
        (ay['Grade Level'].isin(['12'])) & (ay['HS Grad Status code'] == 'Graduated')
    ][['High School AY', 'First College Attended Name']].copy()

    if len(pse_df) == 0:
        return get_empty_figure("No graduated seniors in data")

    pse_df['PSE Status'] = np.where(
        (pse_df['First College Attended Name'].isna()) | (pse_df['First College Attended Name'].str.lower() == 'not found'),
        'Did Not Enroll', 'Enrolled'
    )

    counts = pse_df.groupby(['High School AY', 'PSE Status']).size().to_frame('Count').reset_index()
    counts['Percent'] = counts.groupby('High School AY')['Count'].transform(
        lambda x: round(x / x.sum() * 100, 1)
    )

    fig = px.bar(
        counts, x='High School AY', y='Percent', color='PSE Status',
        barmode='stack', text_auto=True, title='Post-Secondary Enrollment by Year (Graduates Only)',
        category_orders={'PSE Status': ['Enrolled', 'Did Not Enroll']},
        color_discrete_map={
            'Enrolled': Colors.PRIMARY,
            'Did Not Enroll': Colors.SECONDARY, 
        },
    ).update_traces(texttemplate='%{y}%').update_layout(legend_title_text=None)

    if benchmark_val and increase_val is not None and benchmark_year:
        fig.add_trace(get_benchmark_line(years, benchmark_val, increase_val, benchmark_year, None))

    return fig

@safe_chart("No Algebra 1 data available")
def get_yty_alg_1(
    ay: pd.DataFrame, years: list,
    benchmark_val, increase_val, benchmark_year
) -> Figure:
    alg_1_df = ay[ay['Grade Level'] == '9']

    if len(alg_1_df) == 0:
        return get_empty_figure("No 9th graders in data")
    
    counts = alg_1_df.groupby(['High School AY', 'Algebra 1 Status']).size().to_frame('Count').reset_index()
    counts['Percent'] = counts.groupby('High School AY')['Count'].transform(
        lambda x: round(x / x.sum() * 100, 1)
    )

    fig = px.bar(
        counts, x='High School AY', y='Percent', color='Algebra 1 Status',
        barmode='stack', text_auto=True, title='Algebra 1 Status (9th Graders Only)',
        category_orders={'Algebra 1 Status': ['Enrolled and Completed', 'Enrolled But Not Completed', 'Not Enrolled or Data Unavailable', 'N/A']},
        color_discrete_map={
            'Enrolled and Completed': Colors.PRIMARY,
            'Enrolled But Not Completed': Colors.SECONDARY,
            'Not Enrolled or Data Unavailable': Colors.TERTIARY,
            'N/A': Colors.LIGHT_GREY
        },
    ).update_traces(texttemplate='%{y}%').update_layout(legend_title_text=None)

    if benchmark_val and increase_val is not None and benchmark_year:
        fig.add_trace(get_benchmark_line(years, benchmark_val, increase_val, benchmark_year, None))

    return fig