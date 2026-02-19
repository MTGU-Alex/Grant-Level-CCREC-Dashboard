from dash import Input, Output, State, html, dcc, no_update, ctx, ALL
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import components

temp_csv = '\\\\stella.msu.montana.edu\\GearUp\\20. Data Analysis\\CCREC Dashboard\\temp.csv'

load_demographics_filter = False
load_service_filters = False
load_yty_filters = False

month_map = {
    1: 'Jan',
    2: 'Feb',
    3: 'Mar',
    4: 'Apr',
    5: 'May',
    6: 'Jun',
    7: 'Jul',
    8: 'Aug',
    9: 'Sep',
    10: 'Oct',
    11: 'Nov',
    12: 'Dec'
}

def register_callbacks(app, AY_df, agg_services_df, duration_by_student_month_type):
    @app.callback(
        Output('page-content', 'children'),
        Output('temp-demographics-filter-store', 'data'),
        Output('temp-services-filter-store', 'data'),
        Output('temp-yty-filter-store', 'data'),
        Input('url', 'pathname'),
        State('demographics-filter-store', 'data', allow_optional=True),
        State('services-filter-store', 'data', allow_optional=True),
        State('yty-filter-store', 'data', allow_optional=True)
    )
    def display_page(pathname, demographics_filters, services_filters, yty_filters):
        global load_demographics_filter
        global load_service_filters
        global load_yty_filters

        if not demographics_filters and not services_filters and not yty_filters:
            current_filters = {}
        elif demographics_filters:
            current_filters = demographics_filters.copy()
        elif services_filters:
            current_filters = services_filters.copy()
        elif yty_filters:
            current_filters = yty_filters.copy()
        else:
            current_filters = {}

        if pathname == '/demographics':
            load_demographics_filter = True
            return components.demographics_layout(AY_df), current_filters, no_update, no_update
        elif pathname == '/services':
            load_service_filters = True
            return components.services_layout(AY_df), no_update, current_filters, no_update
        elif pathname == '/yty':
            load_yty_filters = True
            return components.year_to_year_layout(AY_df), no_update, no_update, current_filters
        elif pathname == '/analytics':
            return components.analytics_layout(AY_df), no_update, no_update, no_update
        else: return components.demographics_layout(AY_df), no_update, no_update, no_update

    @app.callback(
        [Output('enrollment-by-locale', 'figure'),
         Output('enrollment-by-gender-fig', 'figure'),
         Output('enrollment-by-ethnicity-fig', 'figure'),
         Output('enrollment-by-grade-level-fig', 'figure'),
         Output('enrollment-by-race-fig', 'figure'),
         Output('demographics-total-service-hours', 'children'),
         Output('demographics-total-students', 'children'),
         Output('demographics-total-schools', 'children'),
         Output('demographics-active-filters', 'children'),
         Output('demographics-filter-store', 'data')],

        [Input('demographics-year-filter', 'value'),
         Input('enrollment-by-locale', 'clickData'),
         Input('enrollment-by-gender-fig', 'clickData'),
         Input('enrollment-by-ethnicity-fig', 'clickData'),
         Input('enrollment-by-grade-level-fig', 'clickData'),
         Input('enrollment-by-race-fig', 'clickData')] + 
        [Input({'type': 'demographics-remove-filter-btn', 'key': ALL}, 'n_clicks')],

        State('demographics-filter-store', 'data', allow_optional=True),
        State('temp-demographics-filter-store', 'data', allow_optional=True)
    )
    def update_demographics_page(selected_year, locale_click, gender_click, ethnicity_click, grade_click, race_click, remove_clicks, active_filters, temp_filters):
        global load_demographics_filter
        trigger = ctx.triggered_id
        filters = active_filters.copy()

        if temp_filters and len(active_filters) == 0 and load_demographics_filter:
            filters = temp_filters.copy()
            temp_filters = {}
            load_demographics_filter = False

        # Checking clicks for filter or unfiltering data
        if isinstance(trigger, dict) and trigger.get('type') == 'demographics-remove-filter-btn':
            removed_key = trigger['key']
            filters.pop(removed_key, None)

        elif trigger == 'enrollment-by-locale' and locale_click:
            filters['Locale'] = locale_click['points'][0]['y']

        elif trigger == 'enrollment-by-gender-fig' and gender_click:
            filters['Gender Code'] = gender_click['points'][0]['label']

        elif trigger == 'enrollment-by-ethnicity-fig' and ethnicity_click:
            filters['Ethnicity Code'] = ethnicity_click['points'][0]['label']
        
        elif trigger == 'enrollment-by-grade-level-fig' and grade_click:
            filters['Grade Level'] = grade_click['points'][0]['x']

        elif trigger == 'enrollment-by-race-fig' and race_click:
            filters['Race Code'] = race_click['points'][0]['y']

        # Filtering data by active filters
        filtered_df = AY_df.copy()
        filtered_df = filtered_df[filtered_df['High School AY'] == selected_year]
        for key, val in filters.items():
            filtered_df = filtered_df[filtered_df[key] == val]

        # Getting header numbers
        service_columns = ['Tutoring/Homework Assistance', 'Mentoring', 'Financial Aid Counseling/Advising', 'Counseling/Advising', 'College Visit', 'Job Site Visit/Job Shadowing', 'Summer Programs', 'Educational Field Trips', 'Student Workshops', 'Parent/Family Workshops', 'Family Counseling/ Advising', 'Family College Visit', 'Other Family Events']
        total_hours = round(filtered_df[service_columns].sum().sum()/60, 2)
        total_students = len(filtered_df)
        total_schools = len(filtered_df[filtered_df['School NCES ID'] != '000099999999']['School NCES ID'].drop_duplicates())

        # Creating Charts from filtered data
        enrollment_by_locale = filtered_df.groupby('Locale').size().to_frame('Student Count').reset_index().sort_values('Student Count')
        locale_fig = px.bar(enrollment_by_locale, y='Locale', x='Student Count', text=enrollment_by_locale['Student Count']).update_layout(paper_bgcolor="#E5E5E5", plot_bgcolor='lightgrey')
        
        enrollemnt_by_gender = filtered_df.groupby('Gender Code').size().to_frame('Gender Count').reset_index()
        gender_fig = px.pie(enrollemnt_by_gender, names='Gender Code', values='Gender Count', title='Enrollment by Gender').update_layout(paper_bgcolor="#E5E5E5").update_traces(textinfo='value+percent')
        
        enrollment_by_ethnicity = filtered_df.groupby('Ethnicity Code').size().to_frame('Ethnicity Count').reset_index()
        ethnicity_fig = px.pie(enrollment_by_ethnicity, names='Ethnicity Code', values='Ethnicity Count', title='Enrollment by Ethnicity').update_layout(paper_bgcolor="#E5E5E5").update_traces(textinfo='value+percent')

        enrollment_by_grade = filtered_df.groupby('Grade Level').size().to_frame('Enrollment Count').reset_index()
        enrollment_by_grade.sort_values('Grade Level', key=lambda x: x.map({grade: int(grade) for grade in enrollment_by_grade['Grade Level'].drop_duplicates().to_list()}), inplace=True)
        grade_fig = px.bar(enrollment_by_grade, x='Grade Level', y='Enrollment Count', text=enrollment_by_grade['Enrollment Count']).update_layout(paper_bgcolor="#E5E5E5", plot_bgcolor='lightgrey')

        enrollment_by_race = filtered_df.groupby('Race Code').size().to_frame('Race Count').reset_index().sort_values('Race Count')
        race_fig = px.bar(enrollment_by_race, y='Race Code', x='Race Count', labels=({'Race Code': 'Race', 'Race Count': 'Enrollment Count'}), text=enrollment_by_race['Race Count']).update_layout(paper_bgcolor="#E5E5E5", plot_bgcolor='lightgrey')
        
        # Adding active filters as buttons 
        filter_tags = []
        for key, value in filters.items():
            filter_tags.append(
                html.Span([
                    f'{key} = {value}',
                    html.Button('x', id={'type': 'demographics-remove-filter-btn', 'key': key}, n_clicks=0)
                ], id='demographics-filter-buttons')
            )

        return locale_fig, gender_fig, ethnicity_fig, grade_fig, race_fig, total_hours, total_students, total_schools, filter_tags, filters
    
    @app.callback(
        [Output('services-participation', 'figure'),
         Output('service-participation-by-grade', 'figure'),
         Output('service-time-by-grade', 'figure'),
         Output('threshold-value', 'children'),
         Output('services-total-service-hours', 'children'),
         Output('services-total-students', 'children'),
         Output('services-total-schools', 'children'),
         Output('services-active-filters', 'children'),
         Output('services-filter-store', 'data')],

        [Input('services-year-filter', 'value'),
         Input('service-time-slider', 'value'),
         Input('service-type-filter', 'value')] + 
        [Input({'type': 'services-remove-filter-btn', 'key': ALL}, 'n_clicks')],

        State('services-filter-store', 'data', allow_optional=True),
        State('temp-services-filter-store', 'data', allow_optional=True)
    )
    def update_services_page(selected_year, participation_threshold, service_types, remove_clicks, active_filters, temp_filters):
        global load_service_filters
        trigger = ctx.triggered_id
        filters = active_filters.copy()

        if temp_filters and len(active_filters) == 0 and load_service_filters:
            filters = temp_filters.copy()
            temp_filters = {}
            load_service_filters = False
        
        # Checking clicks for filter or unfiltering data
        if isinstance(trigger, dict) and trigger.get('type') == 'services-remove-filter-btn':
            removed_key = trigger['key']
            filters.pop(removed_key, None)

        filtered_df = AY_df.copy()
        filtered_df = filtered_df[filtered_df['High School AY'] == selected_year]
        for key,val in filters.items():
            filtered_df = filtered_df[filtered_df[key] == val]
        
        service_columns = ['Tutoring/Homework Assistance', 'Mentoring', 'Financial Aid Counseling/Advising', 'Counseling/Advising', 'College Visit', 'Job Site Visit/Job Shadowing', 'Summer Programs', 'Educational Field Trips', 'Student Workshops', 'Parent/Family Workshops', 'Family Counseling/ Advising', 'Family College Visit', 'Other Family Events']
        total_hours = round(filtered_df[service_columns].sum().sum()/60, 2)
        total_students = len(filtered_df)
        total_schools = len(filtered_df[filtered_df['School NCES ID'] != '000099999999']['School NCES ID'].drop_duplicates())

        # Calculating participation and average duration for services
        for col in service_columns:
            num_non_zero = (filtered_df[col] != 0).sum()
            total_len = len(filtered_df)
            participation = round((num_non_zero/total_len)*100, 2)

            average_duration_mins = filtered_df[filtered_df[col] != 0][col].mean()
            average_duration_hours = round(average_duration_mins/60, 2)

            current_df = pd.DataFrame({'Service Type': [col], 'Participation': [participation], 'Average Hours': [average_duration_hours]})

            if 'service_df' not in locals():
                service_df = current_df
            else:
                service_df = pd.concat([service_df, current_df])

        service_df = service_df.sort_values('Participation')

        # Create subplot with 3 columns: left bars, middle label strip, right bars
        service_fig = make_subplots(subplot_titles=('Service Participation', '', 'Average Time Spent'),
            rows=1, cols=3,
            shared_yaxes=True,
            column_widths=[0.45, 0.125, 0.45],  # adjust middle strip width
            horizontal_spacing=0.02
        )

        # Left bars (negative values to flip direction)
        service_fig.add_trace(
            go.Bar(
                y=service_df['Service Type'],
                x=-service_df['Participation'],
                text=np.abs(service_df['Participation']).astype(str) + '%',
                hovertemplate="%{y}: %{text}<extra></extra>",
                orientation='h',
                marker_color='indianred',
                showlegend=False
            ),
            row=1, col=1
        )

        # Middle dummy plot (kept blank for labels)
        service_fig.add_trace(
            go.Bar(
                y=service_df['Service Type'],
                x=[0] * len(service_df),
                orientation='h',
                marker_color='white',
                hoverinfo='skip',
                showlegend=False
            ),
            row=1, col=2
        )

        # Right bars (positive values)
        service_fig.add_trace(
            go.Bar(
                y=service_df['Service Type'],
                x=service_df['Average Hours'],
                text=service_df['Average Hours'],
                orientation='h',
                marker_color='steelblue',
                showlegend=False
            ),
            row=1, col=3
        )

        # Add centered annotations for labels
        for label in service_df['Service Type']:
            service_fig.add_annotation(
                x=0.5,  # center of middle subplot
                y=label,
                text=label,
                showarrow=False,
                xref="x2 domain",  # middle subplot's x-axis domain
                yref="y2",         # middle subplot's y-axis
                font=dict(size=14, color="black", family="Arial", weight="bold"),
                align="center"
            )

        # Hide default y-axis labels for all subplots
        service_fig.update_yaxes(showticklabels=False)

        # Hide the middle subplot's x-axis completely
        service_fig.update_xaxes(visible=False, row=1, col=2)

        # Layout tweaks
        service_fig.update_layout(
            barmode="overlay",
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor="#E5E5E5",
            plot_bgcolor='#E5E5E5'
        )

        # Correcting left chart's x axis
        max_val = service_df['Participation'].max()
        next_10_multiplier = max_val//10 + 1
        left_axis = service_fig.layout.xaxis
        ticks = left_axis.tickvals if left_axis.tickvals else [-num*10 for num in range(1, int(next_10_multiplier))]
        
        service_fig.update_xaxes(
            tickvals=ticks,
            ticktext=[abs(v) for v in ticks],
            row=1, col=1
        )

        # CREATING service-participation-by-grade
        filtered_df['Total Service Time'] = filtered_df[service_types].sum(axis=1)/60
        students_per_grade = filtered_df.groupby('Grade Level').size().to_frame('Enrollment Count').reset_index()
        if participation_threshold == 0:
            filtered_df_for_participation = filtered_df[filtered_df['Total Service Time'] != 0]
        else:
            filtered_df_for_participation = filtered_df[filtered_df['Total Service Time'] >= participation_threshold]
        student_participation_count_by_grade = filtered_df_for_participation.groupby('Grade Level').size().to_frame('Service Participation').reset_index()
        enrollment_and_participation = students_per_grade.merge(student_participation_count_by_grade, how='left', on='Grade Level').fillna(0)
        participation_by_grade_fig = go.Figure(data=[
            go.Bar(name='Service Participation', x=enrollment_and_participation['Grade Level'], y=enrollment_and_participation['Service Participation'], text=enrollment_and_participation['Service Participation']),
            go.Bar(name='Enrollment Count', x=enrollment_and_participation['Grade Level'], y=enrollment_and_participation['Enrollment Count'], text=enrollment_and_participation['Enrollment Count'])
        ])
        participation_by_grade_fig.update_layout(barmode='group', 
            xaxis_title='Grade Level', 
            yaxis_title='Student Count', 
            title='Student Participation by Grade', 
            paper_bgcolor="#E5E5E5", 
            plot_bgcolor='lightgrey',
            legend=dict(
                x=1,   # position horizontally (0=left, 1=right)
                y=1.25,   # position vertically (0=bottom, 1=top)
                xanchor="right",  # anchor relative to x
                yanchor="top",    # anchor relative to y
                bgcolor="rgba(255,255,255,0.6)",  # optional: semi-transparent background
                bordercolor="black",
                borderwidth=1
                )
            )   

        # CREATING service-time-by-grade
        average_time_per_grade = filtered_df.groupby('Grade Level')['Total Service Time'].mean().to_frame('Average Service Time').reset_index()
        average_time_per_grade_fig = px.bar(average_time_per_grade, x='Grade Level', y='Average Service Time', text=round(average_time_per_grade['Average Service Time'], 2)).update_layout(title='Average Service Time per Student by Grade', paper_bgcolor="#E5E5E5", plot_bgcolor='lightgrey')

        # Adding active filters as buttons 
        filter_tags = []
        for key, value in filters.items():
            filter_tags.append(
                html.Span([
                    f'{key} = {value}',
                    html.Button('x', id={'type': 'services-remove-filter-btn', 'key': key}, n_clicks=0)
                ], id='services-filter-buttons')
            )

        return service_fig, participation_by_grade_fig, average_time_per_grade_fig, participation_threshold, total_hours, total_students, total_schools, filter_tags, filters

    @app.callback(
        [Output('yty-total-service-hours', 'children'),
         Output('yty-total-students', 'children'),
         Output('yty-total-schools', 'children'),
         Output('enrollment-count-by', 'figure'),
         Output('service-split-by-year', 'figure'),
         Output('service-participation-by-month', 'figure'),
         Output('average-service-time-by-month', 'figure'),
         Output('yty-threshold-value', 'children'),
         Output('yty-active-filters', 'children'),
         Output('yty-filter-store', 'data')],

        [Input('yty-year-filter', 'value'),
         Input('yty-slider', 'value'),
         Input('yty-year-checklist', 'value'),
         Input('yty-service-type-filter', 'value')] + 
        [Input({'type': 'yty-remove-filter-btn', 'key': ALL}, 'n_clicks')],

        State('yty-filter-store', 'data', allow_optional=True),
        State('temp-yty-filter-store', 'data', allow_optional=True)        
    )
    def update_yty_page(selected_year, participation_threshold, year_list, service_type_list, remove_clicks, active_filters, temp_filters):
        global load_yty_filters
        trigger = ctx.triggered_id
        filters = active_filters.copy()
        year_list.sort()

        if temp_filters and len(active_filters) == 0 and load_yty_filters:
            filters = temp_filters.copy()
            temp_filters = {}
            load_yty_filters = False

        # checking clicks for filter or unfiltering data
        if isinstance(trigger, dict) and trigger.get('type') == 'yty-remove-filter-btn':
            removed_key = trigger['key']
            filters.pop(removed_key, None)

        filtered_df = AY_df.copy()
        for key,val in filters.items():
            filtered_df = filtered_df[filtered_df[key] == val]

        service_columns = ['Tutoring/Homework Assistance', 'Mentoring', 'Financial Aid Counseling/Advising', 'Counseling/Advising', 'College Visit', 'Job Site Visit/Job Shadowing', 'Summer Programs', 'Educational Field Trips', 'Student Workshops', 'Parent/Family Workshops', 'Family Counseling/ Advising', 'Family College Visit', 'Other Family Events']
        total_hours = round(filtered_df[service_columns].sum().sum()/60, 2)
        total_students = len(filtered_df)
        total_schools = len(filtered_df[filtered_df['School NCES ID'] != '000099999999']['School NCES ID'].drop_duplicates())

        enrollment_by_year = filtered_df.groupby('High School AY').size().to_frame('Students').reset_index()
        enrollment_by_year_fig = px.bar(enrollment_by_year, x='High School AY', y='Students', labels={'High School AY': 'School Year'}, text=enrollment_by_year['Students'], title='Enrollment Count by Year').update_layout(paper_bgcolor="#E5E5E5", plot_bgcolor='lightgrey')

        service_time_by_type_and_year = filtered_df.groupby('High School AY')[service_columns].sum().reset_index()
        service_time_by_type_and_year['Total Service Mins'] = service_time_by_type_and_year[service_columns].sum(axis=1)
        for col in service_columns:
            percent_col = col + ' Percentage'
            service_time_by_type_and_year[percent_col] = round((service_time_by_type_and_year[col]/service_time_by_type_and_year['Total Service Mins']*100), 5)
        service_percent_columns = [col + ' Percentage' for col in service_columns]
        service_time_by_type_and_year = service_time_by_type_and_year[['High School AY'] + service_percent_columns]

        melted_service_time_by_type_and_year = service_time_by_type_and_year.melt(
            id_vars='High School AY',
            value_vars=service_percent_columns,
            var_name='Service Type',
            value_name='Percent'
        )

        service_type_times = melted_service_time_by_type_and_year.groupby('Service Type')['Percent'].sum().to_frame('Percentage Sum').reset_index()
        service_type_times.sort_values(by='Percentage Sum', ascending=False, inplace=True)
        service_type_order = service_type_times['Service Type'].to_list()

        service_type_by_year_fig = px.bar(melted_service_time_by_type_and_year,
            x='High School AY',
            y='Percent',
            color='Service Type',
            category_orders={'Service Type': service_type_order},
            title='Percentage of Time Spent by Service Category'
        ).update_layout(barmode='stack', paper_bgcolor="#E5E5E5", plot_bgcolor='lightgrey', margin=dict(pad=0, t=40))

        students_per_year = AY_df.groupby('High School AY').size().to_frame('Student Count').reset_index()
        students_per_year = students_per_year[students_per_year['High School AY'].isin(year_list)]
        month_order = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        months_df = pd.DataFrame({'Month': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]})
        students_per_month = students_per_year.merge(months_df, how='cross')
        
        filtered_duration_by_month_student = duration_by_student_month_type[(duration_by_student_month_type['High School AY'].isin(year_list)) & (duration_by_student_month_type['Service Type Code'].isin(service_type_list))]
        duration_by_month_student = filtered_duration_by_month_student.groupby(['High School AY', 'Month', 'National CCREC Student ID'])['Total Time'].sum().reset_index()
        duration_by_month_student['Total Time'] = duration_by_month_student['Total Time']/60
        if participation_threshold == 0:
            filtered_duration_by_month_student = duration_by_month_student
        else:
            filtered_duration_by_month_student = duration_by_month_student[duration_by_month_student['Total Time'] >= participation_threshold]
        participation_count_by_month = filtered_duration_by_month_student.groupby(['High School AY', 'Month'])['National CCREC Student ID'].nunique().reset_index().rename(columns={'National CCREC Student ID': 'Student Participation Count'})
        participation_by_month_with_enrollment = participation_count_by_month.merge(students_per_month, how='right', on=['High School AY', 'Month']).fillna(0)
        participation_by_month_with_enrollment['Participation Percent'] = round((participation_by_month_with_enrollment['Student Participation Count']/participation_by_month_with_enrollment['Student Count'])*100, 2)
        participation_by_month_with_enrollment['Month'] = participation_by_month_with_enrollment['Month'].map(month_map)
        participation_by_month_with_enrollment['Month'] = pd.Categorical(participation_by_month_with_enrollment['Month'], categories=month_order, ordered=True)
        participation_by_month_with_enrollment.sort_values('Month', inplace=True)
        participation_by_month_fig = px.line(participation_by_month_with_enrollment,
            x='Month',
            y='Participation Percent',
            color='High School AY',
            markers=True,
            title='Service Participation Percentage by Month',
            category_orders={
                'High School AY': year_list
            }
        ).update_layout(paper_bgcolor="#E5E5E5", plot_bgcolor='lightgrey', margin=dict(pad=0, t=40))

        filtered_aggregate_services = agg_services_df[(agg_services_df['High School AY'].isin(year_list)) & (agg_services_df['Service Type Code'].isin(service_type_list))]
        total_service_mins_per_month = filtered_aggregate_services.groupby(['High School AY', 'Month'])['Total Minutes'].sum().reset_index()   
        service_mins_with_student_count = total_service_mins_per_month.merge(students_per_month, how='right', on=['High School AY', 'Month']).fillna(0)
        service_mins_with_student_count['Hours per Student'] = round((service_mins_with_student_count['Total Minutes']/service_mins_with_student_count['Student Count'])/60, 2)
        service_mins_with_student_count['Month'] = service_mins_with_student_count['Month'].map(month_map)
        service_mins_with_student_count['Month'] = pd.Categorical(service_mins_with_student_count['Month'], categories=month_order, ordered=True)
        service_mins_with_student_count.sort_values('Month', inplace=True)
        average_service_mins_by_month_fig = px.line(service_mins_with_student_count,
            x='Month',
            y='Hours per Student',
            color='High School AY',
            markers=True,
            title='Average Service Hours per Student by Month',
            category_orders={
                'High School AY': year_list
            }
        ).update_layout(paper_bgcolor="#E5E5E5", plot_bgcolor='lightgrey', margin=dict(pad=0, t=40))

        filter_tags = []
        for key, value in filters.items():
            filter_tags.append(
                html.Span([
                    f'{key} = {value}',
                    html.Button('x', id={'type': 'yty-remove-filter-btn', 'key': key}, n_clicks=0)
                ], id='yty-filter-buttons')
            )

        return total_hours, total_students, total_schools, enrollment_by_year_fig, service_type_by_year_fig, participation_by_month_fig, average_service_mins_by_month_fig, participation_threshold, filter_tags, filters