from dash import Input, Output, State, html, dcc, no_update, ctx, ALL
import pandas as pd
import charts
import components

service_types = ['Tutoring/Homework Assistance', 'Mentoring', 'Financial Aid Counseling/Advising', 'Counseling/Advising', 'College Visit', 'Job Site Visit/Job Shadowing', 'Summer Programs', 'Educational Field Trips', 'Student Workshops', 'Parent/Family Workshops', 'Family Counseling/ Advising', 'Family College Visit', 'Other Family Events']

def get_demographics_page(AY):
    enrollment_by_locale = charts.get_enrollment_by_locale(AY)
    enrollment_by_gender = charts.get_enrollment_by_gender(AY)
    enrollment_by_ethnicity = charts.get_enrollment_by_ethnicity(AY)
    enrollment_by_grade = charts.get_enrollment_by_grade(AY)
    enrollment_by_race = charts.get_enrollment_by_race(AY)

    return components.get_demographics_layout(enrollment_by_locale, enrollment_by_gender, enrollment_by_ethnicity, enrollment_by_grade, enrollment_by_race)

def get_services_page(AY, threshold, services_type_filter):
    if not threshold:
        threshold = 0

    if not services_type_filter:
        services_type_filter = service_types

    participation_and_avg_time = charts.get_participation_and_avg_time(AY)
    participation_by_grade = charts.get_participation_by_grade(AY, threshold, services_type_filter)
    avg_time_by_grade = charts.get_service_time_by_grade(AY)

    return components.get_services_layout(threshold, service_types, services_type_filter, participation_and_avg_time, participation_by_grade, avg_time_by_grade)

def get_services_yty_page(AY, duration_by_student_month_type, agg_services_df, threshold, service_type_filter):
    if not threshold:
        threshold = 0

    if not service_type_filter:
        service_type_filter = service_types
        
    service_time_by_type_and_year = charts.get_y_t_y_service_time_by_type(AY)
    enrollment_by_year = charts.get_y_t_y_enrollments(AY)
    participation_by_month = charts.get_participation_by_month(AY, duration_by_student_month_type, threshold, service_type_filter)
    hours_per_student_by_month = charts.get_hours_per_student_by_month(AY, agg_services_df, service_type_filter)

    return components.get_yty_layout(threshold, service_types, service_type_filter, service_time_by_type_and_year, enrollment_by_year, participation_by_month, hours_per_student_by_month)

def get_objective_page(AY):
    return(html.H1('WORK IN PROGESS'))

def get_objective_yty_page(AY):
    return(html.H1('WORK IN PROGESS'))

def get_compare_page(AY):
    return(html.H1('WORK IN PROGESS'))

def register_callbacks(app, AY_df: pd.DataFrame, agg_services_df: pd.DataFrame, duration_by_student_month_type: pd.DataFrame):
    @app.callback(
        [Output('page-contents', 'children'),
         Output('page-title', 'children'),
         Output('total-service-hours', 'children'),
         Output('total-students', 'children'),
         Output('total-schools', 'children'),
         Output('current-page', 'data'),
         Output('active-filters', 'children'),
         Output('filter-store', 'data')],

        [Input('year-filter', 'value'),
         Input('demographics-btn', 'n_clicks'),
         Input('services-btn', 'n_clicks'),
         Input('services-yty-btn', 'n_clicks'),
         Input('objectives-btn', 'n_clicks'),
         Input('objectives-yty-btn', 'n_clicks'),
         Input('compare-btn', 'n_clicks'),
        
         Input('enrollment-by-locale', 'clickData', allow_optional=True),
         Input('enrollment-by-gender', 'clickData', allow_optional=True),
         Input('enrollment-by-ethnicity', 'clickData', allow_optional=True),
         Input('enrollment-by-grade', 'clickData', allow_optional=True),
         Input('enrollment-by-race', 'clickData', allow_optional=True),
         Input({'type': 'remove-filter-btn', 'key': ALL}, 'n_clicks'),

         Input('services-time-slider', 'value', allow_optional=True),
         Input('services-type-filter', 'value', allow_optional=True),
         Input('yty-time-slider', 'value', allow_optional=True),
         Input('yty-type-filter', 'value', allow_optional=True)],
        
        State('filter-store', 'data'),
        State('current-page', 'data')
    )
    def update_page(selected_year, demographics_btn, services_btn, services_yty_btn, objectives_btn, objectives_yty_btn, combare_btn, locale_click, gender_click, ethnicity_click, grade_click, race_click, remove_clicks, services_threshold, services_type_filter, yty_threshold, yty_type_filter, active_filters, current_page):
        
        trigger = ctx.triggered_id
        filters = active_filters.copy()

        if isinstance(trigger, dict) and trigger.get('type') == 'remove-filter-btn':
            remove_key = trigger['key']
            filters.pop(remove_key, None)
        elif trigger == 'enrollment-by-locale' and locale_click:
            filters['Locale'] = locale_click['points'][0]['y']
        elif trigger == 'enrollment-by-gender' and gender_click:
            filters['Gender Code'] = gender_click['points'][0]['label']
        elif trigger == 'enrollment-by-ethnicity' and ethnicity_click:
            filters['Ethnicity Code'] = ethnicity_click['points'][0]['label']        
        elif trigger == 'enrollment-by-grade' and grade_click:
            filters['Grade Level'] = str(grade_click['points'][0]['x'])
        elif trigger == 'enrollment-by-race' and race_click:
            filters['Race Code'] = race_click['points'][0]['y']

        if trigger == 'demographics-btn':
            page = 'demographics'
        elif trigger == 'services-btn':
            page = 'services'
        elif trigger == 'services-yty-btn':
            page = 'services-yty'
        elif trigger == 'objectives-btn':
            page = 'objectives'
        elif trigger == 'objectives-yty-btn':
            page = 'objectives-yty'
        elif trigger == 'compare-btn':
            page = 'compare'
        else: page = current_page

        filtered_AY = AY_df.copy()
        filtered_AY = filtered_AY[filtered_AY['High School AY'] == selected_year]
        for key, val in filters.items():
            filtered_AY = filtered_AY[filtered_AY[key] == val]

        match page:
            case 'demographics':
                contents = get_demographics_page(filtered_AY)
                page_lable = 'Demographics'
            case 'services':
                contents = get_services_page(filtered_AY, services_threshold, services_type_filter)
                page_lable = 'Services'
            case 'services-yty':
                contents = get_services_yty_page(AY_df.copy(), duration_by_student_month_type.copy(), agg_services_df.copy(), yty_threshold, yty_type_filter)
                page_lable = 'Services YTY'
            case 'objectives':
                contents = get_objective_page(filtered_AY)
                page_lable = 'Objectives'
            case 'objectives-yty':
                contents = get_objective_yty_page(filtered_AY)
                page_lable = 'Objectives YTY'
            case 'compare':
                contents = get_compare_page(filtered_AY)
                page_lable = 'compare'

        service_columns = ['Tutoring/Homework Assistance', 'Mentoring', 'Financial Aid Counseling/Advising', 'Counseling/Advising', 'College Visit', 'Job Site Visit/Job Shadowing', 'Summer Programs', 'Educational Field Trips', 'Student Workshops', 'Parent/Family Workshops', 'Family Counseling/ Advising', 'Family College Visit', 'Other Family Events']
        total_hours = round(filtered_AY[service_columns].sum().sum()/60, 2)
        total_students = len(filtered_AY)
        total_schools = len(filtered_AY[filtered_AY['School NCES ID'] != '000099999999']['School NCES ID'].drop_duplicates())

        filter_tags = []
        for key, value in filters.items():
            filter_tags.append(
                html.Span([
                    f'{key} = {value}',
                    html.Button('x', id={'type': 'remove-filter-btn', 'key': key}, n_clicks=0)
                ], id='filter-buttons')
            )

        return contents, f'CCREC Grant Level Dashboard: {page_lable}', total_hours, total_students, total_schools, page, filter_tags, filters

     