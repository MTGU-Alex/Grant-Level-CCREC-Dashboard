"""
Main application layout including the persistent header and filter box.
"""

from dash import dcc, html
import district_names


def get_app_layout(years: list, renames: dict, group_list: list) -> html.Div:
    """
    Build the top-level application layout.

    Parameters
    ----------
    years : list
        Available academic years for the year filter dropdown.

    Returns
    -------
    html.Div
    """
    return html.Div([
        # State stores
        dcc.Store(id='current-page', data='demographics'),
        dcc.Store(id='filter-store', data={}),
        dcc.Store(id='district-mappings-store', storage_type='memory', data=district_names.load_mappings()),
        dcc.Store(id='district-pending-store', storage_type='memory', data=None),
        dcc.Store(id='school-renames', storage_type='memory', data=renames),

        # Header
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Div([
                            html.Div([
                                html.P('School Year:'),
                                dcc.Dropdown(
                                    id='year-filter',
                                    options=[{'label': y, 'value': y} for y in sorted(years)],
                                    value=sorted(years)[-1],
                                    clearable=False,
                                )
                            ], className='dropdown-and-lable'),
                            html.Div([
                                html.P('School/Group:'),
                                dcc.Dropdown(
                                    id='group-dropdown',
                                    options=[{'label': y, 'value': y} for y in group_list],
                                    value=group_list[0],
                                    clearable=False
                                ),
                            ], className='dropdown-and-lable')
                        ], id='header-dropdowns'),
                        html.H1(id='page-title'),
                    ], id='header-row-1'),
                    html.Div([
                        html.Div([
                            html.H4('Total Service Hours:', className='header-stat-text'),
                            html.Div(id='total-service-hours', className='header-number'),
                        ], className='stat-element'),
                        html.Div([
                            html.H4('Total Students:', className='header-stat-text'),
                            html.Div(id='total-students', className='header-number'),
                        ], className='stat-element'),
                        html.Div([
                            html.H4('Total Schools:', className='header-stat-text'),
                            html.Div(id='total-schools', className='header-number'),
                        ], className='stat-element'),
                    ], id='header-row-2'),
                ], id='header-left'),
                html.Div([
                    html.Button('Demographics', id='demographics-btn', n_clicks=0, className='link-button'),
                    html.Button('Services', id='services-btn', n_clicks=0, className='link-button'),
                    html.Button('Services YTY', id='services-yty-btn', n_clicks=0, className='link-button'),
                    html.Button('Compare', id='compare-btn', n_clicks=0, className='link-button'),
                    html.Button('Objectives', id='objectives-btn', n_clicks=0, className='link-button'),
                    html.Button('Objectives YTY', id='objectives-yty-btn', n_clicks=0, className='link-button'),
                ], id='header-right'),
            ], id='full-header'),

            # Filter box
            html.Div([
                html.H4('Filters:', id='filter-title'),
                html.Div(id='active-filters'),
            ], id='filter-box'),
        ], id='header-wrapper'),

        # Page content area
        html.Div(id='page-contents'),
    ], id='app-container')