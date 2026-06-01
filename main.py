# "main.py"
"""
main.py
Entry point for the CCREC Grant Level Dashboard.

Usage
-----
  python main.py              # opens a folder-selection dialog
  python main.py /path/to/data   # loads data directly from the given folder
"""

print('- Starting dashboard')
print('- Look for a folder-selection window titled '
      '"Please select source file folder"')
print('- Please be patient — initial data load may take a minute or two.')

import sys
from dash import Dash

import data_loader
import components
from callbacks import register_callbacks

# ── Load data ──────────────────────────────────────────────────────────────────
data_frames = data_loader.load_data(sys.argv[1] if len(sys.argv) > 1 else 'default')

if isinstance(data_frames, str):
    print(data_frames)
    sys.exit(1)

AY_df                          = data_frames['ay_df']
agg_services_df                = data_frames['agg_services_df']
duration_by_student_month_type = data_frames['duration_by_student_month_type']
college_visits                 = data_frames['college_visits']

# ── Initialise Dash app ────────────────────────────────────────────────────────
app = Dash(__name__, suppress_callback_exceptions=True)
app.title = 'CCREC Dashboard'

app.layout = components.get_layout(AY_df['High School AY'].unique())
register_callbacks(app, AY_df, agg_services_df, duration_by_student_month_type, college_visits)

# ── Run ────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)