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
                html.Button('Objectives', id='objectives-btn', n_clicks=0, className='link-button'),
                html.Button('Objectives YTY', id='objectives-yty-btn', n_clicks=0, className='link-button'),
                html.Button('Compare', id='compare-btn', n_clicks=0, className='link-button')
            ], id='header-right')
        ], id='full-header'),
        html.Div([
            html.H4('Filters: ', id='filter-title'),
            dcc.Store(id='filter-store', data={}),
            html.Div(id='active-filters')
        ], id='filter-box'),
        html.Div(id='page-contents')
    ]))

def get_demographics_layout(enrollment_by_locale, enrollment_by_gender, enrollment_by_ethnicity, enrollment_by_grade, enrollment_by_race):
    return html.Div([
        html.Div([
            dcc.Graph(figure=enrollment_by_locale, id='enrollment-by-locale', className='graph'),
            dcc.Graph(figure=enrollment_by_gender, id='enrollment-by-gender', className='graph'),
            dcc.Graph(figure=enrollment_by_ethnicity, id='enrollment-by-ethnicity', className='graph')
        ], id='demogrpahics-row-1', className='graph-flex'),
        html.Div([
            dcc.Graph(figure=enrollment_by_grade, id='enrollment-by-grade', className='graph'),
            dcc.Graph(figure=enrollment_by_race, id='enrollment-by-race', className='graph')
        ], id='demogrpahics-row-2', className='graph-flex')
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