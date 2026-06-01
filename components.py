# "components.py"
"""
components.py
Pure layout functions — no business logic.
Each function receives pre-built Plotly figures and returns a Dash html.Div.
"""

from dash import dcc, html


# ── Top-level app layout ───────────────────────────────────────────────────────

def get_layout(years) -> html.Div:
    return html.Div([
        # URL location — source-of-truth for the active page
        dcc.Location(id='url', refresh=False),

        # ── Header ─────────────────────────────────────────────────────────────
        html.Div([
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='year-filter',
                        options=[{'label': y, 'value': y} for y in sorted(years)],
                        value=sorted(years)[-1],
                        clearable=False,
                    ),
                    html.H1(id='page-title'),
                ], id='header-row-1'),
                html.Div([
                    html.Div([
                        html.H4('Total Service Hours:', className='header-stat-text'),
                        html.Div(id='total-service-hours', className='header-number'),
                    ], id='total-service-hour-div', className='stat-element'),
                    html.Div([
                        html.H4('Total Students:', className='header-stat-text'),
                        html.Div(id='total-students', className='header-number'),
                    ], id='total-students-div', className='stat-element'),
                    html.Div([
                        html.H4('Total Schools:', className='header-stat-text'),
                        html.Div(id='total-schools', className='header-number'),
                    ], id='total-schools-div', className='stat-element'),
                ], id='header-row-2'),
            ], id='header-left'),
            html.Div([
                html.Button('Demographics',   id='demographics-btn',   n_clicks=0, className='link-button'),
                html.Button('Services',       id='services-btn',       n_clicks=0, className='link-button'),
                html.Button('Services YTY',   id='services-yty-btn',   n_clicks=0, className='link-button'),
                html.Button('Compare',        id='compare-btn',        n_clicks=0, className='link-button'),
                html.Button('Objectives',     id='objectives-btn',     n_clicks=0, className='link-button'),
                html.Button('Objectives YTY', id='objectives-yty-btn', n_clicks=0, className='link-button'),
            ], id='header-right'),
        ], id='full-header'),

        # ── Active-filter display ───────────────────────────────────────────────
        html.Div([
            html.H4('Filters:', id='filter-title'),
            dcc.Store(id='filter-store', data={}),
            html.Div(id='active-filters'),
        ], id='filter-box'),

        # ── Page content — wrapped in Loading spinner ───────────────────────────
        dcc.Loading(
            id='page-loading',
            type='circle',
            color='#0F5C83',
            children=html.Div(id='page-contents'),
            style={'marginTop': '10px'},
        ),
    ])


# ── Demographics page ──────────────────────────────────────────────────────────

def get_demographics_layout(
    enrollment_by_district,
    enrollment_by_gender,
    enrollment_by_ethnicity,
    enrollment_by_grade,
    enrollment_by_race,
) -> html.Div:
    return html.Div([
        html.Div([
            dcc.Graph(figure=enrollment_by_district,  id='enrollment-by-district',  className='graph'),
            dcc.Graph(figure=enrollment_by_gender,    id='enrollment-by-gender',    className='graph'),
            dcc.Graph(figure=enrollment_by_ethnicity, id='enrollment-by-ethnicity', className='graph'),
        ], id='demographics-row-1', className='graph-flex'),
        html.Div([
            dcc.Graph(figure=enrollment_by_race,  id='enrollment-by-race',  className='graph'),
            dcc.Graph(figure=enrollment_by_grade, id='enrollment-by-grade', className='graph'),
        ], id='demographics-row-2', className='graph-flex'),
    ])


# ── Services page ──────────────────────────────────────────────────────────────

def get_services_layout(
    threshold: float,
    service_types: list[str],
    services_type_filter: list[str],
    participation_and_avg_time,
    participation_by_grade,
    avg_time_by_grade,
) -> html.Div:
    return html.Div([
        html.Div([
            dcc.Graph(figure=participation_and_avg_time,
                      id='participation-and-avg-time', className='graph'),
        ], id='services-row-1', className='graph-flex'),
        html.Div([
            html.Div([
                html.H5('Threshold (Hours):', id='services-threshold-title'),
                html.H5(threshold, id='services-threshold-value'),
                dcc.Slider(
                    id='services-time-slider',
                    min=0, max=50, step=1, value=threshold,
                    marks={i: str(i) for i in range(0, 51, 5)},
                ),
                html.Hr(className='hr-line'),
                html.Div([
                    dcc.Checklist(
                        id='services-type-filter',
                        options=service_types,
                        value=services_type_filter,
                        inline=False,
                    ),
                ], id='services-checklist-div'),
            ], id='services-filters-div'),
            dcc.Graph(figure=participation_by_grade, id='participation-by-grade', className='graph'),
            dcc.Graph(figure=avg_time_by_grade,      id='avg-time-by-grade',      className='graph'),
        ], id='services-row-2', className='graph-flex'),
    ])


# ── Services YTY page ──────────────────────────────────────────────────────────

def get_yty_layout(
    threshold: float,
    service_types: list[str],
    service_type_filter: list[str],
    service_time_by_type_and_year,
    enrollment_by_year,
    participation_by_month,
    hours_per_student_by_month,
) -> html.Div:
    return html.Div([
        html.Div([
            dcc.Graph(figure=service_time_by_type_and_year,
                      id='yty-service-time-by-type', className='graph'),
            dcc.Graph(figure=enrollment_by_year, id='yty-enrollment', className='graph'),
        ], id='yty-row-1', className='graph-flex'),
        html.Div([
            html.Div([
                html.H5('Threshold (Hours):', id='yty-threshold-title'),
                html.H5(threshold, id='yty-threshold-value'),
                dcc.Slider(
                    id='yty-time-slider',
                    min=0, max=50, step=1, value=threshold,
                    marks={i: str(i) for i in range(0, 51, 5)},
                ),
                html.Hr(className='hr-line'),
                html.Div([
                    dcc.Checklist(
                        id='yty-type-filter',
                        options=service_types,
                        value=service_type_filter,
                        inline=False,
                    ),
                ], id='yty-checklist-div'),
            ], id='yty-filters-div'),
            dcc.Graph(figure=participation_by_month, id='participation-by-month', className='graph'),
        ], id='yty-row-2', className='graph-flex'),
        html.Div([
            dcc.Graph(figure=hours_per_student_by_month,
                      id='avg-service-hours-per-student-by-month', className='graph'),
        ], id='yty-row-3', className='graph-flex'),
    ])


# ── Objectives page ────────────────────────────────────────────────────────────

def get_objectives_layout(
    gpa_type: str,
    gpa_low: float,
    gpa_high: float,
    gpa_benchmark: float,
    gpa_by_grade,
    l1_options, l1_selection,
    l2_options, l2_selection,
    l3_options, l3_selection,
    l4_options, l4_selection,
    alg1_by_grade,
    fafsa_completion,
    graduation_and_pse,
) -> html.Div:
    # fafsa_completion is always a go.Figure after the no_data_figure refactor
    fafsa_content = dcc.Graph(figure=fafsa_completion, id='fafsa-completion', className='graph')

    return html.Div([
        # Row 1 — GPA controls + GPA chart
        html.Div([
            html.Div([
                html.Div([
                    dcc.RadioItems(['Cumulative GPA', 'Final Term GPA'], gpa_type,
                                   inline=True, id='gpa-radio'),
                ], id='gpa-radio-div'),
                html.Div([
                    html.H4('GPA Band Ranges:', id='gpa-ranges-title'),
                    dcc.RangeSlider(0, 4, 0.1, value=[gpa_low, gpa_high], id='gpa-range-slider'),
                ], id='gpa-slider-div'),
                html.Div([
                    html.H4('GPA Benchmark:', id='gpa-benchmark-title'),
                    dcc.Slider(id='gpa-benchmark-slider', min=0, max=4,
                               step=0.1, value=gpa_benchmark),
                ], id='gpa-benchmark-div'),
                html.Hr(className='hr-line'),
                html.Div([
                    html.H3('— Sankey Levels —', id='sankey-level-title'),
                    *[
                        html.Div([
                            html.P(f'Level {lvl}:', className='sankey-level-label'),
                            html.Div([
                                dcc.Dropdown(
                                    id=f'sankey-l{lvl}-dropdown',
                                    options=[{'label': c, 'value': c} for c in sorted(opts)],
                                    value=sel,
                                    clearable=False,
                                    className='sankey-drop-down',
                                ),
                            ], className='sankey-drop-down-div'),
                        ], className='sankey-level-flex')
                        for lvl, opts, sel in [
                            (1, l1_options, l1_selection),
                            (2, l2_options, l2_selection),
                            (3, l3_options, l3_selection),
                            (4, l4_options, l4_selection),
                        ]
                    ],
                ]),
            ], id='objectives-filters', className='graph'),
            dcc.Graph(figure=gpa_by_grade, id='gpa-by-grade', className='graph'),
        ], id='objectives-row-1', className='graph-flex'),

        # Row 2 — FAFSA + Algebra 1 (Bug A fix: these were computed but never rendered)
        html.Div([
            fafsa_content,
            dcc.Graph(figure=alg1_by_grade, id='alg1-by-grade', className='graph'),
        ], id='objectives-row-2', className='graph-flex'),

        # Row 3 — Graduation / PSE Sankey
        html.Div([
            dcc.Graph(figure=graduation_and_pse, id='graduation-and-pse', className='graph'),
        ], id='objectives-row-3', className='graph-flex'),
    ])


# ── Objectives YTY page ────────────────────────────────────────────────────────

def get_objectives_yty_layout(
    yty_gpa_type: str,
    gpa_benchmark,
    gpa_increase,
    gpa_year,
    fafsa_benchmark,
    fafsa_increase,
    fafsa_year,
    graduation_benchmark,
    graduation_increase,
    graduation_year,
    pse_benchmark,
    pse_increase,
    pse_year,       # Bug B fix: was incorrectly substituted with gpa_year
    years: list[str],
    avg_gpa_by_year,
    fafsa_by_year,
    graduation_by_year,
    pse_by_year,
) -> html.Div:

    options_dict = {
        'gpa-yty': {
            'text':     'GPA',
            'placeholder': 2.5,
            'optional': html.Div(
                [dcc.RadioItems(['Cumulative GPA', 'Final Term GPA'], yty_gpa_type,
                                inline=True, id='yty-gpa-radio')],
                id='yty-gpa-radio-div',
            ),
            'benchmark-value':  gpa_benchmark,
            'increase-value':   gpa_increase,
            'year':             gpa_year or sorted(years)[0],
        },
        'fafsa-yty': {
            'text':            'FAFSA',
            'placeholder':     80,
            'optional':        None,
            'benchmark-value': fafsa_benchmark,
            'increase-value':  fafsa_increase,
            'year':            fafsa_year or sorted(years)[0],
        },
        'graduation-yty': {
            'text':            'Graduation',
            'placeholder':     60,
            'optional':        None,
            'benchmark-value': graduation_benchmark,
            'increase-value':  graduation_increase,
            'year':            graduation_year or sorted(years)[0],
        },
        'pse-yty': {
            'text':            'PSE',
            'placeholder':     40,
            'optional':        None,
            'benchmark-value': pse_benchmark,
            'increase-value':  pse_increase,
            'year':            pse_year or sorted(years)[0],  # Bug B fix
        },
    }

    option_divs = []
    for option_id, option in options_dict.items():
        option_divs.append(html.Div([
            html.H3(option['text'], id=f'{option_id}-options-title', className='yty-option-title'),
            option['optional'],
            html.Div([
                html.H4('Benchmark:', className='options-text'),
                dcc.Input(id=f'{option_id}-benchmark-input', type='number',
                          placeholder=option['placeholder'],
                          value=option['benchmark-value'],
                          className='options-input'),
            ], id=f'{option_id}-benchmark-div', className='yty-benchmark-div'),
            html.Div([
                html.H4('Yearly Increase:', className='options-text'),
                dcc.Input(id=f'{option_id}-increase-input', type='number',
                          placeholder=0, value=option['increase-value'],
                          className='options-input'),
            ], id=f'{option_id}-increase-div', className='yty-increase-div'),
            html.Div([
                html.H4('Benchmark Year:', className='options-text'),
                dcc.Dropdown(
                    id=f'{option_id}-benchmark-year',
                    options=[{'label': y, 'value': y} for y in sorted(years)],
                    value=option['year'],
                    clearable=False,
                    className='options-input',
                ),
            ], id=f'{option_id}-benchmark-year-div', className='yty-benchmark-year-div'),
        ], id=f'{option_id}-options-div', className='yty-option-div'))

    return html.Div([
        html.Div([
            html.Div(option_divs, id='objectives-yty-options-parent-div', className='graph'),
            dcc.Graph(figure=avg_gpa_by_year, id='average-gpa-by-year', className='graph'),
        ], id='objective-yty-row-1', className='graph-flex'),
        html.Div([
            dcc.Graph(figure=fafsa_by_year,      id='fafsa-by-year',      className='graph'),
            dcc.Graph(figure=graduation_by_year, id='graduation-by-year', className='graph'),
        ], id='objective-yty-row-2', className='graph-flex'),
        html.Div([
            dcc.Graph(figure=pse_by_year, id='pse-by-year', className='graph'),
        ], id='objective-yty-row-3', className='graph-flex'),
    ])


# ── Compare page ───────────────────────────────────────────────────────────────

def get_compare_layout(
    district_list: list[str],
    current_district: str,
    range_low: float,
    range_high: float,
    objective_selection: str,
    gpa_type: str,
    district_services_time_split,
    program_services_time_split,
    service_participation_compare,
    objective_compare,     # always a go.Figure after no_data_figure refactor
) -> html.Div:

    gpa_radio = (
        dcc.RadioItems(['Cumulative GPA', 'Final Term GPA'], gpa_type,
                       inline=True, id='compare-gpa-radio')
        if objective_selection == 'GPA'
        else None
    )

    # objective_compare is always a go.Figure — no isinstance check needed
    objectives_content = dcc.Graph(figure=objective_compare,
                                   id='objective-compare', className='graph')

    return html.Div([
        html.Div([
            html.Div([
                html.H4('District:'),
                dcc.Dropdown(
                    id='district-dropdown',
                    options=[{'label': d, 'value': d} for d in sorted(district_list)],
                    value=current_district,
                    clearable=False,
                ),
                html.Hr(className='hr-line'),
                html.H4('Service Ranges (Hours):', id='compare-service-time-range'),
                dcc.RangeSlider(0, 50, 1, value=[range_low, range_high],
                                id='compare-service-ranges'),
                html.Hr(className='hr-line'),
                html.H4('Objectives Chart Selection:'),
                dcc.Dropdown(
                    id='objective-compare-dropdown',
                    options=['GPA', 'FAFSA', 'Graduation', 'Post Secondary Enrollment'],
                    value=objective_selection,
                    clearable=False,
                ),
                gpa_radio,
            ], id='compare-filters-div', className='graph'),
            dcc.Graph(figure=district_services_time_split,
                      id='district-service-time-split', className='graph'),
            dcc.Graph(figure=program_services_time_split,
                      id='program-service-time-split', className='graph'),
        ], id='compare-row-1', className='graph-flex'),
        html.Div([
            dcc.Graph(figure=service_participation_compare,
                      id='service-participation-compare', className='graph'),
            objectives_content,
        ], id='compare-row-2', className='graph-flex'),
    ])