print('- Starting dashboard')
print('- Look for a folder selection window with a title of \"Please select a source file folder\"')
print('- Please be patient, it may take a minute or two ')

import sys
from dash import Dash, html, dcc

import data_loader
import components
from callbacks import register_callbacks
import pickle

# Reading in data with data_loader.py and mapping codes
if len(sys.argv) > 1:
    data_frames = data_loader.load_data(sys.argv[1])
else:
    data_frames = data_loader.load_data('default')
if type(data_frames) == str:
    print(data_frames)
    sys.exit()
AY_df = data_frames['ay_df']
agg_services_df = data_frames['agg_services_df']
duration_by_student_month_type = data_frames['duration_by_student_month_type']

# Setting up Dash app
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = 'Dashboard'

app.layout = components.get_layout(AY_df['High School AY'].unique())
register_callbacks(app, AY_df, agg_services_df, duration_by_student_month_type)

# Running Dash app
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)