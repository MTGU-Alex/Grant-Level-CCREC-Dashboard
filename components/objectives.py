# "objectives.py"
"""Layout for the Objectives page."""

from dash import dcc, html
from plotly.graph_objects import Figure


def get_objectives_layout(
    gpa_type: str,
    gpa_low: float,
    gpa_high: float,
    gpa_benchmark: float,
    gpa_by_grade: Figure,
    fafsa: Figure,
    graduation: Figure,
    pse: Figure,
    alg_1: Figure,
    l1_options: list,
    l1_selection: str,
    l2_options: list,
    l2_selection: str,
    l3_options: list,
    l3_selection: str,
    l4_options: list,
    l4_selection: str,
    sankey_fig: Figure,
    return_message: str
) -> html.Div:
    """Build the objectives page layout."""
    return html.Div([
        # ── Row 1: sidebar filters + GPA chart ──────────────────────────────
        html.Div([
            html.Div([
                # GPA controls only (Sankey controls moved below)
                html.Div([
                    dcc.RadioItems(
                        ['Cumulative GPA', 'Final Term GPA'],
                        gpa_type, inline=True, id='gpa-radio',
                    ),
                ], id='gpa-radio-div'),
                html.Div([
                    html.H4('GPA Band Ranges:', className='control-label'),
                    dcc.RangeSlider(0, 4, 0.1, value=[gpa_low, gpa_high], id='gpa-range-slider'),
                ], className='control-group'),
                html.Div([
                    html.H4(f'GPA Benchmark: {gpa_benchmark}', className='filter-label'),
                    dcc.Slider(id='gpa-benchmark-slider', min=0, max=4, step=0.1, value=gpa_benchmark),
                ], className='control-group'),
            ], id='objectives-filters', className='graph sidebar-filters'),
            dcc.Graph(figure=gpa_by_grade, id='gpa-by-grade', className='graph graph-3x'),
        ], className='graph-flex'),

        # ── Row 2: FAFSA + Graduation ────────────────────────────────────────
        html.Div([
            dcc.Graph(figure=fafsa, id='fafsa', className='graph'),
            dcc.Graph(figure=graduation, id='graduation', className='graph'),
        ], className='graph-flex'),

        # ── Row 3: PSE + Algebra 1 ───────────────────────────────────────────
        html.Div([
            dcc.Graph(figure=pse, id='pse', className='graph'),
            dcc.Graph(figure=alg_1, id='alg_1', className='graph'),
        ], className='graph-flex'),

        # ── Sankey level controls (horizontal row) ───────────────────────────
        html.Div([
            _sankey_level_row('Level 1:', 'sankey-l1-dropdown', l1_options, l1_selection),
            _sankey_level_row('Level 2:', 'sankey-l2-dropdown', l2_options, l2_selection),
            _sankey_level_row('Level 3:', 'sankey-l3-dropdown', l3_options, l3_selection),
            _sankey_level_row('Level 4:', 'sankey-l4-dropdown', l4_options, l4_selection),
            html.P(return_message, id='sankey-return-message'),
        ], id='sankey-controls-row'),

        # ── Row 4: Sankey diagram ─────────────────────────────────────────────
        html.Div([
            dcc.Graph(figure=sankey_fig, id='graduation-and-pse', className='graph'),
        ], className='graph-flex'),
    ])


def _sankey_level_row(label: str, dropdown_id: str, options: list, value: str) -> html.Div:
    """Create a single sankey level control row."""
    return html.Div([
        html.P(label, className='sankey-level-label'),
        html.Div([
            dcc.Dropdown(
                id=dropdown_id,
                options=[{'label': c, 'value': c} for c in sorted(options)] if options else [],
                value=value,
                clearable=False,
                className='sankey-drop-down',
            ),
        ], className='sankey-drop-down-div'),
    ], className='sankey-level-flex')