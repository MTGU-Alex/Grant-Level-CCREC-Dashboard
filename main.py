import sys
from dash import Dash, html, dcc

import data_loader
import components
from callbacks import register_callbacks

'''
NCES LOCALES: https://data-nces.opendata.arcgis.com/search?groupIds=455147561fd3416daa180395fb4e9237
- Can't find 2020-21
'''

# Reading in data with data_loader.py and mapping codes
data_frames = data_loader.load_data()
if type(data_frames) == str:
    print(data_frames)
    sys.exit()
AY_df = data_frames['ay_df']
agg_services_df = data_frames['agg_services_df']
duration_by_student_month_type = data_frames['duration_by_student_month_type']

# Setting up Dash app
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = 'Dashboard'

app.layout = html.Div([
    dcc.Location(id='url'),
    dcc.Store(id='temp-demographics-filter-store'),
    dcc.Store(id='temp-services-filter-store'),
    dcc.Store(id='temp-yty-filter-store'),
    dcc.Store(id='demographics-filter-store'),
    dcc.Store(id='services-filter-store'),
    dcc.Store(id='yty-filter-store'),
    html.Div(id='page-content')
])
register_callbacks(app, AY_df, agg_services_df, duration_by_student_month_type)

# Running Dash app
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
    