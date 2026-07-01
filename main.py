"""
CCREC Grant Level Dashboard - Entry Point.
Loads data, initializes the Dash application, and starts the server.
"""

print('- Starting CCREC Dashboard')
print('- A folder selection window may appear. Please select your data folder.')
print('- Please be patient, loading may take a minute or two.')

import sys

from dash import Dash

import data_loader
from data_service import DashboardData
from callbacks import register_callbacks
import components


def create_app():
    """Create and configure the Dash application."""
    # Load data
    if len(sys.argv) > 1:
        data_dict = data_loader.load_data(sys.argv[1])
    else:
        data_dict = data_loader.load_data('default')

    if isinstance(data_dict, str):
        print(data_dict)
        sys.exit(1)

    # Create data service
    data = DashboardData(
        ay_df=data_dict['ay_df'],
        agg_services_df=data_dict['agg_services_df'],
        duration_by_student_month_type=data_dict['duration_by_student_month_type'],
        college_visits=data_dict['college_visits'],
    )

    # Initialize Dash
    app = Dash(__name__, suppress_callback_exceptions=True)
    app.title = 'CCREC Dashboard'

    # Set layout
    group_list = ['All'] + sorted(data_dict['ay_df']['School Display Name'].drop_duplicates().to_list())
    app.layout = components.get_app_layout(data.years, data_dict['renames'], group_list)

    # Register callbacks
    register_callbacks(app, data)
    return app

# Create and run
app = create_app()

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)