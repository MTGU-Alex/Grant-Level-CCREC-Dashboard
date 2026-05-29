"""Layout for the Services Year-to-Year page."""

from dash import dcc, html
from plotly.graph_objects import Figure


def get_services_yty_layout(
    threshold: float,
    service_types: list,
    selected_types: list,
    service_time_by_type: Figure,
    enrollment_by_year: Figure,
    participation_by_month: Figure,
    hours_per_student: Figure,
) -> html.Div:
    """Build the services YTY page layout."""
    return html.Div([
        html.Div([
            dcc.Graph(figure=service_time_by_type, id='yty-service-time-by-type', className='graph graph-2x'),
            dcc.Graph(figure=enrollment_by_year, id='yty-enrollment', className='graph'),
        ], className='graph-flex'),
        html.Div([
            html.Div([
                html.Div([
                    html.H5('Threshold (Hours):', className='filter-label'),
                    html.Span(threshold, id='yty-threshold-value', className='filter-value'),
                ], className='filter-label-row'),
                dcc.Slider(
                    id='yty-time-slider',
                    min=0, max=50, step=1, value=threshold,
                    marks={i: str(i) for i in range(0, 51, 10)},
                ),
                html.Hr(className='hr-line'),
                html.H5('Service Types:', className='filter-label'),
                html.Div([
                    dcc.Checklist(
                        id='yty-type-filter',
                        options=service_types,
                        value=selected_types,
                        inline=False,
                        className='service-checklist',
                    ),
                ], className='checklist-container'),
            ], id='yty-filters-div', className='sidebar-filters'),
            dcc.Graph(figure=participation_by_month, id='participation-by-month', className='graph'),
        ], className='graph-flex'),
        html.Div([
            dcc.Graph(figure=hours_per_student, id='avg-service-hours-per-student-by-month', className='graph'),
        ], className='graph-flex'),
    ])