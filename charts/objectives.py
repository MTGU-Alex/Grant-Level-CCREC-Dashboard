"""
Charts for the Objectives page (GPA, FAFSA, Sankey).
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from plotly.graph_objects import Figure

from constants import Colors, CHART_COLORWAY, SANKEY_LEVEL_OPTIONS, SERVICE_COLUMNS
from charts.common import safe_chart, sort_by_grade, get_empty_figure


@safe_chart("No GPA data available")
def get_gpa_by_grade(
    ay: pd.DataFrame, gpa_type: str,
    gpa_low: float, gpa_high: float, gpa_benchmark: float
) -> Figure:
    """
    Dual-axis chart: stacked % bars for GPA bands + average GPA bars with benchmark line.
    """
    gpas = ay[['Grade Level', gpa_type]].copy()
    gpas = gpas[~gpas['Grade Level'].isin(['7', '8', '13'])]

    if len(gpas) == 0:
        return get_empty_figure("No GPA data for current filters")

    gpas[gpa_type] = gpas[gpa_type].fillna(9.99)

    # Categorize into bands
    conditions = [
        gpas[gpa_type] <= gpa_low,
        (gpas[gpa_type] > gpa_low) & (gpas[gpa_type] < gpa_high),
        (gpas[gpa_type] >= gpa_high) & (gpas[gpa_type] < 9),
    ]
    choices = [
        f'Low: ≤ {gpa_low}',
        f'Medium: {gpa_low} - {gpa_high}',
        f'High: ≥ {gpa_high}',
    ]
    gpas['GPA Range'] = np.select(conditions, choices, default='Unknown')

    # Calculate percentages
    counts = gpas.groupby(['Grade Level', 'GPA Range']).size().to_frame('Count').reset_index()
    counts['Percentage'] = counts.groupby('Grade Level')['Count'].transform(
        lambda x: round(x / x.sum() * 100, 1)
    )
    pivoted = counts.pivot(index='Grade Level', columns='GPA Range', values='Percentage').reset_index().fillna(0)

    # Average GPA (excluding unknowns)
    avg_gpa = (
        gpas[gpas[gpa_type] < 9]
        .groupby('Grade Level')[gpa_type]
        .mean()
        .to_frame('Average GPA')
        .reset_index()
    )
    avg_gpa['Average GPA'] = avg_gpa['Average GPA'].round(2)
    pivoted = pivoted.merge(avg_gpa, on='Grade Level', how='left')

    # Build figure
    fig = make_subplots(specs=[[{'secondary_y': True}]])

    stack_cols = [f'Low: ≤ {gpa_low}', f'Medium: {gpa_low} - {gpa_high}', f'High: ≥ {gpa_high}', 'Unknown']
    band_colors = [Colors.SECONDARY, Colors.GOLD, Colors.TERTIARY, Colors.LIGHT_GREY]

    for col, color in zip(stack_cols, band_colors):
        if col not in pivoted.columns:
            continue
        fig.add_trace(
            go.Bar(
                x=pivoted['Grade Level'], y=pivoted[col],
                offsetgroup=0, name=col,
                text=pivoted[col].apply(lambda v: f'{v}%' if v > 0 else ''),
                marker_color=color,
            ),
            secondary_y=False,
        )

    if 'Average GPA' in pivoted.columns:
        fig.add_trace(
            go.Bar(
                x=pivoted['Grade Level'], y=pivoted['Average GPA'],
                name='Average GPA', offsetgroup=1,
                text=pivoted['Average GPA'],
                marker_color=Colors.PRIMARY,
            ),
            secondary_y=True,
        )

    fig.update_layout(
        barmode='stack',
        title='GPA Ranges and Averages by Grade',
    )
    fig.update_xaxes(
        type='category',
        categoryarray=['9', '10', '11', '12'],
        title='Grade Level',
    )
    fig.update_yaxes(title_text='% of Students', range=[0, 100], showticklabels=False, secondary_y=False)
    fig.update_yaxes(title_text='Average GPA', range=[0, 4], secondary_y=True)
    fig.add_hline(
        y=gpa_benchmark, line_dash="dash", line_width=2,
        line_color=Colors.BENCHMARK, secondary_y=True,
    )

    return fig


@safe_chart("No FAFSA data available")
def get_fafsa(ay: pd.DataFrame):
    """Pie chart of FAFSA completion status for seniors."""
    seniors = ay[ay['Grade Level'].isin(['12'])]

    data = (
        seniors.groupby('FAFSA status code').size()
        .transform(lambda x: round(x / x.sum() * 100, 1))
        .to_frame('Percent')
        .reset_index()
    )
    return px.pie(
        data, names='FAFSA status code', values='Percent',
        title='FAFSA Completion (OnlySeniors)',
    )

@safe_chart('No graduation data available')
def get_graduation(ay: pd.DataFrame) -> Figure:
    seniors = ay[ay['Grade Level'].isin(['12'])] 

    data = (
        seniors.groupby('HS Grad Status code').size()
        .transform(lambda x: round(x / x.sum() * 100, 1))
        .to_frame('Percent')
        .reset_index()
    )
    return px.pie(
        data, names='HS Grad Status code', values='Percent',
        title='High School Graduatiohn Code (Seniors Only)'
    )

@safe_chart('No graduation data available')
def get_pse(ay: pd.DataFrame) -> Figure:
    seniors = ay[ay['Grade Level'].isin(['12'])] 

    seniors['PSE Status'] = np.where(
        (seniors['First College Attended Name'].isna()) | (seniors['First College Attended Name'].str.lower() == 'not found'),
        'Did Not Enroll', 'Enrolled'
    )

    data = (
        seniors.groupby('PSE Status').size()
        .transform(lambda x: round(x / x.sum() * 100, 1))
        .to_frame('Percent')
        .reset_index()
    )
    return px.pie(
        data, names='PSE Status', values='Percent',
        title='Post Seconsary Enrollment (Seniors Only)'
    )

@safe_chart('No Algebra 1 data available')
def get_alg_1(ay: pd.DataFrame) -> Figure:
    alg_df = ay.groupby(['Grade Level', 'Algebra 1 Status']).size().to_frame('Count').reset_index()
    alg_df['Percentage'] = alg_df.groupby('Grade Level')['Count'].transform(
        lambda x: round(x / x.sum() * 100, 1)
    )

    return px.bar(alg_df,
        x='Grade Level',
        y='Percentage',
        color='Algebra 1 Status',
        barmode='stack',
        title='Algebra 1 Status',
        text_auto=True
    ).update_traces(texttemplate='%{y}%')

def _get_next_sankey_level(level: str) -> list:
    """Get available options for the next sankey level."""
    return SANKEY_LEVEL_OPTIONS.get(level, [])


def get_sankey(
    ay: pd.DataFrame,
    l1_selection: str, l2_selection: str,
    l3_selection: str, l4_selection: str,
    gpa_type: str, gpa_low: float, gpa_high: float
) -> tuple:
    """
    Build a dynamic multi-level Sankey diagram for student outcome pathways.

    Returns
    -------
    tuple
        (l1_options, l1_selection, l2_options, l2_selection,
         l3_options, l3_selection, l4_options, l4_selection, figure)
    """
    # Level 1 setup
    l1_options = ['GPA', 'District', 'Grade Level', 'Service Participation Level', 'HS Grad Status code', 'Post Secondary Enrollment', 'Post Secondary Graduation']
    if not l1_selection:
        l1_selection = 'GPA'

    # Cascade level options
    options_dict = {
        'l1_selection': l1_selection,
        'l2_selection': l2_selection,
        'l3_selection': l3_selection,
        'l4_selection': l4_selection,
    }

    level_counter = 2
    for option_key in ['l1_selection', 'l2_selection', 'l3_selection']:
        option = options_dict[option_key]
        next_options = _get_next_sankey_level(option) if option else []
        if level_counter > 2:
            next_options = ['None'] + next_options
        options_dict[f'l{level_counter}_options'] = next_options

        current_sel = options_dict.get(f'l{level_counter}_selection')
        if not next_options:
            options_dict[f'l{level_counter}_selection'] = 'None'
        elif current_sel not in next_options:
            options_dict[f'l{level_counter}_selection'] = next_options[0]
        level_counter += 1

    # Build selection list (excluding 'None')
    selection_list = [
        x for x in [
            options_dict['l1_selection'],
            options_dict['l2_selection'],
            options_dict['l3_selection'],
            options_dict['l4_selection'],
        ]
        if x and x != 'None'
    ]

    if len(selection_list) < 2:
        empty_fig = get_empty_figure("Select at least 2 levels for Sankey diagram")
        return (
            l1_options, l1_selection,
            options_dict.get('l2_options', []), options_dict['l2_selection'],
            options_dict.get('l3_options', []), options_dict['l3_selection'],
            options_dict.get('l4_options', []), options_dict['l4_selection'],
            empty_fig,
        )

    # Compute derived columns
    ay = ay.copy()
    ay['Post Secondary Enrollment'] = np.where(
        (ay['First College Attended Name'].isna()) | (ay['First College Attended Name'].str.lower() == 'not found'),
        'Did Not Enroll', 'Enrolled'
    )

    ay['Post Secondary Graduation'] = np.where(
        (ay['Graduated Y/N'].isna()) | (ay['Graduated Y/N'].str.lower() == 'n'),
        'Has Not Graduated', 'Graduated'
    )

    ay[gpa_type] = ay[gpa_type].fillna(9.99)
    conditions = [
        ay[gpa_type] <= gpa_low,
        (ay[gpa_type] > gpa_low) & (ay[gpa_type] < gpa_high),
        (ay[gpa_type] >= gpa_high) & (ay[gpa_type] < 9),
    ]
    choices = [
        f'Low: ≤ {gpa_low}',
        f'Medium: {gpa_low} - {gpa_high}',
        f'High: ≥ {gpa_high}',
    ]
    ay['GPA'] = np.select(conditions, choices, default='Unknown')

    ay['Service Hours'] = ay[SERVICE_COLUMNS].sum(axis=1) / 60
    conditions = [
        ay['Service Hours'] == 0,
        (ay['Service Hours'] > 0) & (ay['Service Hours'] <= 1),
        (ay['Service Hours'] > 1) & (ay['Service Hours'] <= 10),
        ay['Service Hours'] > 10,
    ]
    choices = [
        'No Participation',
        f'Low Participation (≤ 1 hour)',
        f'Medium Participation (1 - 10 hours)',
        f'High Participation (> 10 hours)',
    ]
    ay['Service Participation Level'] = np.select(conditions, choices, default='Unknown')

    return_message = None
    if 'GPA' in selection_list:
        return_message = '• Only grades 9-12 represented in sankey with the current levels.'
        ay = ay[ay['Grade Level'].isin(['9', '10', '11', '12'])]
    if 'FAFSA status code' in selection_list or 'HS Grad Status code' in selection_list or 'Post Secondary Enrollment' in selection_list or 'Post Secondary Graduation' in selection_list:
        return_message = '• Only 12th graders represented in sankey with the current levels.'
        ay = ay[ay['Grade Level'].isin(['12'])]

    # Build node list and metadata
    node_list = []
    node_level_map = {}
    sankey_meta = {}
    node_index = 0

    for level_num, col_name in enumerate(selection_list, start=1):
        sankey_meta[level_num] = {'column': col_name, 'values': {}}
        for val in ay[col_name].dropna().unique():
            node_level_map[node_index] = level_num
            node_list.append(val)
            sankey_meta[level_num]['values'][val] = node_index
            node_index += 1

    # X positions and colors
    num_levels = len(sankey_meta)
    x_step = 1 / max(num_levels - 1, 1)
    x_splits = [round(i * x_step, 2) for i in range(num_levels)]

    x_locations = []
    colors = []
    for level_idx, x_pos in enumerate(x_splits):
        level_num = level_idx + 1
        for _ in sankey_meta[level_num]['values']:
            x_locations.append(x_pos)
            colors.append(CHART_COLORWAY[level_idx % len(CHART_COLORWAY)])

    # Build links
    source_list, target_list, value_list = [], [], []
    for i in range(1, num_levels):
        src_col = sankey_meta[i]['column']
        tgt_col = sankey_meta[i + 1]['column']
        for src_val, src_idx in sankey_meta[i]['values'].items():
            for tgt_val, tgt_idx in sankey_meta[i + 1]['values'].items():
                count = len(ay[(ay[src_col] == src_val) & (ay[tgt_col] == tgt_val)])
                source_list.append(src_idx)
                target_list.append(tgt_idx)
                value_list.append(count)

    # Calculate node percentages
    links_df = pd.DataFrame({'Source': source_list, 'Target': target_list, 'Value': value_list})
    out_counts = links_df.groupby('Source')['Value'].sum().to_frame('Out').reset_index().rename(columns={'Source': 'Node'})
    in_counts = links_df.groupby('Target')['Value'].sum().to_frame('In').reset_index().rename(columns={'Target': 'Node'})
    node_counts = out_counts.merge(in_counts, how='outer', on='Node').fillna(0)
    node_counts['Val'] = node_counts[['Out', 'In']].max(axis=1)
    node_counts['Level'] = node_counts['Node'].map(node_level_map)
    node_counts['Percent'] = node_counts.groupby('Level')['Val'].transform(
        lambda x: round(x / x.sum() * 100, 1)
    )
    node_counts = node_counts.set_index('Node')

    # Node labels with percentages
    node_labels_with_pct = []
    for i in range(len(node_list)):
        level = node_level_map[i]
        col = sankey_meta[level]['column']
        pct = node_counts.loc[i, 'Percent'] if i in node_counts.index else 0
        node_labels_with_pct.append(f'{col}: {node_list[i]} - {pct}%')

    # Link hover text
    link_hover = []
    for i in range(len(source_list)):
        src_idx = source_list[i]
        tgt_idx = target_list[i]
        val = value_list[i]
        src_col = sankey_meta[node_level_map[src_idx]]['column']
        tgt_col = sankey_meta[node_level_map[tgt_idx]]['column']
        src_total = node_counts.loc[src_idx, 'Val'] if src_idx in node_counts.index else 1
        tgt_total = node_counts.loc[tgt_idx, 'Val'] if tgt_idx in node_counts.index else 1
        pct_src = round((val / src_total) * 100, 1) if src_total > 0 else 0
        pct_tgt = round((val / tgt_total) * 100, 1) if tgt_total > 0 else 0
        text = (
            f'{val} students: {src_col}="{node_list[src_idx]}" → {tgt_col}="{node_list[tgt_idx]}"<br>'
            f'{pct_src}% of "{node_list[src_idx]}" | {pct_tgt}% of "{node_list[tgt_idx]}"'
        )
        link_hover.append(text)

    # Create Sankey figure
    fig = go.Figure(data=[go.Sankey(
        arrangement='fixed',
        node=dict(
            pad=5, thickness=40,
            line=dict(color=Colors.DARK_GREY, width=0.5),
            label=node_list,
            customdata=node_labels_with_pct,
            hovertemplate='%{customdata}<extra></extra>',
            x=x_locations,
            color=colors,
        ),
        link=dict(
            source=source_list, target=target_list, value=value_list,
            customdata=link_hover,
            hovertemplate='%{customdata}<extra></extra>',
        ),
    )])

    # Level title annotations
    label_x_map = {0: -0.02, 0.33: 0.3, 0.5: 0.5, 0.67: 0.71, 1: 1.02}
    for i, x_pos in enumerate(x_splits):
        closest_x = min(label_x_map.keys(), key=lambda k: abs(k - x_pos))
        fig.add_annotation(
            x=label_x_map[closest_x], y=1.06,
            text=f"<b>{selection_list[i]}</b>",
            showarrow=False, font=dict(size=12),
        )


    return (
        l1_options, l1_selection,
        options_dict.get('l2_options', []), options_dict['l2_selection'],
        options_dict.get('l3_options', []), options_dict['l3_selection'],
        options_dict.get('l4_options', []), options_dict['l4_selection'],
        fig, return_message
    )