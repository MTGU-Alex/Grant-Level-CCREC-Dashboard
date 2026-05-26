from dash import dcc, html

def get_layout(years):
    return(html.Div([
        dcc.Store(id='current-page', data='demographics'),
        html.Div([
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='year-filter',
                        options=[{'label': c, 'value': c} for c in sorted(years)],
                        value=sorted(years)[-1],
                        clearable=False
                    ),
                    html.H1(id='page-title')
                ], id='header-row-1'),
                html.Div([
                    html.Div([
                        html.H4('Total Service Hours: ', className='header-stat-text'),
                        html.Div(id='total-service-hours', className='header-number')
                    ], id='total-service-hour-div', className='stat-element'),
                    html.Div([
                        html.H4('Total Students: ', className='header-stat-text'),
                        html.Div(id='total-students', className='header-number')                    
                    ], id='total-students-div', className='stat-element'),
                    html.Div([
                        html.H4('Total Schools: ', className='header-stat-text'),
                        html.Div(id='total-schools', className='header-number')                    
                    ], id='total-schools-div', className='stat-element')
                ], id='header-row-2')
            ], id='header-left'),
            html.Div([
                html.Button('Demographics', id='demographics-btn', n_clicks=0, className='link-button'),
                html.Button('Services', id='services-btn', n_clicks=0, className='link-button'),
                html.Button('Services YTY', id='services-yty-btn', n_clicks=0, className='link-button'),
                html.Button('Compare', id='compare-btn', n_clicks=0, className='link-button'),
                html.Button('Objectives', id='objectives-btn', n_clicks=0, className='link-button'),
                html.Button('Objectives YTY', id='objectives-yty-btn', n_clicks=0, className='link-button')
            ], id='header-right')
        ], id='full-header'),
        html.Div([
            html.H4('Filters: ', id='filter-title'),
            dcc.Store(id='filter-store', data={}),
            html.Div(id='active-filters')
        ], id='filter-box'),
        html.Div(id='page-contents')
    ]))

def get_demographics_layout(enrollment_by_district, enrollment_by_gender, enrollment_by_ethnicity, enrollment_by_grade, enrollment_by_race):
    return html.Div([
        html.Div([
            dcc.Graph(figure=enrollment_by_district, id='enrollment-by-district', className='graph'),
            dcc.Graph(figure=enrollment_by_gender, id='enrollment-by-gender', className='graph'),
            dcc.Graph(figure=enrollment_by_ethnicity, id='enrollment-by-ethnicity', className='graph')
        ], id='demogrpahics-row-1', className='graph-flex'),
        html.Div([
            dcc.Graph(figure=enrollment_by_race, id='enrollment-by-race', className='graph'),
            dcc.Graph(figure=enrollment_by_grade, id='enrollment-by-grade', className='graph')
        ], id='demogrpahics-row-2', className='graph-flex'),
    ])

def get_services_layout(threshold, service_types, services_type_filter, participation_and_avg_time, participation_by_grade, avg_time_by_grade):
    return html.Div([
        html.Div([
            dcc.Graph(figure=participation_and_avg_time, id='participation-and-avg-time', className='graph')
        ], id='services-row-1', className='graph-flex'),
        html.Div([
            html.Div([
                html.H5('Threshold (Hours): ', id='services-threshold-title'),
                html.H5(threshold, id='services-threshold-value'),
                dcc.Slider(
                    id='services-time-slider',
                    min=0,
                    max=50,
                    step=1,
                    value=threshold,
                    marks={i: f'{i}' for i in range(0, 51, 5)}
                ),
                html.Hr(className='hr-line'),
                html.Div([
                    dcc.Checklist(
                        id='services-type-filter',
                        options=service_types,
                        value=services_type_filter,
                        inline=False
                    )
                ], id='services-checklist-div')                
            ], id='services-filters-div'),
            dcc.Graph(figure=participation_by_grade, id='participation-by-grade', className='graph'),
            dcc.Graph(figure=avg_time_by_grade, id='avg-time-by-grade', className='graph')
        ], id='services-row-2', className='graph-flex'),
    ])

def get_yty_layout(threshold, service_types, service_type_filter, service_time_by_type_and_year, enrollment_by_year, participation_by_month, hours_per_student_by_month):
    return html.Div([
        html.Div([
            dcc.Graph(figure=service_time_by_type_and_year, id='yty-service-time-by-type', className='graph'),
            dcc.Graph(figure=enrollment_by_year, id='yty-enrollment', className='graph')
        ], id='yty-row-1', className='graph-flex'),
        html.Div([
            html.Div([
                html.H5('Threshold (Hours): ', id='yty-threshold-title'),
                html.H5(threshold, id='yty-threshold-value'),
                dcc.Slider(
                    id='yty-time-slider',
                    min=0,
                    max=50,
                    step=1,
                    value=threshold,
                    marks={i: f'{i}' for i in range(0, 51, 5)}
                ),
                html.Hr(className='hr-line'),
                html.Div([
                    dcc.Checklist(
                        id='yty-type-filter',
                        options=service_types,
                        value=service_type_filter,
                        inline=False
                    )
                ], id='yty-checklist-div')                
            ], id='yty-filters-div'),
            dcc.Graph(figure=participation_by_month, id='participation-by-month', className='graph')
        ], id='yty-row-2', className='graph-flex'),
        html.Div([
            dcc.Graph(figure=hours_per_student_by_month, id='avg-service-hours-per-student-by-month', className='graph')
        ], id='yty-row-3', className='graph-flex')
    ])

def get_objectives_layout(gpa_type, gpa_low, gpa_high, gpa_benchmark, gpa_by_grade, l1_options, l1_selection, l2_options, l2_selection, l3_options, l3_selection, l4_options, l4_selection, alg1_by_grade, fafsa_completion, graduation_and_pse):    
    
    if type(fafsa_completion) == str:
        fafsa_content = html.Div([
            html.P('No Senior This Year With the Current Filters', id='fafsa-no-seniors-text')
        ], id='fafsa-completion', className='graph')
    else:
        fafsa_content = dcc.Graph(figure=fafsa_completion, id='fafsa-completion', className='graph')
    
    return html.Div([
        html.Div([
            html.Div([
                html.Div([
                    dcc.RadioItems(['Cumulative GPA', 'Final Term GPA'], gpa_type, inline=True, id='gpa-radio'),
                ], id='gpa-radio-div'),
                html.Div([
                    html.H4('GPA Band Ranges:', id='gpa-ranges-title'),
                    dcc.RangeSlider(0, 4, .1, value=[gpa_low, gpa_high], id='gpa-range-slider')
                ], id='gpa-slider-div'),
                html.Div([
                    html.H4('GPA Benchmark: ', id='gpa-benchmark-title'),
                    dcc.Slider(id='gpa-benchmark-slider', min=0, max=4, step=.1, value=gpa_benchmark)
                ], id='gpa-benchmark-div'),
                html.Hr(className='hr-line'),
                html.Div([
                    html.H3('-- Sankey Levels --', id='sankey-level-title'),
                    html.Div([
                        html.P('level 1:', className='sankey-level-label'),
                        html.Div([
                            dcc.Dropdown(
                                id='sankey-l1-dropdown',
                                options=[{'label': c, 'value': c} for c in sorted(l1_options)],
                                value=l1_selection,
                                clearable=False,
                                className='sankey-drop-down'
                            )
                        ], className='sankey-drop-down-div')
                    ], className='sankey-level-flex'),
                    html.Div([
                        html.P('level 2:', className='sankey-level-label'),
                        html.Div([
                            dcc.Dropdown(
                                id='sankey-l2-dropdown',
                                options=[{'label': c, 'value': c} for c in sorted(l2_options)],
                                value=l2_selection,
                                clearable=False,
                                className='sankey-drop-down'
                            ),                            
                        ], className='sankey-drop-down-div')
                    ], className='sankey-level-flex'),                    
                    html.Div([
                        html.P('level 3:', className='sankey-level-label'),
                        html.Div([
                            dcc.Dropdown(
                                id='sankey-l3-dropdown',
                                options=[{'label': c, 'value': c} for c in sorted(l3_options)],
                                value=l3_selection,
                                clearable=False,
                                className='sankey-drop-down'
                            )
                        ], className='sankey-drop-down-div')
                    ], className='sankey-level-flex'),
                    html.Div([
                        html.P('level 4:', className='sankey-level-label'),
                        html.Div([
                            dcc.Dropdown(
                                id='sankey-l4-dropdown',
                                options=[{'label': c, 'value': c} for c in sorted(l4_options)],
                                value=l4_selection,
                                clearable=False,
                                className='sankey-drop-down'
                            )
                        ], className='sankey-drop-down-div')
                    ], className='sankey-level-flex')
                ])
            ], id='objectives-filters', className='graph'),
            dcc.Graph(figure=gpa_by_grade, id='gpa-by-grade', className='graph')
        ], id='objectives-row-1', className='graph-flex'),
        html.Div([
            dcc.Graph(figure=graduation_and_pse, id='graduation-and-pse', className='graph')
        ], id='objectives-row-3', className='graph-flex')
    ])

def get_objectives_yty_layout(yty_gpa_type, gpa_benchmark, gpa_increase, gpa_year, fafsa_benchmark, fafsa_increase, fafsa_year, graduation_benchmark, graduation_increase, graduation_year, pse_benchmark, pse_increase, pse_year, years, avg_gpa_by_year, fafsa_by_year, graduation_by_year, pse_by_year):
    options_dict = {
        'gpa-yty': {
            'text': 'GPA',
            'placeholder': 2.5,
            'optional': html.Div([dcc.RadioItems(['Cumulative GPA', 'Final Term GPA'], yty_gpa_type, inline=True, id='yty-gpa-radio')], id='yty-gpa-radio-div')
        }, 
        'fafsa-yty': {
            'text': 'FAFSA',
            'placeholder': 80,
            'optional': None
        }, 
        'graduation-yty': {
            'text': 'Graduation',
            'placeholder': 60,
            'optional': None
        }, 
        'pse-yty': {
            'text': 'PSE',
            'placeholder': 40,
            'optional': None
        }  
    } 

    if gpa_benchmark:
        options_dict['gpa-yty']['benchmark-value'] = gpa_benchmark
    else:
        options_dict['gpa-yty']['benchmark-value'] = None

    if fafsa_benchmark:
        options_dict['fafsa-yty']['benchmark-value'] = fafsa_benchmark
    else:
        options_dict['fafsa-yty']['benchmark-value'] = None

    if graduation_benchmark:
        options_dict['graduation-yty']['benchmark-value'] = graduation_benchmark
    else:
        options_dict['graduation-yty']['benchmark-value'] = None

    if pse_benchmark:
        options_dict['pse-yty']['benchmark-value'] = pse_benchmark
    else:
        options_dict['pse-yty']['benchmark-value'] = None

    if gpa_increase:
        options_dict['gpa-yty']['increase-value'] = gpa_increase
    else:
        options_dict['gpa-yty']['increase-value'] = None

    if fafsa_increase:
        options_dict['fafsa-yty']['increase-value'] = fafsa_increase
    else:
        options_dict['fafsa-yty']['increase-value'] = None

    if graduation_increase:
        options_dict['graduation-yty']['increase-value'] = graduation_increase
    else:
        options_dict['graduation-yty']['increase-value'] = None

    if pse_increase:
        options_dict['pse-yty']['increase-value'] = pse_increase
    else:
        options_dict['pse-yty']['increase-value'] = None

    if gpa_year:
        options_dict['gpa-yty']['year'] = gpa_year
    else:
        options_dict['gpa-yty']['year'] = sorted(years)[0]

    if fafsa_year:
        options_dict['fafsa-yty']['year'] = fafsa_year
    else:
        options_dict['fafsa-yty']['year'] = sorted(years)[0]

    if graduation_year:
        options_dict['graduation-yty']['year'] = graduation_year
    else:
        options_dict['graduation-yty']['year'] = sorted(years)[0]

    if gpa_year:
        options_dict['pse-yty']['year'] = gpa_year
    else:
        options_dict['pse-yty']['year'] = sorted(years)[0]


    options_div_list = []
    for option_id, option in options_dict.items():
        div = html.Div([
            html.H3(option['text'], id=f'{option_id}-options-title', className='yty-option-title'),
            option['optional'],
            html.Div([
                html.H4('Benchmark:', className='options-text'),
                dcc.Input(
                    id=f'{option_id}-benchmark-input',
                    type='number',
                    placeholder=option['placeholder'],
                    value=option['benchmark-value'],
                    className='options-input'
                )
            ], id=f'{option_id}-benchmark-div', className='yty-benchmark-div'),
            html.Div([
                html.H4('Yearly Increase:', className='options-text'),
                dcc.Input(
                    id=f'{option_id}-increase-input',
                    type='number',
                    placeholder=0,
                    value=option['increase-value'],
                    className='options-input'
                )
            ], id=f'{option_id}-increase-div', className='yty-increase-div'),
            html.Div([
                html.H4('Benchmark year:', className='options-text'),
                dcc.Dropdown(
                    id=f'{option_id}-benchmark-year',
                    options=[{'label': c, 'value': c} for c in sorted(years)],
                    value=option['year'],
                    clearable=False,
                    className='options-input'
                )
            ], id=f'{option_id}-benchmark-year-div', className='yty-benchmark-year-div'),
        ], id=f'{option_id}-options-div', className='yty-option-div')
        options_div_list.append(div)

    return html.Div([
        html.Div([
            html.Div(
                options_div_list,
                id='objectives-yty-options-parent-div', 
                className='graph'
            ),
            dcc.Graph(figure=avg_gpa_by_year, id='average-gpa-by-year', className='graph')
        ], id='objective-yty-row-1', className='graph-flex'),
        html.Div([
            dcc.Graph(figure=fafsa_by_year, id='fafsa-by-year', className='graph'),
            dcc.Graph(figure=graduation_by_year, id='graduation-by-year', className='graph')
        ], id='objective-yty-row-2', className='graph-flex'),
        html.Div([
            dcc.Graph(figure=pse_by_year, id='pse-by-year', className='graph')
        ], id='objective-yty-row-3', className='graph-flex')
    ])


def get_compare_layout(district_list, current_district, range_low, range_high, district_services_time_split, program_services_time_split, service_participation_compare, objective_compare):
    return html.Div([
        html.Div([
            html.Div([
                html.H4('District: '),
                dcc.Dropdown(
                    id='district-dropdown',
                    options=[{'label': c, 'value': c} for c in sorted(district_list)],
                    value=current_district,
                    clearable=False
                ),
                html.H4('Service Ranges (Hours):', id='compare-service-time-range'),
                dcc.RangeSlider(0, 50, 1, value=[range_low, range_high], id='compare-service-ranges')
            ], id='compare-filters-div', className='graph'),
            dcc.Graph(figure=district_services_time_split, id='district-service-time-split', className='graph'),
            dcc.Graph(figure=program_services_time_split, id='program-service-time-split', className='graph')
        ], id='compare-row-1', className='graph-flex'),
        html.Div([
            dcc.Graph(figure=service_participation_compare, id='service-participation-compare', className='graph'),
            dcc.Graph(figure=objective_compare, id='objective-compare', className='graph')
        ], id='compare-row-2', className='graph-flex')
    ])