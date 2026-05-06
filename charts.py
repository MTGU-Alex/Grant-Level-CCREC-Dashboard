import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio


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

# =======================
# == ENROLLMENT CHARTS ==
# =======================
def get_enrollment_by_locale(AY: pd.DataFrame):
    enrollment_by_locale = AY.groupby('Locale').size().to_frame('Student Count').reset_index().sort_values('Student Count')
    return px.bar(enrollment_by_locale,
        x='Student Count',
        y='Locale',
        text_auto=True,
        title='Enrollment by Locale'
    )

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
    AY['Total Service Time'] = AY[types].sum(axis=1)/60
    students_per_grade = AY.groupby('Grade Level').size().to_frame('Students').reset_index()
    if threshold == 0 :
        filtered_df_for_participation = AY[AY['Total Service Time'] != 0]
    else:
        filtered_df_for_participation = AY[AY['Total Service Time'] >= threshold]
    student_participation_count_by_grade = filtered_df_for_participation.groupby('Grade Level').size().to_frame('Students').reset_index()
    
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
    service_time_by_type_and_year = AY.groupby('High School AY')[service_columns].sum().reset_index()
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
    students_per_year = AY.groupby('High School AY').size().to_frame('Student Count').reset_index()
    month_order = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    months_df = pd.DataFrame({'Month': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]})
    students_per_month = students_per_year.merge(months_df, how='cross')

    filtered_duration_by_month_student = duration_by_student_month_type[duration_by_student_month_type['Service Type Code'].isin(service_types)]
    duration_by_month_student = filtered_duration_by_month_student.groupby(['High School AY', 'Month', 'National CCREC Student ID'])['Total Time'].sum().reset_index()
    duration_by_month_student['Total Time'] = duration_by_month_student['Total Time']/60
    if threshold == 0:
        filtered_duration_by_month_student = duration_by_month_student
    else:
        filtered_duration_by_month_student = duration_by_month_student[duration_by_month_student['Total Time'] >= threshold]

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
    students_per_year = AY.groupby('High School AY').size().to_frame('Student Count').reset_index()
    month_order = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    months_df = pd.DataFrame({'Month': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]})
    students_per_month = students_per_year.merge(months_df, how='cross')

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