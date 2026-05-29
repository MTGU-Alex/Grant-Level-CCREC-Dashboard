"""Layout for the Services page."""

from dash import dcc, html
from plotly.graph_objects import Figure


def get_services_layout(
    threshold: float,
    service_types: list,
    selected_types: list,
    participation_and_avg_time: Figure,
    participation_by_grade: Figure,
    avg_time_by_grade: Figure,
) -> html.Div:
    """Build the services page layout."""
    return html.Div([
        html.Div([
            dcc.Graph(figure=participation_and_avg_time, id='participation-and-avg-time', className='graph'),
        ], className='graph-flex'),
        html.Div([
            html.Div([
                html.Div([
                    html.H5('Threshold (Hours):', className='filter-label'),
                    html.Span(threshold, id='services-threshold-value', className='filter-value'),
                ], className='filter-label-row'),
                dcc.Slider(
                    id='services-time-slider',
                    min=0, max=50, step=1, value=threshold,
                    marks={i: str(i) for i in range(0, 51, 10)},
                ),
                html.Hr(className='hr-line'),
                html.H5('Service Types:', className='filter-label'),
                html.Div([
                    dcc.Checklist(
                        id='services-type-filter',
                        options=service_types,
                        value=selected_types,
                        inline=False,
                        className='service-checklist',
                    ),
                ], className='checklist-container'),
            ], id='services-filters-div', className='sidebar-filters'),
            dcc.Graph(figure=participation_by_grade, id='participation-by-grade', className='graph'),
            dcc.Graph(figure=avg_time_by_grade, id='avg-time-by-grade', className='graph'),
        ], className='graph-flex'),
    ])