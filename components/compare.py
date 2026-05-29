"""Layout for the Compare page."""

from dash import dcc, html
from plotly.graph_objects import Figure


def get_compare_layout(
    district_list: list,
    current_district: str,
    range_low: float,
    range_high: float,
    objective_selection: str,
    gpa_type: str,
    district_pie: Figure,
    program_pie: Figure,
    participation_compare: Figure,
    objective_compare,
) -> html.Div:
    """Build the compare page layout."""
    # Conditional GPA radio
    gpa_radio = None
    if objective_selection == 'GPA':
        gpa_radio = dcc.RadioItems(
            ['Cumulative GPA', 'Final Term GPA'],
            gpa_type, inline=True, id='compare-gpa-radio',
        )

    # Objective chart (can be Figure or html.Div for no-data message)
    if isinstance(objective_compare, html.Div):
        objective_content = objective_compare
    else:
        objective_content = dcc.Graph(
            figure=objective_compare, id='objective-compare', className='graph'
        )

    return html.Div([
        html.Div([
            html.Div([
                html.H4('District:', className='control-label'),
                dcc.Dropdown(
                    id='district-dropdown',
                    options=[{'label': d, 'value': d} for d in sorted(district_list)],
                    value=current_district, clearable=False,
                ),
                html.Hr(className='hr-line'),
                html.H4('Service Hour Ranges:', className='control-label'),
                dcc.RangeSlider(0, 50, 1, value=[range_low, range_high], id='compare-service-ranges'),
                html.Hr(className='hr-line'),
                html.H4('Objective Comparison:', className='control-label'),
                dcc.Dropdown(
                    id='objective-compare-dropdown',
                    options=['GPA', 'FAFSA', 'Graduation', 'Post Secondary Enrollment'],
                    value=objective_selection, clearable=False,
                ),
                gpa_radio,
            ], id='compare-filters-div', className='graph sidebar-filters'),
            dcc.Graph(figure=district_pie, id='district-service-time-split', className='graph'),
            dcc.Graph(figure=program_pie, id='program-service-time-split', className='graph'),
        ], className='graph-flex'),
        html.Div([
            dcc.Graph(figure=participation_compare, id='service-participation-compare', className='graph'),
            objective_content,
        ], className='graph-flex'),
    ])