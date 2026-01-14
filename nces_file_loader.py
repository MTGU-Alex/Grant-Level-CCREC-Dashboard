'''
Helper script for formating yearly NCES locale files into a single pickle.
Raw files go in \\raw_locale_files
Each file needs fields: nces id, school name, Locale code, and school year
- Code used for cleaning csvs below (commented out)
'''

import pandas as pd
import numpy as np
import os

current_dir = os.getcwd()
locale_dir = current_dir+'\\raw_locale_files\\'

# iterating through non-bkup files, concat with full_df
full_df = pd.DataFrame()
for locale_file in [file_name for file_name in os.listdir(locale_dir) if '_bkup' not in file_name]:
    df = pd.read_csv(locale_dir+locale_file, low_memory=False, dtype={'NCESSCH': 'str'})
    df = df[df['LOCALE'] != 'N']
    df['LOCALE'] = df['LOCALE'].astype('int')
    df = df[['NCESSCH', 'LOCALE', 'SCHOOLYEAR']]
    full_df = pd.concat([full_df, df])

# getting prev/next locale and years and filtering rows
full_df = full_df.sort_values(['NCESSCH', 'SCHOOLYEAR'])
full_df[['PREV_SCHOOLYEAR', 'PREV_LOCALE']] = full_df.groupby('NCESSCH')[['SCHOOLYEAR', 'LOCALE']].shift(periods=1)
full_df = full_df[(full_df['LOCALE'] != full_df['PREV_LOCALE'])]
full_df[['NEXT_LOCALE_SCHOOL_YEAR', 'NEXT_LOCALE']] = full_df.groupby('NCESSCH')[['SCHOOLYEAR', 'LOCALE']].shift(periods=-1)

# Setting start year and end year for each local year range
full_df['START_YEAR'] = np.where(full_df['PREV_SCHOOLYEAR'].isna(), 1, full_df['SCHOOLYEAR'].str[:4].astype('int'))
full_df['NEXT_LOCALE_SCHOOL_YEAR'] = full_df['NEXT_LOCALE_SCHOOL_YEAR'].fillna('9999-9999')
full_df['END_YEAR'] = full_df['NEXT_LOCALE_SCHOOL_YEAR'].str[:4].astype('int') - 1
full_df = full_df[['NCESSCH', 'LOCALE', 'START_YEAR', 'END_YEAR']]

# mapping locale names from codes
locale_mapping = {
    11: 'City - Large',
    12: 'City - Midsize',
    13: 'City - Small',
    21: 'Suburban - Large',
    22: 'Suburban - Midsize',
    23: 'Suburban - Small',
    31: 'Town - Fringe',
    32: 'Town - Distant',
    33: 'Town - Remote',    
    41: 'Rural - Fringe',
    42: 'Rural - Distant',
    43: 'Rural - Remote'
}
full_df['LOCALE_NAME'] = full_df['LOCALE'].map(locale_mapping)
full_df['LOCAL_CATEGORY'] = full_df['LOCALE_NAME'].str.split().str[0]

# pickling final results
#full_df.to_pickle(current_dir+'\\locale_data.pkl')

# cleaning files with no school year column
'''
locale_2015_path = locale_dir+'Public_School_Locations_2015-16_bkup.csv'
locale_2016_path = locale_dir+'Public_School_Locations_2016-17_bkup.csv'

df_15 = pd.read_csv(locale_2015_path, low_memory=False, dtype={'NCESSCH': 'str'})
df_16 = pd.read_csv(locale_2016_path, low_memory=False, dtype={'NCESSCH': 'str'})
df_15 = df_15[df_15['LOCALE'] != 'N']
df_16 = df_16[df_16['LOCALE'] != 'N']
df_15['SCHOOLYEAR'] = '2015-2016'
df_16['SCHOOLYEAR'] = '2016-2017'

df_15.to_csv(locale_2015_path.replace('_bkup', ''), index=False)
df_16.to_csv(locale_2016_path.replace('_bkup', ''), index=False)
'''

# cleaning "Characteristic" file to match other format
'''
raw_2018_path = '\\downloads\\Public_School_Characteristics_2018-19.csv'
cleaned_2018_path = locale_dir+'Public_School_Locations_2018-19.csv'
df_2018 = pd.read_csv(raw_2018_path, low_memory=False, dtype={'NCESSCH': 'str'})
df_2018.rename(columns={'SURVYEAR': 'SCHOOLYEAR', 'SCH_NAME': 'NAME'}, inplace=True)
df_2018['LOCALE'] = df_2018['ULOCALE'].str[:2]
df_2018[['NCESSCH', 'SCHOOLYEAR', 'NAME', 'LOCALE']].to_csv(cleaned_2018_path, index=False)
'''