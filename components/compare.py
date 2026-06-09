"""Layout for the Compare page."""

from dash import dcc, html
from plotly.graph_objects import Figure


# ── Modal helpers ─────────────────────────────────────────────────────────────

def _drag_item(district: str) -> html.Div:
    """Single draggable district card."""
    return html.Div(district, className='district-drag-item', draggable='true')


def _group_zone(group_name: str, districts: list) -> html.Div:
    """Named group container with a drop zone pre-populated with *districts*."""
    print(group_name)
    print(districts)
    print('----------------')
    items = [_drag_item(d) for d in sorted(districts)]
    items.append(html.Span('Drop districts here', className='drop-hint'))
    return html.Div([
        html.Div([
            html.Span(group_name, className='group-name-label'),
            html.Button('✕', className='remove-group-btn', title=f'Remove group: {group_name}'),
        ], className='group-header'),
        html.Div(items, className='district-drop-zone', **{'data-group': group_name}),
    ], className='district-group')


def _build_rename_modal(all_districts: list, current_mappings: dict) -> html.Div:
    """
    Build the district rename modal overlay.

    Parameters
    ----------
    all_districts : list
        Original (pre-mapping) district names.
    current_mappings : dict
        Saved GROUP format: ``{ group_name: [original_district_1, ...] }``
    """
    # ─── Determine which districts are already assigned to a group ───
    assigned = set()
    for group_name, district_list in current_mappings.items():
        for d in district_list:
            if d in all_districts:
                assigned.add(d)

    unassigned = [d for d in sorted(all_districts) if d not in assigned]

    # ─── Build group zones from the mapping ───
    # Only include districts that actually exist in all_districts
    groups: dict[str, list] = {}
    for group_name, district_list in current_mappings.items():
        valid_districts = [d for d in district_list if d in all_districts]
        if valid_districts:
            groups[group_name] = valid_districts

    # ─── Unassigned pool ───
    pool_items = [_drag_item(d) for d in unassigned]
    pool_items.append(html.Span('Drop districts here', className='drop-hint'))

    # ─── Group zones ───
    group_zones = [_group_zone(name, dists) for name, dists in sorted(groups.items())]

    return html.Div([
        html.Div([
            # Header
            html.Div([
                html.H3('Rename / Group Districts'),
                html.Button(
                    '✕', id='close-rename-modal-btn',
                    className='modal-close-btn', n_clicks=0,
                ),
            ], className='modal-header'),

            html.P(
                'Create a custom group name then drag districts from the '
                'pool on the left into the group.',
                className='modal-instructions',
            ),

            # Add-group input row
            html.Div([
                dcc.Input(
                    id='new-group-name-input',
                    placeholder='New group name…',
                    type='text',
                    className='new-group-input',
                    debounce=False,
                ),
                html.Button(
                    '+ Add Group', id='add-group-btn',
                    className='add-group-btn', n_clicks=0,
                ),
            ], className='new-group-row'),

            # Two-column body
            html.Div([
                # Left – district pool
                html.Div([
                    html.H4('Districts', className='modal-column-header'),
                    html.Div(
                        pool_items,
                        id='unassigned-drop-zone',
                        className='district-drop-zone district-pool',
                    ),
                ], className='modal-column'),

                # Right – custom groups
                html.Div([
                    html.H4('Custom Groups', className='modal-column-header'),
                    html.Div(
                        group_zones,
                        id='groups-container',
                        className='groups-container',
                    ),
                ], className='modal-column'),
            ], className='modal-columns'),

            # Footer
            html.Div([
                html.Button('Save',      id='save-district-rename-btn',   className='btn-primary',   n_clicks=0),
                html.Button('Reset All', id='reset-district-rename-btn',  className='btn-danger',    n_clicks=0),
                html.Button('Close',     id='close-rename-modal-footer-btn', className='btn-secondary', n_clicks=0),
            ], className='modal-footer'),

        ], className='modal-dialog'),
    ], id='district-rename-modal', className='modal-overlay', style={'display': 'none'})


# ── Public layout function ────────────────────────────────────────────────────

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
    all_original_districts: list,
    current_mappings: dict,
) -> html.Div:
    """Build the compare page layout, including the district rename modal."""

    # Conditional GPA radio
    gpa_radio = None
    if objective_selection == 'GPA':
        gpa_radio = dcc.RadioItems(
            ['Cumulative GPA', 'Final Term GPA'],
            gpa_type, inline=True, id='compare-gpa-radio',
        )

    # Objective chart
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
                html.Hr(className='hr-line'),
                # ── Rename Districts button ──────────────────────────────
                html.Button(
                    '✏ Rename Districts',
                    id='open-rename-modal-btn',
                    className='rename-districts-btn',
                    n_clicks=0,
                ),
            ], id='compare-filters-div', className='graph sidebar-filters'),
            dcc.Graph(figure=district_pie, id='district-service-time-split', className='graph'),
            dcc.Graph(figure=program_pie,  id='program-service-time-split',  className='graph'),
        ], className='graph-flex'),
        html.Div([
            dcc.Graph(figure=participation_compare, id='service-participation-compare', className='graph'),
            objective_content,
        ], className='graph-flex'),
        # ── Modal (always in DOM while on compare page; hidden by default) ──
        _build_rename_modal(all_original_districts, current_mappings),
    ])