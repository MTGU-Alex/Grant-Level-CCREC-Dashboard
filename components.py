from dash import dcc, html

service_types = ['Tutoring/Homework Assistance', 'Mentoring', 'Financial Aid Counseling/Advising', 'Counseling/Advising', 'College Visit', 'Job Site Visit/Job Shadowing', 'Summer Programs', 'Educational Field Trips', 'Student Workshops', 'Parent/Family Workshops', 'Family Counseling/ Advising', 'Family College Visit', 'Other Family Events']

def demographics_layout(AY_df):
    return html.Div([
        html.Div([
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='demographics-year-filter',
                        options=[{'label': c, 'value': c} for c in sorted(AY_df['High School AY'].unique())],
                        value=sorted(AY_df['High School AY'].unique())[-1],
                        clearable=False
                    ),
                    html.H1('CCREC Descriptive Dashboard: Demographics', id='demographics-title')
                ], id='demographics-header-row-1'),
                html.Div([
                    html.Div([
                        html.H4('Total Service Hours: ', className='header-stat-text'),
                        html.Div(id='demographics-total-service-hours', className='header-number')
                    ], id='demographics-total-service-hour-div', className='stat-element'),
                    html.Div([
                        html.H4('Total Students: ', className='header-stat-text'),
                        html.Div(id='demographics-total-students', className='header-number')                    
                    ], id='demographics-total-students-div', className='stat-element'),
                    html.Div([
                        html.H4('Total Schools: ', className='header-stat-text'),
                        html.Div(id='demographics-total-schools', className='header-number')                    
                    ], id='demographics-total-schools-div', className='stat-element')
                ], id='demographics-header-row-2')
            ], id='demographics-header-left'),
            html.Div([
                dcc.Link('Services', href='/services', className='link-button'),
                dcc.Link('Year to Year', href='/yty', className='link-button'),
                dcc.Link('Analytics', href='/analytics', className='link-button')
            ], id='demographics-header-right')
        ], id='demographics-full-header'),
        html.Div([
            html.H4('Filters: ', id='demographics-filter-title'),
            dcc.Store(id='demographics-filter-store', data={}),
            html.Div(id='demographics-active-filters')
        ], id='demographics-filter-box'),
        html.Div([
            dcc.Graph(id='enrollment-by-locale', className='graph'),
            dcc.Graph(id='enrollment-by-gender-fig', className='graph'),
            dcc.Graph(id='enrollment-by-ethnicity-fig', className='graph')
        ], id='demographics-first-row', className='graph-flex'),
        html.Div([
            dcc.Graph(id='enrollment-by-grade-level-fig', className='graph'),
            dcc.Graph(id='enrollment-by-race-fig', className='graph')            
        ], id='demographics-second-row', className='graph-flex')
    ])

def services_layout(AY_df):
    return html.Div([
        html.Div([
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='services-year-filter',
                        options=[{'label': c, 'value': c} for c in sorted(AY_df['High School AY'].unique())],
                        value=sorted(AY_df['High School AY'].unique())[-1],
                        clearable=False
                    ),
                    html.H1('CCREC Descriptive Dashboard: Services', id='services-title')
                ], id='services-header-row-1'),
                html.Div([
                    html.Div([
                        html.H4('Total Service Hours: ', className='header-stat-text'),
                        html.Div(id='services-total-service-hours', className='header-number')
                    ], id='services-total-service-hour-div', className='stat-element'),
                    html.Div([
                        html.H4('Total Students: ', className='header-stat-text'),
                        html.Div(id='services-total-students', className='header-number')                    
                    ], id='services-total-students-div', className='stat-element'),
                    html.Div([
                        html.H4('Total Schools: ', className='header-stat-text'),
                        html.Div(id='services-total-schools', className='header-number')                    
                    ], id='services-total-schools-div', className='stat-element')
                ], id='services-header-row-2')
            ], id='services-header-left'),
            html.Div([
                dcc.Link('Demographics', href='/demographics', className='link-button'),
                dcc.Link('Year to Year', href='/yty', className='link-button'),
                dcc.Link('Analytics', href='/analytics', className='link-button')
            ], id='services-header-right')
        ], id='services-full-header'),
        html.Div([
            html.H4('Filters: ', id='services-filter-title'),
            dcc.Store(id='services-filter-store', data={}),
            html.Div(id='services-active-filters')
        ], id='services-filter-box'),
        html.Div([
            dcc.Graph(id='services-participation', className='graph')
        ], id='services-first-row', className='graph-flex'),
        html.Div([
            html.Div([
                html.H5('Threshold (Hours): ', id='threshold-title'),
                html.H5(id='threshold-value'),
                dcc.Slider(
                    id='service-time-slider',
                    min=0,
                    max=50,
                    step=1,
                    value=0,
                    marks={i: f'{i}' for i in range(0, 51, 5)}
                ),
                html.Hr(className='hr-line'),
                html.Div([
                    dcc.Checklist(
                        id='service-type-filter',
                        options=service_types,
                        value=service_types,
                        inline=False
                    )
                ], id='service-checklist-div'),
            ], id='services-second-row-filters'),
            dcc.Graph(id='service-participation-by-grade', className='graph'),
            dcc.Graph(id='service-time-by-grade', className='graph')
        ], id='services-second-row', className='graph-flex')
    ])

def year_to_year_layout(AY_df):
    years = sorted(AY_df['High School AY'].drop_duplicates().to_list())
    return html.Div([
        html.Div([
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='yty-year-filter',
                        options=[{'label': c, 'value': c} for c in sorted(AY_df['High School AY'].unique())],
                        value=sorted(AY_df['High School AY'].unique())[-1],
                        clearable=False
                    ),
                    html.H1('CCREC Descriptive Dashboard: Year to Year View', id='yty-title')
                ], id='yty-header-row-1'),
                html.Div([
                    html.Div([
                        html.H4('Total Service Hours: ', className='header-stat-text'),
                        html.Div(id='yty-total-service-hours', className='header-number')
                    ], id='yty-total-service-hour-div', className='stat-element'),
                    html.Div([
                        html.H4('Total Students: ', className='header-stat-text'),
                        html.Div(id='yty-total-students', className='header-number')                    
                    ], id='yty-total-students-div', className='stat-element'),
                    html.Div([
                        html.H4('Total Schools: ', className='header-stat-text'),
                        html.Div(id='yty-total-schools', className='header-number')                    
                    ], id='yty-total-schools-div', className='stat-element')
                ], id='yty-header-row-2')
            ], id='yty-header-left'),
            html.Div([
                dcc.Link('Demographics', href='/demographics', className='link-button'),
                dcc.Link('Services', href='/services', className='link-button'),                
                dcc.Link('Analytics', href='/analytics', className='link-button')
            ], id='yty-header-right')
        ], id='yty-full-header'),
        html.Div([
            html.H4('Filters: ', id='yty-filter-title'),
            dcc.Store(id='yty-filter-store', data={}),
            html.Div(id='yty-active-filters')
        ], id='yty-filter-box'),
        html.Div([
            dcc.Graph(id='service-split-by-year', className='graph'),
            dcc.Graph(id='enrollment-count-by', className='graph')
        ], id='yty-first-row', className='graph-flex'),
        html.Div([
            html.Div([
                html.H5('Threshold (Hours): ', id='yty-threshold-title'),
                html.H5(id='yty-threshold-value'),
                dcc.Slider(
                    id='yty-slider',
                    min=0,
                    max=50,
                    step=1,
                    value=0,
                    marks={i: f'{i}' for i in range(0, 51, 5)}
                ),
                html.Hr(className='hr-line'),
                dcc.Checklist(
                    id='yty-year-checklist',
                    options=years,
                    value=years,
                    inline=False
                ),
                html.Hr(className='hr-line'),
                html.Div([
                    dcc.Checklist(
                        id='yty-service-type-filter',
                        options=service_types,
                        value=service_types,
                        inline=False
                    )     
                ], id='yty-service-type-div')           
            ], id='yty-service-filters'),
            dcc.Graph(id='service-participation-by-month', className='graph')
        ], id='yty-second-row', className='graph-flex'),
        html.Div([
            dcc.Graph(id='average-service-time-by-month', className='graph')
        ], id='yty-third-row', className='graph-flex')
    ])

def analytics_layout(AY_df):
    return html.Div([
        html.H2('Analytics'),
        dcc.Link('Demographics', href='/demographics', className='link-button'),
        dcc.Link('Services', href='/services', className='link-button'),
        dcc.Link('Year to Year', href='/yty', className='link-button')
    ])