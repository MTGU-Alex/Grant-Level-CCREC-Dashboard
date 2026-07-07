"""
Charts for the Services page.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.graph_objects import Figure

from constants import SERVICE_COLUMNS, Colors
from charts.common import safe_chart, sort_by_grade


@safe_chart("No service data available")
def get_participation_and_avg_time(ay: pd.DataFrame) -> Figure:
    """
    Butterfly/tornado chart showing participation % (left) and
    average hours spent (right) per service type.
    """
    rows = []
    for col in SERVICE_COLUMNS:
        if col not in ay.columns:
            continue
        num_non_zero = (ay[col] != 0).sum()
        total_len = len(ay)
        participation = round((num_non_zero / total_len) * 100, 2) if num_non_zero > 0 else 0
        avg_hours = round(ay[ay[col] != 0][col].mean() / 60, 2) if num_non_zero > 0 else 0
        rows.append({'Service Type': col, 'Participation': participation, 'Average Hours': avg_hours})

    service_df = pd.DataFrame(rows).sort_values('Participation')

    fig = make_subplots(
        subplot_titles=('Service Participation %', '', 'Average Hours Spent'),
        rows=1, cols=3,
        shared_yaxes=True,
        column_widths=[0.45, 0.125, 0.45],
        horizontal_spacing=0,
    )

    # Left bars (participation - negative for butterfly effect)
    fig.add_trace(
        go.Bar(
            y=service_df['Service Type'],
            x=-service_df['Participation'],
            text=service_df['Participation'].astype(str) + '%',
            hovertemplate="%{y}: %{text}<extra></extra>",
            orientation='h',
            showlegend=False,
            marker_color=Colors.PRIMARY,
        ),
        row=1, col=1,
    )

    # Middle (invisible spacer for labels)
    fig.add_trace(
        go.Bar(
            y=service_df['Service Type'],
            x=[0] * len(service_df),
            orientation='h',
            marker_color='white',
            hoverinfo='skip',
            showlegend=False,
        ),
        row=1, col=2,
    )

    # Right bars (average hours)
    fig.add_trace(
        go.Bar(
            y=service_df['Service Type'],
            x=service_df['Average Hours'],
            text=service_df['Average Hours'],
            orientation='h',
            showlegend=False,
            marker_color=Colors.SECONDARY,
        ),
        row=1, col=3,
    )

    # Center labels
    for label in service_df['Service Type']:
        fig.add_annotation(
            x=0.5, y=label,
            text=label,
            showarrow=False,
            xref="x2 domain", yref="y2",
            font=dict(size=12, color=Colors.BLACK, weight="bold"),
            align="center",
        )

    fig.update_yaxes(showticklabels=False)
    fig.update_xaxes(visible=False, row=1, col=2)
    fig.update_layout(
        barmode="overlay",
        margin=dict(l=20, r=20, t=40, b=20),
    )

    # Fix left axis tick labels
    max_val = service_df['Participation'].max()
    if isinstance(max_val, (int, float, np.floating)) and max_val > 0:
        next_10 = int(max_val // 10 + 1)
        ticks = [-num * 10 for num in range(1, next_10 + 1)]
        fig.update_xaxes(
            tickvals=ticks,
            ticktext=[abs(v) for v in ticks],
            row=1, col=1,
        )

    return fig


@safe_chart("No participation data available")
def get_participation_by_grade(
    ay: pd.DataFrame, threshold: float, service_types: list
) -> Figure:
    """
    Grouped bar chart: enrollment vs. service participants per grade.
    Threshold determines minimum hours to count as participating.
    """
    available_types = [t for t in service_types if t in ay.columns]
    ay = ay.copy()
    ay['Filtered Service Time'] = ay[available_types].sum(axis=1) / 60

    students_per_grade = ay.groupby('Grade Level').size().to_frame('Students').reset_index()

    if threshold == 0:
        participants = ay[ay['Filtered Service Time'] > 0]
    else:
        participants = ay[ay['Filtered Service Time'] >= threshold]

    participant_count = participants.groupby('Grade Level').size().to_frame('Students').reset_index()

    students_per_grade['Group'] = 'Enrollment Count'
    participant_count['Group'] = 'Service Participants'

    combined = pd.concat([students_per_grade, participant_count])
    combined['Grade Level'] = combined['Grade Level'].astype(str)
    combined = sort_by_grade(combined)

    return px.bar(
        combined, x='Grade Level', y='Students', color='Group', custom_data='Group',
        barmode='group', text_auto=True,
        title='Service Participation by Grade',
    ).update_layout(
        legend_title_text="",
        legend=dict(
            yanchor='top',
            y=1.15,
            x=.7
        ),
        margin=dict(r=0)
    ).update_traces(
        hovertemplate='<br>'.join([
            '<b>Grade Level:</b> %{x}',
            '<b>Students:</b> %{y}',
            '<b>Bar:</b> %{customdata}',
            '<extra></extra>'
        ])
    )


@safe_chart("No service time data available")
def get_service_time_by_grade(ay: pd.DataFrame, service_types: list) -> Figure:
    """Bar chart of average service time per student by grade."""
    available_types = [t for t in service_types if t in ay.columns]
    ay = ay.copy()
    ay['Total Service Time'] = ay[available_types].sum(axis=1)/60
    data = (
        ay.groupby('Grade Level')['Total Service Time']
        .mean()
        .to_frame('Average Service Time')
        .reset_index()
    )
    data = sort_by_grade(data)
    data['Average Service Time'] = data['Average Service Time'].round(2)

    return px.bar(
        data, x='Grade Level', y='Average Service Time',
        text=data['Average Service Time'],
        title='Average Service Time per Student by Grade (Hours)',
    ).update_xaxes(type='category')