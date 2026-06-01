# "charts.py"
"""
charts.py
All Plotly figure-generation functions for the CCREC dashboard.

Design rules enforced here:
  - No function mutates its DataFrame inputs; local copies are used where
    computed columns are needed.
  - no_data_figure() is used wherever data may be absent, so callers
    always receive a go.Figure and never need isinstance checks.
  - SERVICE_TYPES and GRADE_LEVELS_HS are imported from constants to avoid
    duplication with callbacks.py.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

from constants import SERVICE_TYPES, GRADE_LEVELS_HS

# ── Global theme ───────────────────────────────────────────────────────────────

mark_colors = [
    '#0F5C83', '#d75426', '#898E3E', '#EDD9B4',
    '#6B3F20', '#C4882A', '#2A3D4A', '#7f7f7f',
    '#7A8C5E', '#17becf',
]

pio.templates['my_theme'] = dict(
    layout=dict(
        paper_bgcolor='#F5F5F5',
        plot_bgcolor='#EBEBEB',
        font=dict(color='#231F20', family='Segoe UI, Arial, sans-serif'),
        colorway=mark_colors,
    )
)
pio.templates.default = 'my_theme'

# Benchmark line colour — orange stands out against all bar colours
benchmark_line_color = '#d75426'

CCREC_orange     = '#d75426'
CCREC_green      = '#898E3E'
CCREC_blue       = '#0F5C83'
CCREC_black      = '#231F20'
CCREC_dark_grey  = '#4D4D4D'
CCREC_grey       = '#818386'
CCREC_light_grey = '#C8C9CA'

month_map = {
    1: 'Jan', 2: 'Feb',  3: 'Mar',  4: 'Apr',
    5: 'May', 6: 'Jun',  7: 'Jul',  8: 'Aug',
    9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec',
}

# ── Shared utilities ───────────────────────────────────────────────────────────

def no_data_figure(message: str) -> go.Figure:
    """
    Return a blank, styled Plotly figure with a centred annotation.
    Used whenever a chart function has insufficient data to render.
    """
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        x=0.5, y=0.5,
        xref='paper', yref='paper',
        showarrow=False,
        font=dict(size=18, color=CCREC_grey, family='Segoe UI, Arial, sans-serif'),
    )
    fig.update_layout(
        xaxis_visible=False,
        yaxis_visible=False,
        paper_bgcolor='#F5F5F5',
        plot_bgcolor='#F5F5F5',
    )
    return fig


def get_blank_fig() -> go.Figure:
    return px.bar()


# ── Demographics ───────────────────────────────────────────────────────────────

def get_enrollment_by_district(AY: pd.DataFrame) -> go.Figure:
    enrollment = (
        AY.groupby('District').size()
        .to_frame('Student Count').reset_index()
        .sort_values('Student Count')
    )
    return px.bar(
        enrollment, x='District', y='Student Count',
        text_auto=True, title='Enrollment by District',
    ).update_xaxes(title_text='')


def get_enrollment_by_gender(AY: pd.DataFrame) -> go.Figure:
    counts = AY.groupby('Gender Code').size().to_frame('Gender Count').reset_index()
    return px.pie(counts, names='Gender Code', values='Gender Count',
                  title='Enrollment by Gender')


def get_enrollment_by_ethnicity(AY: pd.DataFrame) -> go.Figure:
    counts = AY.groupby('Ethnicity Code').size().to_frame('Ethnicity Count').reset_index()
    return px.pie(counts, names='Ethnicity Code', values='Ethnicity Count',
                  title='Enrollment by Ethnicity')


def get_enrollment_by_grade(AY: pd.DataFrame) -> go.Figure:
    counts = AY.groupby('Grade Level').size().to_frame('Enrollment Count').reset_index()
    counts['Grade Level'] = counts['Grade Level'].astype('str')
    counts.sort_values(
        'Grade Level',
        key=lambda x: x.map({g: int(g) for g in counts['Grade Level'].unique()}),
        inplace=True,
    )
    return px.bar(counts, x='Grade Level', y='Enrollment Count',
                  text_auto=True, title='Enrollment by Grade')


def get_enrollment_by_race(AY: pd.DataFrame) -> go.Figure:
    counts = (
        AY.groupby('Race Code').size()
        .to_frame('Race Count').reset_index()
        .sort_values('Race Count')
    )
    return px.bar(
        counts, y='Race Code', x='Race Count',
        labels={'Race Code': 'Race', 'Race Count': 'Enrollment Count'},
        text_auto=True, title='Enrollment by Race',
    )


# ── Services ───────────────────────────────────────────────────────────────────

def get_participation_and_avg_time(AY: pd.DataFrame) -> go.Figure:
    """
    Butterfly chart: participation rate (left) and average hours (right)
    for each service type.
    """
    # Build summary rows without using locals() trick
    rows: list[dict] = []
    total_len = len(AY)
    for col in SERVICE_TYPES:
        non_zero_mask   = AY[col] != 0
        participation   = round((non_zero_mask.sum() / total_len) * 100, 2) if non_zero_mask.any() else 0.0
        avg_hours       = round(AY.loc[non_zero_mask, col].mean() / 60, 2) if non_zero_mask.any() else 0.0
        rows.append({'Service Type': col, 'Participation': participation, 'Average Hours': avg_hours})

    service_df = pd.DataFrame(rows).sort_values('Participation')

    fig = make_subplots(
        subplot_titles=('Service Participation', '', 'Average Time Spent'),
        rows=1, cols=3,
        shared_yaxes=True,
        column_widths=[0.45, 0.125, 0.45],
        horizontal_spacing=0.02,
    )

    # Left bars — negative x so bars point left
    fig.add_trace(go.Bar(
        y=service_df['Service Type'],
        x=-service_df['Participation'],
        text=np.abs(service_df['Participation']).astype(str) + '%',
        hovertemplate='%{y}: %{text}<extra></extra>',
        orientation='h', showlegend=False,
    ), row=1, col=1)

    # Centre spacer
    fig.add_trace(go.Bar(
        y=service_df['Service Type'],
        x=[0] * len(service_df),
        orientation='h',
        marker_color='white',
        hoverinfo='skip', showlegend=False,
    ), row=1, col=2)

    # Right bars
    fig.add_trace(go.Bar(
        y=service_df['Service Type'],
        x=service_df['Average Hours'],
        text=service_df['Average Hours'],
        orientation='h', showlegend=False,
    ), row=1, col=3)

    # Centre labels — one annotation per service type
    for label in service_df['Service Type']:
        fig.add_annotation(
            x=0.5, y=label,
            text=label, showarrow=False,
            xref='x2 domain', yref='y2',
            font=dict(size=13, color='black', family='Segoe UI, Arial, sans-serif',
                      weight='bold'),
            align='center',
        )

    # Axis / layout tweaks — called ONCE, outside the annotation loop
    fig.update_yaxes(showticklabels=False)
    fig.update_xaxes(visible=False, row=1, col=2)
    fig.update_layout(
        barmode='overlay',
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='#F5F5F5',
        plot_bgcolor='#F5F5F5',
    )

    max_val = service_df['Participation'].max()
    if isinstance(max_val, (float, np.floating)):
        next_10 = int(max_val // 10) + 1
        ticks   = [-n * 10 for n in range(1, next_10 + 1)]
        fig.update_xaxes(
            tickvals=ticks,
            ticktext=[abs(v) for v in ticks],
            row=1, col=1,
        )

    return fig


def get_participation_by_grade(
    AY: pd.DataFrame,
    threshold: float,
    types: list[str],
) -> go.Figure:
    """
    Grouped bar: enrolled students vs. service participants per grade.
    A local Series is used for total service time — AY is not mutated.
    """
    total_time = AY[types].sum(axis=1) / 60   # hours, local Series

    students_per_grade = AY.groupby('Grade Level').size().to_frame('Students').reset_index()

    participating_mask = (total_time != 0) if threshold == 0 else (total_time >= threshold)
    participation_by_grade = (
        AY[participating_mask].groupby('Grade Level').size().to_frame('Students').reset_index()
    )

    students_per_grade['Group']    = 'Enrollment Count'
    participation_by_grade['Group'] = 'Service Participants'
    combined = pd.concat([students_per_grade, participation_by_grade])
    combined['Grade Level'] = combined['Grade Level'].astype('str')
    combined.sort_values(
        'Grade Level',
        key=lambda x: x.map({g: int(g) for g in combined['Grade Level'].unique()}),
        inplace=True,
    )

    return px.bar(
        combined, x='Grade Level', y='Students',
        color='Group', barmode='group',
        text_auto=True, title='Service Participation by Grade',
    )


def get_service_time_by_grade(AY: pd.DataFrame, types: list[str]) -> go.Figure:
    """
    Bar chart of average service hours per student by grade.
    Accepts *types* so it respects the same service-type filter as the
    participation chart.  AY is not mutated.
    """
    total_time_series = (AY[types].sum(axis=1) / 60).rename('Average Service Time')
    avg_by_grade = (
        pd.concat([AY['Grade Level'], total_time_series], axis=1)
        .groupby('Grade Level')['Average Service Time']
        .mean()
        .reset_index()
    )
    avg_by_grade['Average Service Time'] = avg_by_grade['Average Service Time'].round(2)
    avg_by_grade.sort_values(
        'Grade Level',
        key=lambda x: x.map({g: int(g) for g in avg_by_grade['Grade Level'].unique()}),
        inplace=True,
    )
    return px.bar(
        avg_by_grade,
        x='Grade Level', y='Average Service Time',
        text=avg_by_grade['Average Service Time'],
        title='Average Service Time per Student by Grade',
    )


# ── Services Year-to-Year ──────────────────────────────────────────────────────

def get_y_t_y_service_time_by_type(AY: pd.DataFrame) -> go.Figure:
    svc = AY.groupby('High School AY')[SERVICE_TYPES].sum().reset_index()
    svc['Total Service Mins'] = svc[SERVICE_TYPES].sum(axis=1)
    pct_cols: list[str] = []
    for col in SERVICE_TYPES:
        pct_col = col + ' Percentage'
        svc[pct_col] = round(svc[col] / svc['Total Service Mins'] * 100, 5)
        pct_cols.append(pct_col)

    melted = svc[['High School AY'] + pct_cols].melt(
        id_vars='High School AY', value_vars=pct_cols,
        var_name='Service Type', value_name='Percent',
    )
    order = (
        melted.groupby('Service Type')['Percent'].sum()
        .sort_values(ascending=False).index.tolist()
    )
    return px.bar(
        melted, x='High School AY', y='Percent',
        color='Service Type', category_orders={'Service Type': order},
        title='Percentage of Time Spent by Service Category',
    )


def get_y_t_y_enrollments(AY: pd.DataFrame) -> go.Figure:
    counts = AY.groupby('High School AY').size().to_frame('Students').reset_index()
    return px.bar(
        counts, x='High School AY', y='Students',
        labels={'High School AY': 'School Year'},
        text_auto=True, title='Enrollment Count by Year',
    )


def get_participation_by_month(
    AY: pd.DataFrame,
    duration_by_student_month_type: pd.DataFrame,
    threshold: float,
    service_types: list[str],
) -> go.Figure:
    month_order = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
                   'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']

    students_per_year  = AY.groupby('High School AY').size().to_frame('Student Count').reset_index()
    months_df          = pd.DataFrame({'Month': list(range(1, 13))})
    students_per_month = students_per_year.merge(months_df, how='cross')

    filtered = duration_by_student_month_type[
        duration_by_student_month_type['Service Type Code'].isin(service_types)
    ]
    by_month_student = (
        filtered.groupby(['High School AY', 'Month', 'National CCREC Student ID'])['Total Time']
        .sum().reset_index()
    )
    by_month_student['Total Time'] = by_month_student['Total Time'] / 60

    qualified = (
        by_month_student if threshold == 0
        else by_month_student[by_month_student['Total Time'] >= threshold]
    )

    participation = (
        qualified.groupby(['High School AY', 'Month'])['National CCREC Student ID']
        .nunique().reset_index()
        .rename(columns={'National CCREC Student ID': 'Student Participation Count'})
    )
    combined = (
        participation
        .merge(students_per_month, how='right', on=['High School AY', 'Month'])
        .fillna(0)
    )
    combined['Participation Percent'] = round(
        combined['Student Participation Count'] / combined['Student Count'] * 100, 2
    )
    combined['Month'] = pd.Categorical(
        combined['Month'].map(month_map), categories=month_order, ordered=True
    )
    combined.sort_values('Month', inplace=True)

    return px.line(
        combined, x='Month', y='Participation Percent',
        color='High School AY', markers=True,
        title='Service Participation Percentage by Month',
    )


def get_hours_per_student_by_month(
    AY: pd.DataFrame,
    agg_services_df: pd.DataFrame,
    service_types: list[str],
) -> go.Figure:
    month_order = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
                   'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']

    students_per_year  = AY.groupby('High School AY').size().to_frame('Student Count').reset_index()
    months_df          = pd.DataFrame({'Month': list(range(1, 13))})
    students_per_month = students_per_year.merge(months_df, how='cross')

    filtered_svc = agg_services_df[agg_services_df['Service Type Code'].isin(service_types)]
    total_mins   = (
        filtered_svc.groupby(['High School AY', 'Month'])['Total Minutes']
        .sum().reset_index()
    )
    combined = (
        total_mins
        .merge(students_per_month, how='right', on=['High School AY', 'Month'])
        .fillna(0)
    )
    combined['Hours per Student'] = round(
        combined['Total Minutes'] / combined['Student Count'] / 60, 2
    )
    combined['Month'] = pd.Categorical(
        combined['Month'].map(month_map), categories=month_order, ordered=True
    )
    combined.sort_values('Month', inplace=True)

    return px.line(
        combined, x='Month', y='Hours per Student',
        color='High School AY', markers=True,
        title='Average Service Hours per Student by Month',
    )


# ── Objectives ─────────────────────────────────────────────────────────────────

def get_gpa_by_grade(
    AY: pd.DataFrame,
    gpa_type: str,
    gpa_low: float,
    gpa_high: float,
    gpa_benchmark: float,
) -> go.Figure:
    gpas = AY[['Grade Level', gpa_type]].copy()
    gpas = gpas[~gpas['Grade Level'].isin(['7', '8', '13'])]
    gpas[gpa_type] = gpas[gpa_type].fillna(9.99)

    conditions = [
        gpas[gpa_type] <= gpa_low,
        (gpas[gpa_type] > gpa_low) & (gpas[gpa_type] < gpa_high),
        (gpas[gpa_type] >= gpa_high) & (gpas[gpa_type] < 9),
    ]
    choices = [
        f'Low: <= {gpa_low}',
        f'Medium: > {gpa_low}; < {gpa_high}',
        f'High: >= {gpa_high}',
    ]
    gpas['GPA Range'] = np.select(conditions, choices, default='Unknown')

    counts = gpas.groupby(['Grade Level', 'GPA Range']).size().to_frame('Student Count').reset_index()
    counts['Percentage'] = counts.groupby('Grade Level')['Student Count'].transform(
        lambda x: round(x / x.sum() * 100, 1)
    )
    counts.sort_values(
        'Grade Level',
        key=lambda x: x.map({g: int(g) for g in counts['Grade Level'].unique()}),
        inplace=True,
    )

    pivoted  = counts.pivot(index='Grade Level', columns='GPA Range', values='Percentage').reset_index()
    avg_gpa  = (
        gpas[gpas[gpa_type] != 9.99].groupby('Grade Level')[gpa_type]
        .mean().round(2).to_frame('Average GPA').reset_index()
    )
    pivoted = pivoted.merge(avg_gpa, on='Grade Level', how='left')

    stack_cols = [
        f'Low: <= {gpa_low}',
        f'Medium: > {gpa_low}; < {gpa_high}',
        f'High: >= {gpa_high}',
        'Unknown',
    ]
    fig = make_subplots(specs=[[{'secondary_y': True}]])

    for col in stack_cols:
        if col not in pivoted.columns:
            continue
        fig.add_trace(go.Bar(
            x=pivoted['Grade Level'],
            y=pivoted[col],
            offsetgroup=0,
            name=col,
            text=pivoted[col].astype('str') + '%',
        ), secondary_y=False)

    fig.add_trace(go.Bar(
        x=pivoted['Grade Level'],
        y=pivoted['Average GPA'],
        name='Average GPA',
        offsetgroup=1,
        text=pivoted['Average GPA'],
    ), secondary_y=True)

    fig.update_layout(barmode='stack', title='GPA Ranges and Averages')
    fig.update_xaxes(
        type='category',
        categoryarray=['9', '10', '11', '12'],
        title='Grade Level',
    )
    fig.update_yaxes(
        title_text='Percent of Students',
        range=[0, 100], showticklabels=False, secondary_y=False,
    )
    fig.update_yaxes(
        title_text='Average GPA',
        range=[0, 4], secondary_y=True,
    )
    fig.add_hline(
        y=gpa_benchmark,
        line_dash='dash', line_width=2,
        line_color=benchmark_line_color,
        secondary_y=True,
    )
    return fig


def get_alg1_by_grade(AY: pd.DataFrame) -> go.Figure:
    # TODO: build Algebra 1 completion chart once data validation is complete.
    return no_data_figure('Algebra 1 Status — Chart Under Development')


def get_fafsa(AY: pd.DataFrame) -> go.Figure:
    """Pie chart of FAFSA status for 12th-graders. Returns a no-data figure if no seniors exist."""
    seniors = AY[AY['Grade Level'].isin([12, '12'])][
        ['National CCREC Student ID', 'Grade Level', 'FAFSA status code']
    ]
    if seniors.empty:
        return no_data_figure('No Seniors in the Current Year or Filters')

    percents = (
        seniors.groupby('FAFSA status code').size()
        .transform(lambda x: round(x / x.sum() * 100, 1))
        .to_frame('Percent of Seniors').reset_index()
    )
    return px.pie(percents, names='FAFSA status code',
                  values='Percent of Seniors', title='FAFSA Completion')


# ── Sankey helpers ─────────────────────────────────────────────────────────────

def _get_next_sankey_level(level: str) -> list[str]:
    levels: dict[str, list[str]] = {
        'FAFSA status code':        ['HS Grad Status code', 'Post Secondary Enrollment', 'Post Secondary Graduation'],
        'HS Grad Status code':      ['Post Secondary Enrollment', 'Post Secondary Graduation'],
        'Post Secondary Enrollment':['Post Secondary Graduation'],
        'Post Secondary Graduation':[],
        'None':                     [],
    }
    return levels.get(level, [])


def get_sankey(
    AY: pd.DataFrame,
    l1_selection: str | None,
    l2_selection: str | None,
    l3_selection: str | None,
    l4_selection: str | None,
) -> tuple:
    """
    Build a configurable Sankey diagram from AY outcome columns.
    Returns (l1_options, l1_sel, l2_options, l2_sel,
             l3_options, l3_sel, l4_options, l4_sel, figure).
    AY is not mutated — computed columns are added to a local copy.
    """
    # Add computed columns to a local copy
    df = AY.copy()
    df['Post Secondary Enrollment'] = np.where(
        df['First College Attended Name'].isna() |
        df['First College Attended Name'].str.lower().eq('not found'),
        'Did Not Enroll', 'Enrolled',
    )
    df['Post Secondary Graduation'] = np.where(
        df['Graduated Y/N'].isna() | df['Graduated Y/N'].str.lower().eq('n'),
        'Has Not Graduated', 'Graduated',
    )

    l1_options = ['FAFSA status code', 'HS Grad Status code', 'Post Secondary Enrollment']
    if not l1_selection:
        l1_selection = 'FAFSA status code'

    options_dict = {
        'l1_selection': l1_selection,
        'l2_selection': l2_selection,
        'l3_selection': l3_selection,
        'l4_selection': l4_selection,
    }
    level_counter = 2
    for key in ['l1_selection', 'l2_selection', 'l3_selection']:
        next_opts = _get_next_sankey_level(options_dict[key])
        if level_counter > 2:
            next_opts = ['None'] + next_opts
        options_dict[f'l{level_counter}_options'] = next_opts
        if options_dict[f'l{level_counter}_selection'] not in next_opts:
            options_dict[f'l{level_counter}_selection'] = next_opts[0]
        level_counter += 1

    selection_list = [
        x for x in [
            options_dict['l1_selection'], options_dict['l2_selection'],
            options_dict['l3_selection'], options_dict['l4_selection'],
        ] if x != 'None'
    ]

    # Node / metadata construction
    node_list:      list[str]       = []
    node_level_map: dict[int, int]  = {}
    sankey_meta:    dict            = {}
    node_index = 0
    for level_num, col_name in enumerate(selection_list, start=1):
        sankey_meta[level_num] = {'column': col_name, 'values': {}}
        for val in df[col_name].drop_duplicates().tolist():
            node_level_map[node_index] = level_num
            node_list.append(val)
            sankey_meta[level_num]['values'][val] = len(node_list) - 1
            node_index += 1

    # X positions and colours
    n_levels  = len(sankey_meta)
    x_step    = 1 / (n_levels - 1) if n_levels > 1 else 1
    x_splits  = [round(i * x_step, 2) for i in range(n_levels)]
    x_locs:   list[float] = []
    colours:  list[str]   = []
    for lvl_i, x_val in enumerate(x_splits, start=1):
        for _ in sankey_meta[lvl_i]['values']:
            colours.append(mark_colors[lvl_i - 1])
            x_locs.append(x_val)

    # Link construction
    source_list: list[int]   = []
    target_list: list[int]   = []
    value_list:  list[int]   = []
    for i in range(1, n_levels):
        for src_val, src_idx in sankey_meta[i]['values'].items():
            for tgt_val, tgt_idx in sankey_meta[i + 1]['values'].items():
                source_list.append(src_idx)
                target_list.append(tgt_idx)
                value_list.append(
                    len(df[
                        (df[sankey_meta[i]['column']] == src_val) &
                        (df[sankey_meta[i + 1]['column']] == tgt_val)
                    ])
                )

    # Per-node percentages
    links_df = pd.DataFrame({'Source': source_list, 'Target': target_list, 'Value': value_list})
    out_cnt  = links_df.groupby('Source')['Value'].sum().to_frame('Out Sum').reset_index().rename(columns={'Source': 'Node'})
    in_cnt   = links_df.groupby('Target')['Value'].sum().to_frame('In Sum').reset_index().rename(columns={'Target': 'Node'})
    combined = out_cnt.merge(in_cnt, how='outer', on='Node')
    combined['Val']   = combined[['Out Sum', 'In Sum']].max(axis=1)
    combined['Level'] = combined['Node'].map(node_level_map)
    combined['Percent'] = combined.groupby('Level')['Val'].transform(
        lambda x: round(x / x.sum() * 100, 1)
    )
    combined = combined.set_index('Node')

    node_labels_with_pct = [
        f"{sankey_meta[node_level_map[i]]['column']}: {node_list[i]} "
        f"— {combined.loc[i, 'Percent']}%"
        for i in range(len(node_list))
    ]

    link_hover: list[str] = []
    for src_idx, tgt_idx, val in zip(source_list, target_list, value_list):
        src_field = sankey_meta[node_level_map[src_idx]]['column']
        src_label = node_list[src_idx]
        tgt_field = sankey_meta[node_level_map[tgt_idx]]['column']
        tgt_label = node_list[tgt_idx]
        pct_src   = round((val / combined.loc[src_idx, 'Val']) * 100, 2)
        pct_tgt   = round((val / combined.loc[tgt_idx, 'Val']) * 100, 2)
        link_hover.append(
            f'Given the active filters and year, {val} students had a '
            f'{src_field} of "{src_label}" and a {tgt_field} of "{tgt_label}".<br />'
            f'This is {pct_src}% of "{src_label}" students and '
            f'{pct_tgt}% of "{tgt_label}" students.'
        )

    sankey_fig = go.Figure(data=[go.Sankey(
        arrangement='fixed',
        node=dict(
            pad=5, thickness=40,
            line=dict(color='black', width=0.5),
            label=node_list,
            customdata=node_labels_with_pct,
            hovertemplate='%{customdata}',
            x=x_locs,
            color=colours,
        ),
        link=dict(
            source=source_list, target=target_list, value=value_list,
            customdata=link_hover,
            hovertemplate='%{customdata}',
        ),
    )])

    # Column header annotations
    lable_x_map = {0: -0.02, 0.33: 0.30, 0.5: 0.50, 0.67: 0.71, 1: 1.02}
    for i, x_val in enumerate(x_splits):
        sankey_fig.add_annotation(
            x=lable_x_map.get(x_val, x_val), y=1.06,
            text=selection_list[i], showarrow=False,
        )

    return (
        l1_options, l1_selection,
        options_dict['l2_options'], options_dict['l2_selection'],
        options_dict['l3_options'], options_dict['l3_selection'],
        options_dict['l4_options'], options_dict['l4_selection'],
        sankey_fig,
    )


# ── Objectives Year-to-Year ────────────────────────────────────────────────────

def get_benchmark_line(
    years: list[str],
    benchmark: float,
    increase: float,
    benchmark_year: str,
    offset: str | None,
) -> go.Scatter:
    years_df     = pd.DataFrame({'Year': years})
    benchmark_df = pd.DataFrame({'Year': [benchmark_year], 'Benchmark': [benchmark]})
    benchmark_df = benchmark_df.merge(years_df, on='Year', how='outer')
    benchmark_df = benchmark_df.set_index('Year')

    for direction in (1, -1):
        running_val  = benchmark
        running_year = benchmark_year
        while True:
            parts = running_year.split('-')
            running_year = f'{int(parts[0]) + direction}-{int(parts[1]) + direction}'
            if running_year in benchmark_df.index:
                running_val += increase * direction
                benchmark_df.loc[running_year, 'Benchmark'] = running_val
            else:
                break

    return go.Scatter(
        x=benchmark_df['Year'], y=benchmark_df['Benchmark'],
        mode='lines+markers', name='Benchmark',
        line_dash='dash', line_color=benchmark_line_color,
        zorder=2, offsetgroup=offset,
    )


def get_yty_gpa(
    AY: pd.DataFrame,
    years: list[str],
    gpa_type: str,
    yty_gpa_radio: str,
    gpa_yty_benchmark_input: float | None,
    gpa_yty_increase_input: float | None,
    gpa_yty_benchmark_year: str | None,
) -> go.Figure:
    benchmark_line = (
        get_benchmark_line(years, gpa_yty_benchmark_input, gpa_yty_increase_input,
                           gpa_yty_benchmark_year, '1')
        if all([gpa_yty_benchmark_input, gpa_yty_increase_input, gpa_yty_benchmark_year])
        else None
    )

    gpa_df = AY[['High School AY', gpa_type]].copy()
    gpa_df['Availability'] = np.where(
        gpa_df[gpa_type].isna() | (gpa_df[gpa_type] > 6), 'Missing', 'Available'
    )

    availability = (
        gpa_df.groupby(['High School AY', 'Availability']).size()
        .to_frame('Student Count').reset_index()
    )
    availability['Percent'] = availability.groupby('High School AY')['Student Count'].transform(
        lambda x: round(x / x.sum() * 100, 1)
    )
    availability = (
        availability.pivot(index='High School AY', columns='Availability', values='Percent')
        .reset_index()
    )
    availability['Available'] = availability.get('Available', 0).fillna(0)

    avg_gpa = (
        gpa_df[gpa_df['Availability'] == 'Available']
        .groupby('High School AY')[gpa_type].mean()
        .round(2).to_frame('Average GPA').reset_index()
    )
    full_data = availability[['High School AY']].drop_duplicates().merge(avg_gpa, on='High School AY', how='left').fillna(0)
    full_data = full_data.merge(availability, on='High School AY', how='left')

    fig = make_subplots(specs=[[{'secondary_y': True}]])
    for col in ['Available', 'Missing']:
        if col not in full_data.columns:
            continue
        fig.add_trace(go.Bar(
            x=full_data['High School AY'], y=full_data[col],
            name=col, text=full_data[col].astype('str') + '%',
        ), secondary_y=True)

    fig.add_trace(go.Bar(
        x=full_data['High School AY'], y=full_data['Average GPA'],
        name='Average GPA', offsetgroup=1,
        text=full_data['Average GPA'],
    ), secondary_y=False)

    fig.update_layout(barmode='stack', title='GPA Missingness and Average by Year')
    fig.update_yaxes(showticklabels=False, showgrid=False, secondary_y=True)
    fig.update_yaxes(title_text='Average GPA', range=[0, 4], secondary_y=False)

    if isinstance(benchmark_line, go.Scatter):
        fig.add_trace(benchmark_line)
        fig.update_layout(scattermode='group')

    return fig


def get_yty_fafsa(
    AY: pd.DataFrame,
    years: list[str],
    fafsa_yty_benchmark_input: float | None,
    fafsa_yty_increase_input: float | None,
    fafsa_yty_benchmark_year: str | None,
) -> go.Figure:
    benchmark_line = (
        get_benchmark_line(years, fafsa_yty_benchmark_input, fafsa_yty_increase_input,
                           fafsa_yty_benchmark_year, None)
        if all([fafsa_yty_benchmark_input, fafsa_yty_increase_input, fafsa_yty_benchmark_year])
        else None
    )

    fafsa_df = AY.loc[AY['Grade Level'].isin([12, '12']), ['High School AY', 'Grade Level', 'FAFSA status code']]
    counts   = fafsa_df.groupby(['High School AY', 'FAFSA status code']).size().to_frame('Student Count').reset_index()
    counts['Percent'] = counts.groupby('High School AY')['Student Count'].transform(
        lambda x: round(x / x.sum() * 100, 1)
    )
    counts.sort_values('High School AY', inplace=True)

    fig = px.bar(
        counts, title='FAFSA Completion by Year',
        x='High School AY', y='Percent', color='FAFSA status code',
        barmode='stack', text_auto=True,
        category_orders={'High School AY': counts['High School AY'].drop_duplicates().sort_values().tolist()},
    ).update_traces(texttemplate='%{y}%').update_layout(legend={'title_text': None})

    if isinstance(benchmark_line, go.Scatter):
        fig.add_trace(benchmark_line)
    return fig


def get_yty_graduation(
    AY: pd.DataFrame,
    years: list[str],
    graduation_yty_benchmark_input: float | None,
    graduation_yty_increase_input: float | None,
    graduation_yty_benchmark_year: str | None,
) -> go.Figure:
    benchmark_line = (
        get_benchmark_line(years, graduation_yty_benchmark_input, graduation_yty_increase_input,
                           graduation_yty_benchmark_year, None)
        if all([graduation_yty_benchmark_input, graduation_yty_increase_input, graduation_yty_benchmark_year])
        else None
    )

    grad_df = AY.loc[AY['Grade Level'].isin([12, '12']), ['High School AY', 'Grade Level', 'HS Grad Status code']]
    counts  = grad_df.groupby(['High School AY', 'HS Grad Status code']).size().to_frame('Student Count').reset_index()
    counts['Percent'] = counts.groupby('High School AY')['Student Count'].transform(
        lambda x: round(x / x.sum() * 100, 1)
    )

    fig = px.bar(
        counts, title='Graduation by Year',
        x='High School AY', y='Percent', color='HS Grad Status code',
        barmode='stack', text_auto=True,
        category_orders={
            'High School AY': counts['High School AY'].drop_duplicates().sort_values().tolist(),
            'HS Grad Status code': ['Graduated', 'Did Not Graduate', 'Graduation Status Unknown', 'N/A'],
        },
    ).update_traces(texttemplate='%{y}%').update_layout(legend={'title_text': None})

    if isinstance(benchmark_line, go.Scatter):
        fig.add_trace(benchmark_line)
    return fig


def get_yty_pse(
    AY: pd.DataFrame,
    years: list[str],
    pse_yty_benchmark_input: float | None,
    pse_yty_increase_input: float | None,
    pse_yty_benchmark_year: str | None,
) -> go.Figure:
    benchmark_line = (
        get_benchmark_line(years, pse_yty_benchmark_input, pse_yty_increase_input,
                           pse_yty_benchmark_year, None)
        if all([pse_yty_benchmark_input, pse_yty_increase_input, pse_yty_benchmark_year])
        else None
    )

    pse_df = AY.loc[
        AY['Grade Level'].isin([12, '12']) & (AY['HS Grad Status code'] == 'Graduated'),
        ['High School AY', 'First College Attended Name'],
    ].copy()
    pse_df['Post Secondary Enrollment'] = np.where(
        pse_df['First College Attended Name'].isna() |
        pse_df['First College Attended Name'].str.lower().eq('not found'),
        'Did Not Enroll', 'Enrolled',
    )
    by_year = pse_df.groupby(['High School AY', 'Post Secondary Enrollment']).size().to_frame('Student Count').reset_index()
    by_year['Percent'] = by_year.groupby('High School AY')['Student Count'].transform(
        lambda x: round(x / x.sum() * 100, 1)
    )

    fig = px.bar(
        by_year, title='Post Secondary Enrollment by Year',
        x='High School AY', y='Percent',
        color='Post Secondary Enrollment', barmode='stack', text_auto=True,
        category_orders={
            'High School AY': by_year['High School AY'].drop_duplicates().sort_values().tolist(),
            'Post Secondary Enrollment': ['Enrolled', 'Did Not Enroll'],
        },
    ).update_traces(texttemplate='%{y}%').update_layout(legend={'title_text': None})

    if isinstance(benchmark_line, go.Scatter):
        fig.add_trace(benchmark_line)
    return fig


# ── District comparison ────────────────────────────────────────────────────────

def get_service_time_pie(AY: pd.DataFrame, title_text: str) -> go.Figure:
    time_by_type = AY[SERVICE_TYPES].sum().to_frame('Hours').reset_index()
    total         = time_by_type['Hours'].sum()
    time_by_type['Percent'] = round(time_by_type['Hours'] / total * 100, 1)
    time_by_type.rename(columns={'index': 'Service Category'}, inplace=True)
    time_by_type = time_by_type[time_by_type['Percent'] != 0]
    return px.pie(time_by_type, names='Service Category',
                  values='Percent', title=title_text)


def _get_double_stacked_formatting(groups: int) -> tuple[int, int, int, int]:
    params = {
        1: (10, 35,  2, -105),
        2: (5,  9,   9,  -50),
        3: (4,  7,   7,  -42),
        4: (2,  3,   4,  -25),
        5: (2,  3,   4,  -25),
    }
    return params.get(groups, (1, 0, 4, -15))


def _get_participation_ranges(
    AY: pd.DataFrame,
    participation_low: float,
    participation_high: float,
    group_label: str,
) -> pd.DataFrame:
    """
    Compute participation-range percentages per grade.
    Returns a pivoted DataFrame.  AY is not mutated.
    """
    total_time = AY[SERVICE_TYPES].sum(axis=1) / 60
    conditions = [
        total_time == 0,
        (total_time > 0) & (total_time <= participation_low),
        (total_time > participation_low) & (total_time <= participation_high),
        total_time > participation_high,
    ]
    choices = [
        'No Participation',
        f'Low: <= {participation_low}',
        f'Medium: > {participation_low}; <= {participation_high}',
        f'High: > {participation_high}',
    ]
    temp = pd.concat(
        [AY['Grade Level'], pd.Series(np.select(conditions, choices, default='Unknown'),
                                       name='Participation Range', index=AY.index)],
        axis=1,
    )
    by_grade = temp.groupby(['Grade Level', 'Participation Range']).size().to_frame('Student Count').reset_index()
    by_grade['Percent'] = by_grade.groupby('Grade Level')['Student Count'].transform(
        lambda x: round(x / x.sum() * 100, 1)
    )
    if group_label:
        by_grade['Group'] = group_label
    return by_grade.pivot(index='Grade Level', columns='Participation Range', values='Percent').reset_index().fillna(0)


def get_service_participation_compare(
    AY: pd.DataFrame,
    district_AY: pd.DataFrame,
    participation_low: float,
    participation_high: float,
) -> go.Figure:
    program_part  = _get_participation_ranges(AY,          participation_low, participation_high, 'Program')
    district_part = _get_participation_ranges(district_AY, participation_low, participation_high, 'District')

    district_grades = district_part['Grade Level'].tolist()
    program_part    = program_part[program_part['Grade Level'].isin(district_grades)]

    stack_cols = [
        f'Low: <= {participation_low}',
        f'Medium: > {participation_low}; <= {participation_high}',
        f'High: > {participation_high}',
        'No Participation',
    ]
    color_map = {
        stack_cols[0]: CCREC_orange,
        stack_cols[1]: CCREC_blue,
        stack_cols[2]: CCREC_green,
        stack_cols[3]: CCREC_light_grey,
    }

    fig = go.Figure()
    for count, df in enumerate([program_part, district_part]):
        for col in stack_cols:
            if col not in df:
                continue
            fig.add_trace(go.Bar(
                x=df['Grade Level'], y=df[col],
                offsetgroup=count, legendgroup=col,
                showlegend=(count == 0),
                marker_color=color_map[col], name=col,
                text=df[col].astype('str') + '%',
                customdata=df['Grade Level'],
                hovertemplate=(
                    f'Participation: {col} hrs<br>'
                    'Grade: %{customdata}<br>'
                    'Students: %{y}%<extra></extra>'
                ),
            ))

    breaks, nudges, prespaces, standoff = _get_double_stacked_formatting(len(district_grades))
    fig.update_layout(
        barmode='stack', title='Service Participation',
        bargroupgap=0.05,
        xaxis=dict(
            tickvals=district_grades,
            ticktext=[
                f'{"&nbsp;" * nudges}{" " * prespaces}{g}th — district'
                f'{"<br>" * breaks}{g}th — program'
                for g in district_grades
            ],
            tickangle=45,
            ticklabelstandoff=standoff,
        ),
    )
    return fig


def _get_avg_gpa_by_grade(df: pd.DataFrame, gpa_type: str, group_label: str) -> pd.DataFrame:
    gpas = df[['Grade Level', gpa_type]].copy()
    gpas = gpas[~gpas['Grade Level'].isin(['7', '8', '13'])]
    gpas = gpas[(gpas[gpa_type] != 9.99) & (~gpas[gpa_type].isna()) & (gpas[gpa_type] != 0)]
    result = gpas.groupby('Grade Level')[gpa_type].mean().round(2).to_frame('Average GPA').reset_index()
    result['Group'] = group_label
    return result


def get_gpa_compare(AY: pd.DataFrame, district_AY: pd.DataFrame, gpa_type: str) -> go.Figure:
    """Grouped bar comparing average GPA between district and program. Returns a no-data figure if the district has no HS grades."""
    if district_AY[district_AY['Grade Level'].isin(GRADE_LEVELS_HS)].empty:
        return no_data_figure('No GPA data for the selected district and filters')
    gpas = pd.concat([_get_avg_gpa_by_grade(AY, gpa_type, 'Program'),
                      _get_avg_gpa_by_grade(district_AY, gpa_type, 'District')])
    return px.bar(gpas, x='Grade Level', y='Average GPA', color='Group',
                  barmode='group', title=f'Average GPA ({gpa_type})', text_auto=True)


def _get_general_percent(df: pd.DataFrame, col: str, group_label: str) -> pd.DataFrame:
    counts = df.groupby(col).size().to_frame('Student Count').reset_index()
    counts['Percent'] = round(counts['Student Count'] / counts['Student Count'].sum() * 100, 1)
    counts['Group']   = group_label
    return counts


def get_fafsa_compare(AY: pd.DataFrame, district_AY: pd.DataFrame) -> go.Figure:
    """Stacked bar comparing FAFSA status between district and program seniors."""
    if district_AY.empty:
        return no_data_figure('No FAFSA data for the selected district and filters')
    fafsa = pd.concat([
        _get_general_percent(AY, 'FAFSA status code', 'Program'),
        _get_general_percent(district_AY, 'FAFSA status code', 'District'),
    ])
    return (
        px.bar(fafsa, x='Group', y='Percent', color='FAFSA status code',
               barmode='stack', text_auto=True)
        .update_traces(texttemplate='%{y}%')
    )


def get_graduation_compare(AY: pd.DataFrame, district_AY: pd.DataFrame) -> go.Figure:
    """Stacked bar comparing graduation status between district and program seniors."""
    if district_AY.empty:
        return no_data_figure('No graduation data for the selected district and filters')
    grad = pd.concat([
        _get_general_percent(AY, 'HS Grad Status code', 'Program'),
        _get_general_percent(district_AY, 'HS Grad Status code', 'District'),
    ])
    return (
        px.bar(grad, x='Group', y='Percent', color='HS Grad Status code',
               barmode='stack', text_auto=True)
        .update_traces(texttemplate='%{y}%')
    )


def get_pse_compare(AY: pd.DataFrame, district_AY: pd.DataFrame) -> go.Figure:
    """Stacked bar comparing PSE enrollment between district and program seniors. AY inputs are not mutated."""
    if district_AY.empty:
        return no_data_figure('No PSE data for the selected district and filters')

    def _add_pse_col(df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        out['Post Secondary Enrollment'] = np.where(
            out['First College Attended Name'].isna() |
            out['First College Attended Name'].str.lower().eq('not found'),
            'Did Not Enroll', 'Enrolled',
        )
        return out

    pse = pd.concat([
        _get_general_percent(_add_pse_col(AY),          'Post Secondary Enrollment', 'Program'),
        _get_general_percent(_add_pse_col(district_AY), 'Post Secondary Enrollment', 'District'),
    ])
    return (
        px.bar(pse, x='Group', y='Percent', color='Post Secondary Enrollment',
               barmode='stack', text_auto=True)
        .update_traces(texttemplate='%{y}%')
    )