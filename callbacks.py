from dash import Input, Output, State, html, dcc, no_update, ctx, ALL
import pandas as pd
import charts
import components

service_types = ['Tutoring/Homework Assistance', 'Mentoring', 'Financial Aid Counseling/Advising', 'Counseling/Advising', 'College Visit', 'Job Site Visit/Job Shadowing', 'Summer Programs', 'Educational Field Trips', 'Student Workshops', 'Parent/Family Workshops', 'Family Counseling/ Advising', 'Family College Visit', 'Other Family Events']

def get_demographics_page(AY):
    enrollment_by_district = charts.get_enrollment_by_district(AY)
    enrollment_by_gender = charts.get_enrollment_by_gender(AY)
    enrollment_by_ethnicity = charts.get_enrollment_by_ethnicity(AY)
    enrollment_by_grade = charts.get_enrollment_by_grade(AY)
    enrollment_by_race = charts.get_enrollment_by_race(AY)

    return components.get_demographics_layout(enrollment_by_district, enrollment_by_gender, enrollment_by_ethnicity, enrollment_by_grade, enrollment_by_race)

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

def get_objectives_page(AY, college_visits, gpa_type, gpa_range, gpa_benchmark, sankey_l1_option, sankey_l2_option, sankey_l3_option, sankey_l4_option):

    if not sankey_l1_option:
        sankey_l1_option = 'FAFSA status code'
    
    if not gpa_range:
        gpa_low = 2
        gpa_high = 3
    else:
        gpa_low = gpa_range[0]
        gpa_high = gpa_range[1]

    if not gpa_type:
        gpa_type = 'Cumulative GPA'

    if not gpa_benchmark:
        gpa_benchmark = 2.5
        
    gpa_by_grade = charts.get_gpa_by_grade(AY, gpa_type, gpa_low, gpa_high, gpa_benchmark)
    alg1_by_grade = charts.get_alg1_by_grade(AY)
    fafsa_completion = charts.get_fafsa(AY)

    l1_options, l1_selection, l2_options, l2_selection, l3_options, l3_selection, l4_options, l4_selection, sankey = charts.get_sankey(AY, sankey_l1_option, sankey_l2_option, sankey_l3_option, sankey_l4_option)

    return components.get_objectives_layout(gpa_type, gpa_low, gpa_high, gpa_benchmark, gpa_by_grade, l1_options, l1_selection, l2_options, l2_selection, l3_options, l3_selection, l4_options, l4_selection, alg1_by_grade, fafsa_completion, sankey)

def get_objective_yty_page(AY, years, yty_gpa_radio, gpa_yty_benchmark_input, gpa_yty_increase_input, gpa_yty_benchmark_year, fafsa_yty_benchmark_input, fafsa_yty_increase_input, fafsa_yty_benchmark_year, graduation_yty_benchmark_input, graduation_yty_increase_input, graduation_yty_benchmark_year, pse_yty_benchmark_input, pse_yty_increase_input, pse_yty_benchmark_year):
    if not yty_gpa_radio:
        yty_gpa_radio = 'Cumulative GPA'
    
    avg_gpa_by_year = charts.get_yty_gpa(AY, years, yty_gpa_radio, yty_gpa_radio, gpa_yty_benchmark_input, gpa_yty_increase_input, gpa_yty_benchmark_year)
    fafsa_by_year = charts.get_yty_fafsa(AY, years, fafsa_yty_benchmark_input, fafsa_yty_increase_input, fafsa_yty_benchmark_year)
    graduation_by_year = charts.get_yty_graduation(AY, years, graduation_yty_benchmark_input, graduation_yty_increase_input, graduation_yty_benchmark_year)
    pse_by_year = charts.get_yty_pse(AY, years, pse_yty_benchmark_input, pse_yty_increase_input, pse_yty_benchmark_year)

    return components.get_objectives_yty_layout(yty_gpa_radio, gpa_yty_benchmark_input, gpa_yty_increase_input, gpa_yty_benchmark_year, fafsa_yty_benchmark_input, fafsa_yty_increase_input, fafsa_yty_benchmark_year, graduation_yty_benchmark_input, graduation_yty_increase_input, graduation_yty_benchmark_year, pse_yty_benchmark_input, pse_yty_increase_input, pse_yty_benchmark_year, years, avg_gpa_by_year, fafsa_by_year, graduation_by_year, pse_by_year)

def get_compare_page(AY: pd.DataFrame, current_district, compare_range_slider):
    district_list = AY['District'].drop_duplicates().to_list()

    if not current_district:
        current_district = sorted(district_list)[0]

    if not compare_range_slider:
        range_low = 5
        range_high = 10
    else:
        range_low = compare_range_slider[0]
        range_high = compare_range_slider[1]

    district_AY = AY[AY['District'] == current_district]

    district_services_time_split = charts.get_service_time_pie(district_AY, f'Service Time by category - {current_district}')
    program_services_time_split = charts.get_service_time_pie(AY, f'Service Time by category - Program Wide')
    service_participation_compare = charts.get_service_participation_compare(AY, district_AY, range_low, range_high)
    objective_compare = charts.get_blank_fig()

    return components.get_compare_layout(district_list, current_district, range_low, range_high, district_services_time_split, program_services_time_split, service_participation_compare, objective_compare)

def register_callbacks(app, AY_df: pd.DataFrame, agg_services_df: pd.DataFrame, duration_by_student_month_type: pd.DataFrame, college_visits: pd.DataFrame):
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
        
         Input('enrollment-by-district', 'clickData', allow_optional=True),
         Input('enrollment-by-gender', 'clickData', allow_optional=True),
         Input('enrollment-by-ethnicity', 'clickData', allow_optional=True),
         Input('enrollment-by-grade', 'clickData', allow_optional=True),
         Input('enrollment-by-race', 'clickData', allow_optional=True),
         Input({'type': 'remove-filter-btn', 'key': ALL}, 'n_clicks'),

         Input('services-time-slider', 'value', allow_optional=True),
         Input('services-type-filter', 'value', allow_optional=True),
         Input('yty-time-slider', 'value', allow_optional=True),
         Input('yty-type-filter', 'value', allow_optional=True),

         Input('district-dropdown', 'value', allow_optional=True),
         Input('compare-service-ranges', 'value', allow_optional=True),
         
         Input('gpa-radio', 'value', allow_optional=True),
         Input('gpa-range-slider', 'value', allow_optional=True),
         Input('gpa-benchmark-slider', 'value', allow_optional=True),
         Input('sankey-l1-dropdown', 'value', allow_optional=True),
         Input('sankey-l2-dropdown', 'value', allow_optional=True),
         Input('sankey-l3-dropdown', 'value', allow_optional=True),
         Input('sankey-l4-dropdown', 'value', allow_optional=True),
         Input('graduation-and-pse', 'clickData', allow_optional=True),
         
         Input('yty-gpa-radio', 'value', allow_optional=True),
         Input('gpa-yty-benchmark-input', 'value', allow_optional=True),
         Input('gpa-yty-increase-input', 'value', allow_optional=True),
         Input('gpa-yty-benchmark-year', 'value', allow_optional=True),
         Input('fafsa-yty-benchmark-input', 'value', allow_optional=True),
         Input('fafsa-yty-increase-input', 'value', allow_optional=True),
         Input('fafsa-yty-benchmark-year', 'value', allow_optional=True),
         Input('graduation-yty-benchmark-input', 'value', allow_optional=True),
         Input('graduation-yty-increase-input', 'value', allow_optional=True),
         Input('graduation-yty-benchmark-year', 'value', allow_optional=True),
         Input('pse-yty-benchmark-input', 'value', allow_optional=True),
         Input('pse-yty-increase-input', 'value', allow_optional=True),
         Input('pse-yty-benchmark-year', 'value', allow_optional=True)],
        
        State('filter-store', 'data'),
        State('current-page', 'data')
    )
    def update_page(selected_year, demographics_btn, services_btn, services_yty_btn, objectives_btn, objectives_yty_btn, combare_btn, district_click, gender_click, ethnicity_click, grade_click, race_click, remove_clicks, services_threshold, services_type_filter, yty_threshold, yty_type_filter, current_district, compare_range_slider, gpa_type, gpa_range, gpa_benchmark, sankey_l1_option, sankey_l2_option, sankey_l3_option, sankey_l4_option, sankey_click, yty_gpa_radio, gpa_yty_benchmark_input, gpa_yty_increase_input, gpa_yty_benchmark_year, fafsa_yty_benchmark_input, fafsa_yty_increase_input, fafsa_yty_benchmark_year, graduation_yty_benchmark_input, graduation_yty_increase_input, graduation_yty_benchmark_year, pse_yty_benchmark_input, pse_yty_increase_input, pse_yty_benchmark_year, active_filters, current_page):
        trigger = ctx.triggered_id
        filters = active_filters.copy()

        if isinstance(trigger, dict) and trigger.get('type') == 'remove-filter-btn':
            remove_key = trigger['key']
            filters.pop(remove_key, None)
        elif trigger == 'enrollment-by-district' and district_click:
            filters['District'] = district_click['points'][0]['x']
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
        for key, val in filters.items():
            filtered_AY = filtered_AY[filtered_AY[key] == val]

        filtered_AY_with_year = filtered_AY[filtered_AY['High School AY'] == selected_year]

        match page:
            case 'demographics':
                contents = get_demographics_page(filtered_AY_with_year)
                page_lable = 'Demographics'
            case 'services':
                contents = get_services_page(filtered_AY_with_year, services_threshold, services_type_filter)
                page_lable = 'Services'
            case 'services-yty':
                contents = get_services_yty_page(filtered_AY, duration_by_student_month_type.copy(), agg_services_df.copy(), yty_threshold, yty_type_filter)
                page_lable = 'Services YTY'
            case 'objectives':
                contents = get_objectives_page(filtered_AY_with_year, college_visits, gpa_type, gpa_range, gpa_benchmark, sankey_l1_option, sankey_l2_option, sankey_l3_option, sankey_l4_option)
                page_lable = 'Objectives'
            case 'objectives-yty':
                contents = get_objective_yty_page(filtered_AY, AY_df['High School AY'].drop_duplicates().to_list(), yty_gpa_radio, gpa_yty_benchmark_input, gpa_yty_increase_input, gpa_yty_benchmark_year, fafsa_yty_benchmark_input, fafsa_yty_increase_input, fafsa_yty_benchmark_year, graduation_yty_benchmark_input, graduation_yty_increase_input, graduation_yty_benchmark_year, pse_yty_benchmark_input, pse_yty_increase_input, pse_yty_benchmark_year)
                page_lable = 'Objectives YTY'
            case 'compare':
                contents = get_compare_page(filtered_AY_with_year, current_district, compare_range_slider)
                page_lable = 'Compare'

        service_columns = ['Tutoring/Homework Assistance', 'Mentoring', 'Financial Aid Counseling/Advising', 'Counseling/Advising', 'College Visit', 'Job Site Visit/Job Shadowing', 'Summer Programs', 'Educational Field Trips', 'Student Workshops', 'Parent/Family Workshops', 'Family Counseling/ Advising', 'Family College Visit', 'Other Family Events']
        total_hours = round(filtered_AY_with_year[service_columns].sum().sum()/60, 2)
        total_students = len(filtered_AY_with_year)
        total_schools = len(filtered_AY_with_year[filtered_AY_with_year['School NCES ID'] != '000099999999']['School NCES ID'].drop_duplicates())

        filter_tags = []
        for key, value in filters.items():
            filter_tags.append(
                html.Span([
                    f'{key} = {value}',
                    html.Button('x', id={'type': 'remove-filter-btn', 'key': key}, n_clicks=0)
                ], id='filter-buttons')
            )

        return contents, f'CCREC Grant Level Dashboard: {page_lable}', total_hours, total_students, total_schools, page, filter_tags, filters