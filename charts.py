import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

# Setting global chart colors
mark_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728" ,"#9467bd" ,"#8c564b" ,"#e377c2" ,"#7f7f7f" ,"#bcbd22" ,"#17becf"]
pio.templates["my_theme"] = dict(
    layout=dict(
        paper_bgcolor="#E5E5E5",
        plot_bgcolor="lightgrey",
        font=dict(color="black"),
        colorway=mark_colors
    )
)
pio.templates.default = "my_theme"
benchmark_bar_color = 'SteelBlue'

# Static data
service_columns = ['Tutoring/Homework Assistance', 'Mentoring', 'Financial Aid Counseling/Advising', 'Counseling/Advising', 'College Visit', 'Job Site Visit/Job Shadowing', 'Summer Programs', 'Educational Field Trips', 'Student Workshops', 'Parent/Family Workshops', 'Family Counseling/ Advising', 'Family College Visit', 'Other Family Events']

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

def get_blank_fig():
    return px.bar()

# =======================
# == ENROLLMENT CHARTS ==
# =======================
def get_enrollment_by_district(AY: pd.DataFrame):
    enrollment_by_district = AY.groupby('District').size().to_frame('Student Count').reset_index().sort_values('Student Count')
    return px.bar(enrollment_by_district,
        x='District',
        y='Student Count',
        text_auto=True,
        title='Enrollment by District'
    ).update_xaxes(title_text="")

def get_enrollment_by_gender(AY: pd.DataFrame):
    enrollemnt_by_gender = AY.groupby('Gender Code').size().to_frame('Gender Count').reset_index()
    return px.pie(enrollemnt_by_gender,
        names='Gender Code', 
        values='Gender Count', 
        title='Enrollment by Gender'
    )

def get_enrollment_by_ethnicity(AY: pd.DataFrame):
    enrollment_by_ethnicity = AY.groupby('Ethnicity Code').size().to_frame('Ethnicity Count').reset_index()
    return px.pie(enrollment_by_ethnicity,
        names='Ethnicity Code', 
        values='Ethnicity Count', 
        title='Enrollment by Ethnicity'
    )
    
def get_enrollment_by_grade(AY: pd.DataFrame):
    enrollment_by_grade = AY.groupby('Grade Level').size().to_frame('Enrollment Count').reset_index()
    enrollment_by_grade['Grade Level'] = enrollment_by_grade['Grade Level'].astype('str')
    enrollment_by_grade.sort_values('Grade Level', key=lambda x: x.map({grade: int(grade) for grade in enrollment_by_grade['Grade Level'].drop_duplicates().to_list()}), inplace=True)
    return px.bar(enrollment_by_grade,
        x='Grade Level', 
        y='Enrollment Count', 
        text_auto=True,
        title='Enrollment By Grade'
    )

def get_enrollment_by_race(AY: pd.DataFrame):
    enrollment_by_race = AY.groupby('Race Code').size().to_frame('Race Count').reset_index().sort_values('Race Count')
    return px.bar(enrollment_by_race,
        y='Race Code', 
        x='Race Count', 
        labels=({'Race Code': 'Race', 'Race Count': 'Enrollment Count'}), 
        text_auto=True,
        title='Enrollment by Race'
    )

# =====================
# == SERVICES CHARTS ==
# =====================
def get_participation_and_avg_time(AY: pd.DataFrame):
    # Getting participation % and avg time spent by service type
    for col in service_columns:
        num_non_zero = (AY[col] != 0).sum()
        total_len = len(AY)
        if num_non_zero > 0:
            participation = round((num_non_zero/total_len)*100, 2)
        else:
            participation = 0

        average_duration_mins = AY[AY[col] != 0][col].mean()
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
    if type(max_val) == np.float64: 
        next_10_multiplier = max_val//10 + 1
        left_axis = service_fig.layout.xaxis
        ticks = left_axis.tickvals if left_axis.tickvals else [-num*10 for num in range(1, int(next_10_multiplier))]
        
        service_fig.update_xaxes(
            tickvals=ticks,
            ticktext=[abs(v) for v in ticks],
            row=1, col=1
        )

    return service_fig

def get_participation_by_grade(AY: pd.DataFrame, threshold, types):
    # Finding students and participants per grade (threshold taken into account)
    AY['Total Service Time'] = AY[types].sum(axis=1)/60
    students_per_grade = AY.groupby('Grade Level').size().to_frame('Students').reset_index()
    if threshold == 0 :
        filtered_df_for_participation = AY[AY['Total Service Time'] != 0]
    else:
        filtered_df_for_participation = AY[AY['Total Service Time'] >= threshold]
    student_participation_count_by_grade = filtered_df_for_participation.groupby('Grade Level').size().to_frame('Students').reset_index()
    
    # Combining and ordering enrollment and participation by grade
    students_per_grade['Group'] = 'Enrollment Count'
    student_participation_count_by_grade['Group'] = 'Service Participants'
    students_and_participats_by_grade = pd.concat([students_per_grade, student_participation_count_by_grade])
    students_and_participats_by_grade['Grade Level'] = students_and_participats_by_grade['Grade Level'].astype('str')
    students_and_participats_by_grade.sort_values('Grade Level', key=lambda x: x.map({grade: int(grade) for grade in students_and_participats_by_grade['Grade Level'].drop_duplicates().to_list()}), inplace=True)
    return px.bar(students_and_participats_by_grade,
        x='Grade Level',
        y='Students',
        color='Group',
        barmode='group',
        text_auto=True,
        title='Service Participation by Grade'
    )
    
def get_service_time_by_grade(AY: pd.DataFrame):
    avg_time_per_grade = AY.groupby('Grade Level')['Total Service Time'].mean().to_frame('Average Service Time').reset_index()
    avg_time_per_grade.sort_values('Grade Level', key=lambda x: x.map({grade: int(grade) for grade in avg_time_per_grade['Grade Level'].drop_duplicates().to_list()}), inplace=True)
    return px.bar(avg_time_per_grade,
        x='Grade Level',
        y='Average Service Time',
        text=round(avg_time_per_grade['Average Service Time'], 2),
        title='Average Service Time per Student by Grade'
    )

# ===========================
# == Y-T-Y SERVICES CHARTS ==
# ===========================
def get_y_t_y_service_time_by_type(AY: pd.DataFrame):
    # Getting percent of service time by type
    service_time_by_type_and_year = AY.groupby('High School AY')[service_columns].sum().reset_index()
    service_time_by_type_and_year['Total Service Mins'] = service_time_by_type_and_year[service_columns].sum(axis=1)
    for col in service_columns:
        percent_col = col + ' Percentage'
        service_time_by_type_and_year[percent_col] = round((service_time_by_type_and_year[col]/service_time_by_type_and_year['Total Service Mins']*100), 5)
    service_percent_columns = [col + ' Percentage' for col in service_columns]
    service_time_by_type_and_year = service_time_by_type_and_year[['High School AY'] + service_percent_columns]

    # Changing dataframe shape
    melted_service_time_by_type_and_year = service_time_by_type_and_year.melt(
        id_vars='High School AY',
        value_vars=service_percent_columns,
        var_name='Service Type',
        value_name='Percent'
    )

    # Ordering
    service_type_times = melted_service_time_by_type_and_year.groupby('Service Type')['Percent'].sum().to_frame('Percentage Sum').reset_index()
    service_type_times.sort_values(by='Percentage Sum', ascending=False, inplace=True)
    service_type_order = service_type_times['Service Type'].to_list()

    return px.bar(melted_service_time_by_type_and_year,
        x='High School AY',
        y='Percent',
        color='Service Type',
        category_orders={'Service Type': service_type_order},
        title='Percentage of Time Spent by Service Category'
    )

def get_y_t_y_enrollments(AY: pd.DataFrame):
    enrollment_by_year = AY.groupby('High School AY').size().to_frame('Students').reset_index()
    return px.bar(enrollment_by_year, 
        x='High School AY', 
        y='Students', 
        labels={'High School AY': 'School Year'}, 
        text_auto=True,
        title='Enrollment Count by Year'
    )

def get_participation_by_month(AY: pd.DataFrame, duration_by_student_month_type: pd.DataFrame, threshold, service_types):
    # Getting total student count by month
    students_per_year = AY.groupby('High School AY').size().to_frame('Student Count').reset_index()
    month_order = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    months_df = pd.DataFrame({'Month': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]})
    students_per_month = students_per_year.merge(months_df, how='cross')

    # Getting participation based on threshold
    filtered_duration_by_month_student = duration_by_student_month_type[duration_by_student_month_type['Service Type Code'].isin(service_types)]
    duration_by_month_student = filtered_duration_by_month_student.groupby(['High School AY', 'Month', 'National CCREC Student ID'])['Total Time'].sum().reset_index()
    duration_by_month_student['Total Time'] = duration_by_month_student['Total Time']/60
    if threshold == 0:
        filtered_duration_by_month_student = duration_by_month_student
    else:
        filtered_duration_by_month_student = duration_by_month_student[duration_by_month_student['Total Time'] >= threshold]

    # Calculating participation by month and ordering
    participation_count_by_month = filtered_duration_by_month_student.groupby(['High School AY', 'Month'])['National CCREC Student ID'].nunique().reset_index().rename(columns={'National CCREC Student ID': 'Student Participation Count'})
    participation_by_month_with_enrollment = participation_count_by_month.merge(students_per_month, how='right', on=['High School AY', 'Month']).fillna(0)
    participation_by_month_with_enrollment['Participation Percent'] = round((participation_by_month_with_enrollment['Student Participation Count']/participation_by_month_with_enrollment['Student Count'])*100, 2)
    participation_by_month_with_enrollment['Month'] = participation_by_month_with_enrollment['Month'].map(month_map)
    participation_by_month_with_enrollment['Month'] = pd.Categorical(participation_by_month_with_enrollment['Month'], categories=month_order, ordered=True)
    participation_by_month_with_enrollment.sort_values('Month', inplace=True)

    return px.line(participation_by_month_with_enrollment,
        x='Month',
        y='Participation Percent',
        color='High School AY',
        markers=True,
        title='Service Participation Percentage by Month'
    )

def get_hours_per_student_by_month(AY: pd.DataFrame, agg_services_df: pd.DataFrame, service_types):
    # Getting total students by month
    students_per_year = AY.groupby('High School AY').size().to_frame('Student Count').reset_index()
    month_order = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    months_df = pd.DataFrame({'Month': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]})
    students_per_month = students_per_year.merge(months_df, how='cross')

    # Getting hours per student by month
    filtered_aggregate_services = agg_services_df[ (agg_services_df['Service Type Code'].isin(service_types))]
    total_service_mins_per_month = filtered_aggregate_services.groupby(['High School AY', 'Month'])['Total Minutes'].sum().reset_index()   
    service_mins_with_student_count = total_service_mins_per_month.merge(students_per_month, how='right', on=['High School AY', 'Month']).fillna(0)
    service_mins_with_student_count['Hours per Student'] = round((service_mins_with_student_count['Total Minutes']/service_mins_with_student_count['Student Count'])/60, 2)
    service_mins_with_student_count['Month'] = service_mins_with_student_count['Month'].map(month_map)
    service_mins_with_student_count['Month'] = pd.Categorical(service_mins_with_student_count['Month'], categories=month_order, ordered=True)
    service_mins_with_student_count.sort_values('Month', inplace=True)

    return px.line(service_mins_with_student_count,
        x='Month',
        y='Hours per Student',
        color='High School AY',
        markers=True,
        title='Average Service Hours per Student by Month',
    )

# =======================
# == OBJECTIVES CHARTS ==
# =======================
def get_gpa_by_grade(AY: pd.DataFrame, gpa_type, gpa_low, gpa_high, gpa_benchmark):
    # Filtering AY dataframe
    gpas = AY[['Grade Level', gpa_type]]
    gpas = gpas[~gpas['Grade Level'].isin(['7', '8', '13'])]
    gpas[gpa_type] = gpas[gpa_type].fillna(9.99)
    
    # Setting GPA range based on slider
    conditions = [
        (gpas[gpa_type] <= gpa_low),
        ((gpas[gpa_type] > gpa_low) & (gpas[gpa_type] < gpa_high)),
        ((gpas[gpa_type] >= gpa_high) & (gpas[gpa_type] < 9))
    ]
    choices = [f'Low: <= {gpa_low}', f'Medium: > {gpa_low}; < {gpa_high}', f'High: >= {gpa_high}']
    gpas['GPA Range'] = np.select(conditions, choices, default='Unknown')
    
    # Calculating percent of studetns in each GPA range by grade
    gpa_range_counts = gpas.groupby(['Grade Level', 'GPA Range']).size().to_frame('Student Count').reset_index()
    gpa_range_counts['Percentage'] = gpa_range_counts.groupby('Grade Level')['Student Count'].transform(lambda x: round(x/x.sum()*100, 1))
    gpa_range_counts.sort_values('Grade Level', key=lambda x: x.map({grade: int(grade) for grade in gpa_range_counts['Grade Level'].drop_duplicates().to_list()}), inplace=True)

    # backup chart
    first_chart = px.bar(gpa_range_counts,
        x='Grade Level',
        y='Percentage',
        barmode='stack',
        color='GPA Range',
        title='GPA By Grade Level',
        category_orders={'GPA Range': [f'Low: <= {gpa_low}', f'Medium: > {gpa_low}; < {gpa_high}', f'High: >= {gpa_high}', 'Unknown']},
        text_auto=True
    ).update_traces(
        texttemplate='%{y}%'
    )

    # Getting avg GPA by grade and combining with 
    gpas_pivoted = gpa_range_counts.pivot(index='Grade Level', columns='GPA Range', values='Percentage').reset_index()
    avg_by_grade = gpas[gpas[gpa_type] != 9.99].groupby('Grade Level')[gpa_type].mean().to_frame('Average GPA').reset_index()
    avg_by_grade['Average GPA'] = round(avg_by_grade['Average GPA'], 2)
    gpas_pivoted = gpas_pivoted.merge(avg_by_grade, on='Grade Level', how='left')
    gpas_pivoted['Grade Level'] = gpas_pivoted['Grade Level']
    
    stack_cols = [f'Low: <= {gpa_low}', f'Medium: > {gpa_low}; < {gpa_high}', f'High: >= {gpa_high}', 'Unknown']

    fig = make_subplots(specs=[[{'secondary_y': True}]])

    for col in stack_cols:
        if col not in gpas_pivoted.columns:
            continue
        fig.add_trace(
            go.Bar(
                x=gpas_pivoted['Grade Level'],
                y=gpas_pivoted[col],
                offsetgroup=0,
                name=col,
                text=gpas_pivoted[col].astype('str')+'%'
            ),
            secondary_y=False
        )

    fig.add_trace(
        go.Bar(
            x=gpas_pivoted['Grade Level'],
            y=gpas_pivoted['Average GPA'],
            name='Average GPA',
            offsetgroup=1,
            text=gpas_pivoted['Average GPA']
        ),
        secondary_y=True
    )

    fig.update_layout(
        barmode='stack',
        title='GPA Ranges and Averages'
    )

    fig.update_xaxes(
        type='category',
        categoryarray=['9', '10', '11', '12'],
        title='Grade Level'
    )

    fig.update_yaxes(
        title_text='Percent of Students',
        range=[0, 100],
        showticklabels=False,
        secondary_y=False
    )

    fig.update_yaxes(
        title_text='Average GPA',
        range = [0, 4],
        secondary_y=True
    )

    fig.add_hline(
        y=gpa_benchmark,
        line_dash="dash",
        line_width=1,
        line_color=benchmark_bar_color,
        secondary_y=True
    )

    return fig

# TODO: Figure out alg 1 code mapping
def get_alg1_by_grade(AY: pd.DataFrame):
    valid_students = AY[AY['Grade Level'].isin([7, '7', 8, '8', 9, '9', 10, '10', 11, '11', 12, '12'])][['National CCREC Student ID', 'Grade Level', 'Algebra 1 Status']]
    alg1_by_grade = valid_students.groupby(['Grade Level', 'Algebra 1 Status']).size().to_frame('Student Count').reset_index()
    alg1_by_grade['Percent'] = alg1_by_grade.groupby('Grade Level')['Student Count'].transform(lambda x: round(x/x.sum()*100, 1))
    #print(alg1_by_grade)
    return px.bar()

def get_fafsa(AY: pd.DataFrame):
    seniors_only = AY[AY['Grade Level'].isin([12, '12'])][['National CCREC Student ID', 'Grade Level', 'FAFSA status code']]
    if len(seniors_only) == 0:
        return 'No Seniors'
    
    fafsa_percents = seniors_only.groupby('FAFSA status code').size().transform(lambda x: round(x/x.sum()*100, 1)).to_frame('Percent of Seniors').reset_index()
    return px.pie(fafsa_percents,
        names='FAFSA status code',
        values='Percent of Seniors',
        title='FAFSA Completion'
    )

# Backup Sankey 
def get_graduation_and_pse(AY: pd.DataFrame, college_visits: pd.DataFrame):
    seniors_only = AY[AY['Grade Level'].isin([12, '12'])][['National CCREC Student ID', 'HS Grad Status code', 'First College Attended Name', 'First College Attended IPEDS', 'Dual Enrollment']]
    seniors_only = seniors_only.merge(college_visits, how='left', on='National CCREC Student ID')

    # Sankey Level 1
    graduates = seniors_only[seniors_only['HS Grad Status code'] == 'Graduated']
    graduation_unknown = seniors_only[seniors_only['HS Grad Status code'] == 'Graduation Status Unknown']
    non_graduates = seniors_only[seniors_only['HS Grad Status code'] == 'Did Not Graduate']

    graduate_count = len(graduates)
    unknown_count = len(graduation_unknown)
    non_graduate_count = len(non_graduates)

    # Sankey Level 2
    enrolled = seniors_only[(~seniors_only['First College Attended IPEDS'].isna()) & (seniors_only['Dual Enrollment'] == 'N')]
    did_not_enroll = seniors_only[(seniors_only['First College Attended IPEDS'].isna()) | (seniors_only['Dual Enrollment'] == 'Y')]

    graduated_and_enrolled_count = len(graduates[(~graduates['First College Attended IPEDS'].isna()) & (graduates['Dual Enrollment'] == 'N')])
    graduated_not_enrolled_count = len(graduates[(graduates['First College Attended IPEDS'].isna()) | (graduates['Dual Enrollment'] == 'Y')])
    graduation_unknown_enrolled_count = len(graduation_unknown[(~graduation_unknown['First College Attended IPEDS'].isna()) & (graduation_unknown['Dual Enrollment'] == 'N')])
    graduation_unknown_not_enrolled_count = len(graduation_unknown[(graduation_unknown['First College Attended IPEDS'].isna()) | (graduation_unknown['Dual Enrollment'] == 'Y')])
    did_not_graduation_enrolled_count = len(non_graduates[(~non_graduates['First College Attended IPEDS'].isna()) & (non_graduates['Dual Enrollment'] == 'N')])
    did_not_graduation_not_enrolled_count = len(non_graduates[(non_graduates['First College Attended IPEDS'].isna()) | (non_graduates['Dual Enrollment'] == 'Y')])

    # Sankey level 3
    enrolled_and_went_on_college_visit = enrolled[~enrolled['IPEDS numbers of the Schools Visited'].isna()]
    enrolled_did_not_go_on_college_visit = enrolled[enrolled['IPEDS numbers of the Schools Visited'].isna()]

    enrolled_and_went_on_college_visit_count = len(enrolled_and_went_on_college_visit)
    enrolled_did_not_go_on_college_visit_count = len(enrolled_did_not_go_on_college_visit)

    # Sankey level 4
    enrolled_and_went_on_college_visit['Attended a Visited School'] = enrolled_and_went_on_college_visit.apply(lambda row: row['First College Attended IPEDS'] in row['IPEDS numbers of the Schools Visited'], axis=1)
    attended_visited_school = len(enrolled_and_went_on_college_visit[enrolled_and_went_on_college_visit['Attended a Visited School']])
    did_not_attended_visited_school = len(enrolled_and_went_on_college_visit[~enrolled_and_went_on_college_visit['Attended a Visited School']])

    EPSILON = 1e-6

    sankey = go.Figure(data=[go.Sankey(
        arrangement='snap',
        node = dict(
        pad = 15,
        thickness = 20,
        line = dict(color = 'black', width = 0.5),
        label = ['Graduated', 'Graduation Status Unknown', 'Did Not Graduate', 'Enrolled in Post Secondary', 'Did not Enroll in Post Secondary', 'Attended College Visit', 'Did not Attended College Visit', 'Enrolled in a school they visited', 'Did not Enrolled in a school they visited'],
        x=[0.1, 0.1, 0.1, 0.3, 0.3, 0.6, 0.6, 0.9, 0.9],
        y=[0.1, .9, .91, .1, .25, .1, .5, .1, .5],
        color = 'blue'
        ),
        link = dict(
        source = [0, 0, 1, 1, 2, 2, 3, 3, 5, 5],
        target = [3, 4, 3, 4, 3, 4, 5, 6, 7, 8],
        value = [v if v > 0 else EPSILON for v in [graduated_and_enrolled_count, graduated_not_enrolled_count, graduation_unknown_enrolled_count, graduation_unknown_not_enrolled_count, did_not_graduation_enrolled_count, did_not_graduation_not_enrolled_count, enrolled_and_went_on_college_visit_count, enrolled_did_not_go_on_college_visit_count, attended_visited_school, did_not_attended_visited_school]]
    ))])
    
    return sankey

# Helper for sankey level selections
def get_next_sankey_level(level):
    levels = {
        'FAFSA status code': ['HS Grad Status code', 'Post Secondary Enrollment', 'Post Secondary Graduation'],
        'HS Grad Status code': ['Post Secondary Enrollment', 'Post Secondary Graduation'],
        'Post Secondary Enrollment': ['Post Secondary Graduation'],
        'Post Secondary Graduation': [],
        'None': []
    }
    return levels[level]

def get_sankey(AY: pd.DataFrame, l1_selection, l2_selection, l3_selection, l4_selection):
    # Setting up Level 1 options 
    l1_options = ['FAFSA status code', 'HS Grad Status code', 'Post Secondary Enrollment']
    if not l1_selection:
        l1_selection = 'FAFSA status code'

    level_counter = 2
    options_dict = {
        'l1_selection': l1_selection,
        'l2_selection': l2_selection,
        'l3_selection': l3_selection,
        'l4_selection': l4_selection
    }
    
    # Getting each levels options based on previous selection
    for option_key in ['l1_selection', 'l2_selection', 'l3_selection']:
        option = options_dict[option_key]
        options_dict[f'l{level_counter}_options'] = get_next_sankey_level(option)
        if level_counter > 2:
            options_dict[f'l{level_counter}_options'] = ['None'] + options_dict[f'l{level_counter}_options']
        if options_dict[f'l{level_counter}_selection'] not in options_dict[f'l{level_counter}_options']:
            options_dict[f'l{level_counter}_selection'] = options_dict[f'l{level_counter}_options'][0]
        level_counter += 1

    # Creating final selection list (removes "None")
    selection_list = [x for x in [options_dict['l1_selection'], options_dict['l2_selection'], options_dict['l3_selection'], options_dict['l4_selection']] if x != 'None']

    # Calculating some fields for sankey
    AY['Post Secondary Enrollment'] = np.where(((AY['First College Attended Name'].isna()) | (AY['First College Attended Name'].str.lower()=='not found')), 'Did Not Enroll', 'Enrolled')
    AY['Post Secondary Graduation'] = np.where(((AY['Graduated Y/N'].isna()) | (AY['Graduated Y/N'].str.lower()=='n')), 'Has Not Graduated', 'Graduated')

    # Creates node list, dict of node index to level, and needed info for sankey creation
    node_list = []
    node_level_map = {}
    sankey_meta_data = {}
    count = 1
    node_index = 0
    for col_name in selection_list:
        sankey_meta_data[count] = {
            'column': col_name,
            'values': {}
        }
        value_list = AY[col_name].drop_duplicates().to_list()
        for val in value_list:
            node_level_map[node_index] = count
            node_index += 1
            node_list.append(val)
            sankey_meta_data[count]['values'][val] = len(node_list)-1
        count += 1

    # Creates X location and color lists
    x_step = 1/(len(sankey_meta_data)-1)
    x_splits = [round(i * x_step, 2) for i in range(len(sankey_meta_data))]
    x_locations = []
    colors = []
    count = 1
    for i in x_splits:
        for j in range(len(sankey_meta_data[count]['values'])):
            colors.append(mark_colors[count-1])
            x_locations.append(i)
        count += 1

    # Creates source, target, and value lists
    source_list = []
    target_list = []
    value_list = []
    for i in range(1, len(sankey_meta_data)):
        for source_value in sankey_meta_data[i]['values'].keys():
            for target_value in sankey_meta_data[i+1]['values'].keys():
                source_list.append(sankey_meta_data[i]['values'][source_value])
                target_list.append(sankey_meta_data[i+1]['values'][target_value])
                link_value = len(AY[(AY[sankey_meta_data[i]['column']] == source_value) & (AY[sankey_meta_data[i+1]['column']] == target_value)])
                value_list.append(link_value)

    # Calculating percentages for each level
    links_df = pd.DataFrame({
        'Source': source_list,
        'Target': target_list,
        'Value': value_list
    })
    out_counts = links_df.groupby('Source')['Value'].sum().to_frame('Out Sum').reset_index().rename(columns={'Source': 'Node'})
    in_counts = links_df.groupby('Target')['Value'].sum().to_frame('In Sum').reset_index().rename(columns={'Target': 'Node'})
    counts_combined = out_counts.merge(in_counts, how='outer', on='Node')
    counts_combined['Val'] = counts_combined[['Out Sum', 'In Sum']].max(axis=1)
    counts_combined.drop(columns=['Out Sum', 'In Sum'], inplace=True)
    counts_combined['Level'] = counts_combined['Node'].map(node_level_map)
    counts_combined['Percent'] = counts_combined.groupby('Level')['Val'].transform(lambda x: round(x/x.sum()*100, 1))
    counts_combined = counts_combined.set_index('Node')

    # Adding percentage per level to node lable list
    node_list_with_percent = []
    for i in range(len(node_list)):
        node_list_with_percent.append(f'{sankey_meta_data[node_level_map[i]]['column']}: {node_list[i]} - {counts_combined.loc[i, 'Percent']}%')

    # Creating custom data list for hover on links 
    link_hover_text = []
    for i in range(len(source_list)):
        source_node_index = source_list[i]
        target_node_index = target_list[i]
        link_value = value_list[i]
        
        source_level_field = sankey_meta_data[node_level_map[source_node_index]]['column']
        source_node_lable = node_list[source_node_index]
        percent_of_source = round((link_value/counts_combined.loc[source_node_index, 'Val'])*100, 2)
        target_level_field = sankey_meta_data[node_level_map[target_node_index]]['column']
        target_node_lable = node_list[target_node_index]
        percent_of_target = round((link_value/counts_combined.loc[target_node_index, 'Val'])*100, 2)

        text = f'Given the active filters and year, {link_value} students had a {source_level_field} of \"{source_node_lable}\" and a {target_level_field} of \"{target_node_lable}\". <br />This accounts for {percent_of_source}% of students with a {source_level_field} of \"{source_node_lable}\" and {percent_of_target}% of students with a {target_level_field} of \"{target_node_lable}\"'
        link_hover_text.append(text)

    # Sankey creation
    sankey = go.Figure(data=[go.Sankey(
        arrangement='fixed',
        node = dict(
        pad = 5,
        thickness = 40,
        line = dict(color = 'black', width = 0.5),
        label = node_list,
        customdata = node_list_with_percent,
        hovertemplate = '%{customdata}',
        x = x_locations,
        color = colors
        ),
        link = dict(
        source = source_list,
        target = target_list,
        value = value_list,
        customdata = link_hover_text,
        hovertemplate = '%{customdata}'
    ))])

    # Adding titles above each level
    lable_x_map = {
        0: -.02,
        .33: .3,
        .5: .5,
        .67: .71,
        1: 1.02
    }
    for i in range(len(x_splits)):
        sankey.add_annotation(
            x = lable_x_map[x_splits[i]],
            y = 1.06,
            text = selection_list[i],
            showarrow = False
        )

    return l1_options, l1_selection, options_dict['l2_options'], options_dict['l2_selection'], options_dict['l3_options'], options_dict['l3_selection'], options_dict['l4_options'], options_dict['l4_selection'], sankey

# =============================
# == Y-T-Y OBJECTIVES CHARTS ==
# =============================
def get_benchmark_line(years, benchmark, increase, benchmark_year, offset):
    years_df = pd.DataFrame({
        'Year': years
    })
    benchmark_df = pd.DataFrame({
        'Year': [benchmark_year],
        'Benchmark': [benchmark]
    })

    benchmark_df = benchmark_df.merge(years_df, on='Year', how='outer')
    benchmark_df.index = benchmark_df['Year']
    
    for i in [1, -1]:
        running_benchmark = benchmark
        running_year = benchmark_year
        while True:
            running_year = str(int(running_year.split('-')[0])+i) + '-' + str(int(running_year.split('-')[1])+i)
            if running_year in benchmark_df.index:
                running_benchmark = running_benchmark+(increase*i)
                benchmark_df.loc[running_year, 'Benchmark'] = running_benchmark
            else:
                break

    benchmark_line = go.Scatter(
        x=benchmark_df['Year'],
        y=benchmark_df['Benchmark'],
        mode='lines+markers',
        zorder=2,
        name='Benchmark',
        line_dash='dash',
        line_color=benchmark_bar_color,
        offsetgroup=offset
    )

    return benchmark_line

def get_yty_gpa(AY: pd.DataFrame, years, gpa_type, yty_gpa_radio, gpa_yty_benchmark_input, gpa_yty_increase_input, gpa_yty_benchmark_year):
    if gpa_yty_benchmark_input and gpa_yty_increase_input and gpa_yty_benchmark_year:
        benchmark_line = get_benchmark_line(years, gpa_yty_benchmark_input, gpa_yty_increase_input, gpa_yty_benchmark_year, '1')
    else:
        benchmark_line = 'No Benchmark'

    gpa_df = AY[['High School AY', gpa_type]]

    # Getting percent of missing vs available by year
    gpa_df['Availability'] = np.where(((AY[gpa_type].isna()) | (AY[gpa_type] > 6)), 'Missing', 'Available')
    gpa_availability_by_year = gpa_df.groupby(['High School AY', 'Availability']).size().to_frame('Student Count').reset_index()
    gpa_availability_by_year['Percent'] = gpa_availability_by_year.groupby('High School AY')['Student Count'].transform(lambda x: round(x/x.sum()*100, 1))
    gpa_availability_by_year = gpa_availability_by_year.pivot(index='High School AY', columns='Availability', values='Percent').reset_index()
    gpa_availability_by_year['Available'] = gpa_availability_by_year['Available'].fillna(0)

    # Getting avg GPA by Year
    avg_gpa: pd.DataFrame = gpa_df[gpa_df['Availability'] == 'Available'].groupby('High School AY')[gpa_type].mean().to_frame('Average GPA').reset_index()
    avg_gpa = gpa_availability_by_year[['High School AY']].drop_duplicates().merge(avg_gpa, on='High School AY', how='left').fillna(0)
    avg_gpa['Average GPA'] = round(avg_gpa['Average GPA'], 2)

    full_gpa_data_by_year = avg_gpa.merge(gpa_availability_by_year, on='High School AY', how='left')
    
    stack_cols = ['Available', 'Missing']
    fig = make_subplots(specs=[[{'secondary_y': True}]])
    for col in stack_cols:
        fig.add_trace(
            go.Bar(
                x=full_gpa_data_by_year['High School AY'],
                y=full_gpa_data_by_year[col],
                name=col,
                text=full_gpa_data_by_year[col].astype('str')+'%'
            ),
            secondary_y=True
        )

    fig.add_trace(
        go.Bar(
            x=full_gpa_data_by_year['High School AY'],
            y=full_gpa_data_by_year['Average GPA'],
            name='Average GPA',
            offsetgroup=1,
            text=full_gpa_data_by_year['Average GPA']
        ),
        secondary_y=False
    ).update_layout(
        barmode='stack',
        title='GPA Missingness and Average by Year'
    ).update_yaxes(
        showticklabels=False,
        showgrid=False,
        secondary_y=True
    ).update_yaxes(
        title_text='Average GPA',
        range = [0, 4],
        secondary_y=False
    )

    if type(benchmark_line) == go.Scatter:
        fig.add_trace(benchmark_line).update_layout(scattermode='group')

    return fig

def get_yty_fafsa(AY: pd.DataFrame, years, fafsa_yty_benchmark_input, fafsa_yty_increase_input, fafsa_yty_benchmark_year):
    if fafsa_yty_benchmark_input and fafsa_yty_increase_input and fafsa_yty_benchmark_year:
        benchmark_line = get_benchmark_line(years, fafsa_yty_benchmark_input, fafsa_yty_increase_input, fafsa_yty_benchmark_year, None)
    else:
        benchmark_line = 'No Benchmark'

    fafsa_df = AY[['High School AY', 'Grade Level', 'FAFSA status code']][AY['Grade Level'].isin([12, '12'])]
    fafsa_counts_by_year = fafsa_df.groupby(['High School AY', 'FAFSA status code']).size().to_frame('Student Count').reset_index()
    fafsa_counts_by_year['Percent'] = fafsa_counts_by_year.groupby('High School AY')['Student Count'].transform(lambda x: round(x/x.sum()*100, 1))
    fafsa_counts_by_year.sort_values(by='High School AY', inplace=True)
    fafsa_by_year_fig = px.bar(fafsa_counts_by_year,
        title='FAFSA Completion by Year',
        x='High School AY',
        category_orders={'High School AY': fafsa_counts_by_year['High School AY'].drop_duplicates().sort_index()},
        y='Percent',
        text_auto=True,
        color='FAFSA status code',
        barmode='stack',
    ).update_traces(
        texttemplate='%{y}%'
    ).update_layout(
        legend={'title_text': None}
    )

    if type(benchmark_line) == go.Scatter:
        fafsa_by_year_fig.add_trace(benchmark_line)

    return fafsa_by_year_fig

def get_yty_graduation(AY: pd.DataFrame, years, graduation_yty_benchmark_input, graduation_yty_increase_input, graduation_yty_benchmark_year):
    if graduation_yty_benchmark_input and graduation_yty_increase_input and graduation_yty_benchmark_year:
        benchmark_line = get_benchmark_line(years, graduation_yty_benchmark_input, graduation_yty_increase_input, graduation_yty_benchmark_year, None)
    else:
        benchmark_line = 'No Benchmark'
    
    graduation_df = AY[['High School AY', 'Grade Level', 'HS Grad Status code']][AY['Grade Level'].isin([12, '12'])]
    graduation_counts_by_year = graduation_df.groupby(['High School AY', 'HS Grad Status code']).size().to_frame('Student Count').reset_index()
    graduation_counts_by_year['Percent'] = graduation_counts_by_year.groupby('High School AY')['Student Count'].transform(lambda x: round(x/x.sum()*100, 1))
    graduation_by_year_fig = px.bar(graduation_counts_by_year,
        title='Graduation by Year',
        x='High School AY',
        category_orders={
            'High School AY': graduation_counts_by_year['High School AY'].drop_duplicates().sort_index(),
            'HS Grad Status code': [
                'Graduated',
                'Did Not Graduate',
                'Graduation Status Unknown',
                'N/A'
            ]
        },
        y='Percent',
        text_auto=True,
        color='HS Grad Status code',
        barmode='stack',
    ).update_traces(
        texttemplate='%{y}%'
    ).update_layout(
        legend={'title_text': None}
    )

    if type(benchmark_line) == go.Scatter:
        graduation_by_year_fig.add_trace(benchmark_line)

    return graduation_by_year_fig

def get_yty_pse(AY: pd.DataFrame, years, pse_yty_benchmark_input, pse_yty_increase_input, pse_yty_benchmark_year):
    if pse_yty_benchmark_input and pse_yty_increase_input and pse_yty_benchmark_year:
        benchmark_line = get_benchmark_line(years, pse_yty_benchmark_input, pse_yty_increase_input, pse_yty_benchmark_year, None)
    else:
        benchmark_line = 'No Benchmark'
    
    pse_df = AY[(AY['Grade Level'].isin([12, '12'])) & (AY['HS Grad Status code'] == 'Graduated')][['High School AY', 'First College Attended Name']]
    pse_df['Post Secondary Enrollment'] = np.where(((pse_df['First College Attended Name'].isna()) | (pse_df['First College Attended Name'].str.lower()=='not found')), 'Did Not Enroll', 'Enrolled')
    pse_by_year = pse_df.groupby(['High School AY', 'Post Secondary Enrollment']).size().to_frame('Student Count').reset_index()
    pse_by_year['Percent'] = pse_by_year.groupby('High School AY')['Student Count'].transform(lambda x: round(x/x.sum()*100, 1))
    pse_by_year_fig = px.bar(pse_by_year,
        title='Post Secondary Enrollment by Year',
        x='High School AY',
        category_orders={
            'High School AY': pse_by_year['High School AY'].drop_duplicates().sort_index(),
            'Post Secondary Enrollment': [
                'Enrolled',
                'Did Not Enroll'
            ]
        },
        y='Percent',
        color='Post Secondary Enrollment',
        barmode='stack',
        text_auto=True
    ).update_traces(
        texttemplate='%{y}%'
    ).update_layout(
        legend={'title_text': None}
    )
    
    if type(benchmark_line) == go.Scatter:
        pse_by_year_fig.add_trace(benchmark_line)

    return pse_by_year_fig


# =============================
# == DISTRICT COMPARE CHARTS ==
# =============================
def get_service_time_pie(AY: pd.DataFrame, title_text):
    # sum hours by category, sum for total, calculate percent
    time_by_service_type = AY[service_columns].sum().to_frame('Hours').reset_index()
    total_time = time_by_service_type['Hours'].sum()
    time_by_service_type['Total Time'] = total_time
    time_by_service_type['Percent'] = round((time_by_service_type['Hours']/time_by_service_type['Total Time'])*100, 1)
    time_by_service_type.rename(columns={'index': 'Service Category'}, inplace=True)

    time_by_service_type = time_by_service_type[time_by_service_type['Percent'] != 0]

    service_time_percents_fig = px.pie(time_by_service_type,
        names = 'Service Category',
        values = 'Percent',
        title = title_text
    )

    return service_time_percents_fig

def get_participation_ranges(AY: pd.DataFrame, participation_low, participation_high, group_lable):
    AY['Total Service Time'] = AY[service_columns].sum(axis=1)/60

    conditions = [
        (AY['Total Service Time'] == 0),
        ((AY['Total Service Time'] > 0) & (AY['Total Service Time'] <= participation_low)),
        ((AY['Total Service Time'] > participation_low) & (AY['Total Service Time'] <= participation_high)),
        (AY['Total Service Time'] > participation_high)
    ]
    choices = ['No Participation', f'Low: <= {participation_low}', f'Medium: > {participation_low}; <= {participation_high}', f'High: > {participation_high}']
    AY['Participation Range'] = np.select(conditions, choices, default='Unknown')

    participation_range_by_grade = AY.groupby(['Grade Level', 'Participation Range']).size().to_frame('Student Count').reset_index()
    participation_range_by_grade['Percent'] = participation_range_by_grade.groupby('Grade Level')['Student Count'].transform(lambda x: round(x/x.sum()*100, 1))
    if group_lable:
        participation_range_by_grade['Group'] = group_lable
    
    return participation_range_by_grade


def get_service_participation_compare(AY: pd.DataFrame, district_AY, participation_low, participation_high):
    
    program_participation = get_participation_ranges(AY, participation_low, participation_high, 'Program')


    return px.bar()