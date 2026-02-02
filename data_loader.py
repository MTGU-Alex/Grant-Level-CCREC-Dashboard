from tkinter import filedialog
import pandas as pd
from tabulate import tabulate
import os, sys

service_code_to_type = {
    1: 'Tutoring/Homework Assistance',
    2: 'Mentoring',
    3: 'Financial Aid Counseling/Advising',
    4: 'Counseling/Advising',
    5: 'College Visit',
    6: 'Job Site Visit/Job Shadowing',
    7: 'Summer Programs',
    8: 'Educational Field Trips',
    9: 'Student Workshops',
    10: 'Parent/Family Workshops',
    11: 'Family Counseling/ Advising',
    12: 'Family College Visit',
    13: 'Other Family Events'
}

def print_data_overview(ay_df: pd.DataFrame, agg_services: pd.DataFrame):
    students_per_year = ay_df.groupby('High School AY')['National CCREC Student ID'].nunique()
    students_with_service_per_year = agg_services.groupby('High School AY')['National CCREC Student ID'].nunique()
    overview_df = pd.merge(students_per_year, students_with_service_per_year, left_index=True, right_index=True, how='outer').fillna(0)
    overview_df.rename(columns={'National CCREC Student ID_x': 'Students in AY file(s)', 'National CCREC Student ID_y': 'Students in service file(s)'}, inplace=True)
    overview_df.reset_index(inplace=True)
    print('---------------------')
    print('Data counts:')
    print(tabulate(overview_df, showindex=False, tablefmt='rounded_outline', headers='keys'))


# helper function for creating and cleaning aggregated service df (by month)
def create_service_aggregation(service_df):
    print('- Aggregating service data')
    service_df['Service Date'] = pd.to_datetime(service_df['Service Date'])
    service_df['Service Type Code'] = service_df['Service Type Code'].map(service_code_to_type)
    aggregated_services = service_df.groupby(['Academic Year', service_df['Service Date'].dt.month, 'Service Type Code']).agg(
        service_mins = ('Service Time', 'sum'),
        students = ('National CCREC Student ID', 'nunique')
    ).reset_index().rename(columns={'Academic Year': 'High School AY', 'Service Date': 'Month', 'service_mins': 'Total Minutes', 'students': 'Student Count'})
    
    service_duration_by_student_month_type = service_df.groupby(['Academic Year', service_df['Service Date'].dt.month, 'Service Type Code', 'National CCREC Student ID'])['Service Time'].sum().reset_index()
    service_duration_by_student_month_type.rename(columns={'Academic Year': 'High School AY', 'Service Date': 'Month', 'Service Time': 'Total Time'}, inplace=True)

    return aggregated_services, service_duration_by_student_month_type

# Finds locale from NCES code
def get_locale(ay_df):
    print('- Finding locale based on NCES ID')
    ay_len = len(ay_df)

    # mergeing AY with 
    locale_pickle_path = get_data_path('locale_data.pkl')
    nces_df = pd.read_pickle(locale_pickle_path)
    ay_df = ay_df.merge(nces_df, how='left', left_on='School NCES ID', right_on='NCESSCH')

    # getting records with missing locale
    missing_ay = ay_df[ay_df['NCESSCH'].isna()]
    missing_len = len(missing_ay)
    missing_ay.loc[:, ['LOCALE_NAME', 'LOCAL_CATEGORY']] = 'Unknown'
    if missing_len > 0:
        print(f'- {missing_len} of {ay_len} total records are missing a matching NCES ID.')

    # filtering locales by year
    ay_df['Year of School Year Start'] = ay_df['High School AY'].str[:4].astype('int')
    ay_df = ay_df[(ay_df['Year of School Year Start'] >= ay_df['START_YEAR']) & (ay_df['Year of School Year Start'] <= ay_df['END_YEAR'])]
    ay_after_filter_len = len(ay_df)

    # combining missing and filtered
    ay_df = pd.concat([ay_df, missing_ay])
    ay_df.drop(columns=['NCESSCH', 'START_YEAR', 'END_YEAR'], inplace=True)
    ay_df.rename(columns={'LOCALE': 'Locale Code', 'LOCALE_NAME': 'Full Locale', 'LOCAL_CATEGORY': 'Locale'}, inplace=True)
    final_len = len(ay_df)

    if final_len != ay_len:
        print(f'WARNING: {final_len} records found after merging with locale dataset, {ay_len} records before.')

    return ay_df

# Function for mapping Gender/race/ethnicity codes to name in text
def map_codes_to_strings(ay_df):
    code_mappings = {
        'Gender Code': {
            1: 'Female',
            2: 'Male',
            3: 'Unknown',
            4: 'Gender Neutral'
        },
        'Ethnicity Code': {
            0: 'Not Hispanic or Latino',
            1: 'Hispanic or Latino',
            2: 'Unknown'
        },
        'Race Code': {
            1: 'American Indian or Alaskan Native',
            2: 'Asain',
            3: 'Black or African American',
            4: 'Native Hawaiian of Pacific Islander',
            5: 'White',
            6: 'Two or More Races',
            7: 'Unknown'
        }
    }
    for item in code_mappings:
        ay_df[item] = ay_df[item].map(code_mappings[item]).fillna('Unknown')
    
    return ay_df

# Helper code for csv path after compiling to exe
def get_data_path(filename):
    if hasattr(sys, '_MEIPASS'):
        bundle_dir = sys._MEIPASS
    else:
        bundle_dir = os.path.abspath(os.path.dirname(__file__))
    
    return os.path.join(bundle_dir, filename)
    
# searches through file list and returns data frame if pattern is found in file name
def get_individual_df(file_type, file_pattern, file_path_list):
    error_message = 'ERROR: '
    dir_name = file_path_list[0].split('/')[-2]

    file_found = any([file_pattern in file_name.split('/')[-1].lower() for file_name in file_path_list])
    if file_found:
        valid_file_paths = [file_path for file_path in file_path_list if file_pattern in file_path.split('/')[-1].lower() and file_path[-4:] == '.csv']
        if len(valid_file_paths) == 0:
            error_message += f'{file_type} file found in {dir_name} but not in csv format'
            file_found = False
        else:
            if len(valid_file_paths) > 1:
                print(f'Multiple {file_type} files found in {dir_name}. Using {valid_file_paths[0].split('/')[-1]} for dashboard.')
            return_df = pd.read_csv(valid_file_paths[0], low_memory=False)
    else:
        error_message += f'{file_type} file not found in folder: {dir_name}'

    if not file_found:
        return error_message
    else:
        return return_df

# function for extracting ay and service df from a file list
def get_ay_and_service(file_path_list):
    error_message = ''
    error_flag = False

    ay_search = get_individual_df('AY', 'aydata', file_path_list)
    service_search = get_individual_df('Service', 'servicedata', file_path_list)

    if type(ay_search) == str:
        error_message += ay_search
        error_flag = True

    if type(service_search) == str:
        error_message += service_search
        error_flag = True

    if error_flag:
        return error_message
    else:
        return {
            'ay_df': ay_search,
            'service_df': service_search
        }

# function to return df for subdir file structure
def process_subdirs(subdir_list):
    ay_df = pd.DataFrame()
    service_df = pd.DataFrame()
    for subdir in subdir_list:
        file_path_list = [subdir+'/'+file_name for file_name in os.listdir(subdir) if not os.path.isdir(subdir+'/'+file_name)]
        search_return = get_ay_and_service(file_path_list)
        if type(search_return) == str:
            return search_return
        else:
            ay_df = pd.concat([ay_df, search_return['ay_df']])
            service_df = pd.concat([service_df, search_return['service_df']])
    return {
        'ay_df': ay_df,
        'service_df': service_df
    }

# function that takes path to CCREC data folder, 
# returns AY, student, service dfs of all years combined
def load_data():

    # opens directory selection window
    selected_dir = filedialog.askdirectory(
        title = 'Please select source file folder'
    )
    if selected_dir == '':
        return 'ERROR: No source file folder selected.'
    
    print(f'- Reading data from: {selected_dir}')
    
    files = []
    subdirs = []
    # finds all files and directories in selected dir
    for element in os.listdir(selected_dir):
        element_path = selected_dir+'/'+element
        if os.path.isdir(element_path):
            subdirs.append(element_path)
        else:
            files.append(element_path)

    # gets dataframes for either valid data format
    if any(['aydata' in file_name.split('/')[-1].lower() for file_name in files if file_name[-4:] == '.csv']) and any(['servicedata' in file_name.split('/')[-1].lower() for file_name in files if file_name[-4:] == '.csv']):
        print(f'- AY and service files found in {selected_dir}')
        raw_dfs = get_ay_and_service(files)
    elif len(subdirs) > 0:
        print(f'- Searching thorugh {len(subdirs)} subfiles in {selected_dir}')
        raw_dfs = process_subdirs(subdirs)
    else:
        return f'ERROR: Files not found in {selected_dir}, please make sure your AY file name contains \"aydata\", your service file contains \"servicedata\", and they are both csv files.'

    if type(raw_dfs) == str:
        return raw_dfs
    else: 
        ay_df = raw_dfs['ay_df']
        service_df = raw_dfs['service_df']
        print('- Ay and service data frames successfully loaded from CSV files ')

    # Getting locales by NCES code, cleaning and renaming columns
    ay_df = ay_df[['High School AY', 'Program Model Code', 'School NCES ID', 'National CCREC Student ID', 'Student Type code', 'Gender Code', 'Ethnicity Code', 'Race Code', 'Grade Level', 'Enrollment Status Code', 'Service 1 Total', 'Service 2 Total', 'Service 3 Total', 'Service 4 Total', 'Service 5 Total', 'Service 6 Total', 'Service 7 Total', 'Service 8 Total', 'Service 9 Total', 'Service 10 Total', 'Service 11 Total', 'Service 12 Total', 'Service 13 Total']].rename(columns={'School NCES ID': 'School NCES ID INT'})
    ay_df['School NCES ID'] = ay_df['School NCES ID INT'].astype('string')
    ay_df.drop(columns='School NCES ID INT', inplace=True)
    ay_df.loc[:, 'School NCES ID'] = ay_df['School NCES ID'].str.pad(width=12, side='left', fillchar='0')
    ay_df = get_locale(ay_df)

    service_cols = [col for col in ay_df.columns if 'Service' in col]
    for col in service_cols:
        ay_df[col] = ay_df[col].fillna(0)

    ay_df.rename(columns={
        'Service 1 Total': 'Tutoring/Homework Assistance',
        'Service 2 Total': 'Mentoring',
        'Service 3 Total': 'Financial Aid Counseling/Advising',
        'Service 4 Total': 'Counseling/Advising',
        'Service 5 Total': 'College Visit',
        'Service 6 Total': 'Job Site Visit/Job Shadowing',
        'Service 7 Total': 'Summer Programs',
        'Service 8 Total': 'Educational Field Trips',
        'Service 9 Total': 'Student Workshops',
        'Service 10 Total': 'Parent/Family Workshops',
        'Service 11 Total': 'Family Counseling/ Advising',
        'Service 12 Total': 'Family College Visit',
        'Service 13 Total': 'Other Family Events'
    }, inplace=True)
    
    ay_df = map_codes_to_strings(ay_df)

    # getting cleaned/aggregated services
    aggregated_services, student_service_duration_by_month = create_service_aggregation(service_df)
    
    # Returns dictionary of the 3 dfs
    print('- Data load complete!')
    print_data_overview(ay_df, student_service_duration_by_month)
    return {
        'ay_df': ay_df,
        'agg_services_df': aggregated_services,
        'duration_by_student_month_type': student_service_duration_by_month,
    }

if __name__ == '__main__':
    load_data()