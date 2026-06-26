"""Layout for the Demographics page."""

from dash import dcc, html
from plotly.graph_objects import Figure


def get_demographics_layout(
    enrollment_by_district: Figure,
    enrollment_by_gender: Figure,
    enrollment_by_ethnicity: Figure,
    enrollment_by_grade: Figure,
    enrollment_by_race: Figure,
) -> html.Div:
    """Build the demographics page layout with all enrollment charts."""
    return html.Div([
        html.Div([
            dcc.Graph(figure=enrollment_by_district, id='enrollment-by-school', className='graph graph-2x'),
            dcc.Graph(figure=enrollment_by_gender, id='enrollment-by-gender', className='graph'),
            dcc.Graph(figure=enrollment_by_ethnicity, id='enrollment-by-ethnicity', className='graph'),
        ], className='graph-flex'),
        html.Div([
            dcc.Graph(figure=enrollment_by_race, id='enrollment-by-race', className='graph'),
            dcc.Graph(figure=enrollment_by_grade, id='enrollment-by-grade', className='graph'),
        ], className='graph-flex'),
    ])