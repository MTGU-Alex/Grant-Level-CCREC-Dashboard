"""Layout for the Objectives Year-to-Year page."""

from dash import dcc, html
from plotly.graph_objects import Figure


def get_objectives_yty_layout(
    gpa_type: str,
    gpa_benchmark, gpa_increase, gpa_year,
    fafsa_benchmark, fafsa_increase, fafsa_year,
    graduation_benchmark, graduation_increase, graduation_year,
    pse_benchmark, pse_increase, pse_year,
    alg_1_benchmark, alg_1_increase, alg_1_year,
    years: list,
    avg_gpa_fig: Figure,
    fafsa_fig: Figure,
    graduation_fig: Figure,
    pse_fig: Figure,
    alg_1_fig: Figure,
) -> html.Div:
    """Build the objectives YTY page layout."""
    sorted_years = sorted(years)
    default_year = sorted_years[0] if sorted_years else None

    options_config = [
        {
            'id': 'gpa-yty',
            'title': 'GPA',
            'benchmark': gpa_benchmark,
            'increase': gpa_increase,
            'year': gpa_year or default_year,
            'placeholder': 2.5,
            'extra': html.Div([
                dcc.RadioItems(
                    ['Cumulative GPA', 'Final Term GPA'],
                    gpa_type, inline=True, id='yty-gpa-radio',
                ),
            ], id='yty-gpa-radio-div'),
        },
        {
            'id': 'fafsa-yty',
            'title': 'FAFSA',
            'benchmark': fafsa_benchmark,
            'increase': fafsa_increase,
            'year': fafsa_year or default_year,
            'placeholder': 80,
            'extra': None,
        },
        {
            'id': 'graduation-yty',
            'title': 'Graduation',
            'benchmark': graduation_benchmark,
            'increase': graduation_increase,
            'year': graduation_year or default_year,
            'placeholder': 60,
            'extra': None,
        },
        {
            'id': 'pse-yty',
            'title': 'PSE',
            'benchmark': pse_benchmark,
            'increase': pse_increase,
            'year': pse_year or default_year,
            'placeholder': 40,
            'extra': None,
        },
        {
            'id': 'alg-1-yty',
            'title': 'Algebra 1',
            'benchmark': alg_1_benchmark,
            'increase': alg_1_increase,
            'year': alg_1_year or default_year,
            'placeholder': 40,
            'extra': None,
        },
    ]

    option_divs = []
    for cfg in options_config:
        children = [html.H3(cfg['title'], className='yty-option-title')]
        if cfg['extra']:
            children.append(cfg['extra'])
        children.extend([
            html.Div([
                html.H4('Benchmark:', className='options-text'),
                dcc.Input(
                    id=f"{cfg['id']}-benchmark-input",
                    type='number', placeholder=0,
                    value=cfg['benchmark'], className='options-input',
                ),
            ], className='yty-benchmark-div'),
            html.Div([
                html.H4('Yearly Increase:', className='options-text'),
                dcc.Input(
                    id=f"{cfg['id']}-increase-input",
                    type='number', placeholder=0,
                    value=cfg['increase'], className='options-input',
                ),
            ], className='yty-increase-div'),
            html.Div([
                html.H4('Benchmark Year:', className='options-text'),
                dcc.Dropdown(
                    id=f"{cfg['id']}-benchmark-year",
                    options=[{'label': y, 'value': y} for y in sorted_years],
                    value=cfg['year'], clearable=False, className='options-input',
                ),
            ], className='yty-benchmark-year-div'),
        ])
        option_divs.append(
            html.Div(children, id=f"{cfg['id']}-options-div", className='yty-option-div')
        )

    return html.Div([
        html.Div([
            html.Div(option_divs, id='objectives-yty-options-parent-div', className='graph'),
            dcc.Graph(figure=avg_gpa_fig, id='average-gpa-by-year', className='graph graph-3x'),
        ], className='graph-flex'),
        html.Div([
            dcc.Graph(figure=fafsa_fig, id='fafsa-by-year', className='graph'),
            dcc.Graph(figure=graduation_fig, id='graduation-by-year', className='graph'),
        ], className='graph-flex'),
        html.Div([
            dcc.Graph(figure=pse_fig, id='pse-by-year', className='graph'),
            dcc.Graph(figure=alg_1_fig, id='alg-1-by-year', className='graph'),
        ], className='graph-flex'),
    ])