"""
Callback registration for the CCREC Dashboard.
Single orchestrator callback with modular handler functions.
"""

from dash import Input, Output, State, html, dcc, ctx, ALL, no_update, clientside_callback
import pandas as pd

import charts
import components
import district_names
from constants import SERVICE_COLUMNS, PAGE_CONFIG
from data_service import DashboardData


# ── Filter helpers ─────────────────────────────────────────────────────────────

def _build_filter_tags(filters: dict) -> list:
    """Create removable filter tag components."""
    return [
        html.Span([
            f'{key} = {value}',
            html.Button('x', id={'type': 'remove-filter-btn', 'key': key}, n_clicks=0),
        ], className='filter-tag')
        for key, value in filters.items()
    ]


def _handle_filter_update(trigger, filters: dict, click_data: dict) -> dict:
    """Process filter additions/removals based on the trigger."""
    filters = filters.copy()

    if isinstance(trigger, dict) and trigger.get('type') == 'remove-filter-btn':
        filters.pop(trigger['key'], None)
    elif trigger == 'enrollment-by-school' and click_data.get('school'):
        filters['School Display Name'] = click_data['school']['points'][0]['x']
    elif trigger == 'enrollment-by-gender' and click_data.get('gender'):
        filters['Gender Code'] = click_data['gender']['points'][0]['label']
    elif trigger == 'enrollment-by-ethnicity' and click_data.get('ethnicity'):
        filters['Ethnicity Code'] = click_data['ethnicity']['points'][0]['label']
    elif trigger == 'enrollment-by-grade' and click_data.get('grade'):
        filters['Grade Level'] = str(click_data['grade']['points'][0]['x'])
    elif trigger == 'enrollment-by-race' and click_data.get('race'):
        filters['Race Code'] = click_data['race']['points'][0]['y']

    return filters


def _determine_page(trigger, current_page: str) -> str:
    """Determine which page to show based on the trigger."""
    if isinstance(trigger, dict):
        return current_page

    return {
        'demographics-btn':   'demographics',
        'services-btn':       'services',
        'services-yty-btn':   'services-yty',
        'objectives-btn':     'objectives',
        'objectives-yty-btn': 'objectives-yty',
        'compare-btn':        'compare',
    }.get(trigger, current_page)


# ── Page renderer functions ─────────────────────────────────────────────────────

def _render_demographics(filtered_ay: pd.DataFrame) -> html.Div:
    return components.get_demographics_layout(
        charts.get_enrollment_by_district(filtered_ay),
        charts.get_enrollment_by_gender(filtered_ay),
        charts.get_enrollment_by_ethnicity(filtered_ay),
        charts.get_enrollment_by_grade(filtered_ay),
        charts.get_enrollment_by_race(filtered_ay),
    )


def _render_services(filtered_ay: pd.DataFrame, threshold, service_filter) -> html.Div:
    threshold      = threshold      or 0
    service_filter = service_filter or SERVICE_COLUMNS.copy()
    return components.get_services_layout(
        threshold, SERVICE_COLUMNS, service_filter,
        charts.get_participation_and_avg_time(filtered_ay),
        charts.get_participation_by_grade(filtered_ay, threshold, service_filter),
        charts.get_service_time_by_grade(filtered_ay),
    )


def _render_services_yty(
    filtered_ay: pd.DataFrame, duration_data: pd.DataFrame,
    threshold, service_filter,
) -> html.Div:
    threshold      = threshold      or 0
    service_filter = service_filter or SERVICE_COLUMNS.copy()
    return components.get_services_yty_layout(
        threshold, SERVICE_COLUMNS, service_filter,
        charts.get_yty_service_time_by_type(filtered_ay),
        charts.get_yty_enrollments(filtered_ay),
        charts.get_participation_by_month(filtered_ay, duration_data, threshold, service_filter),
        charts.get_hours_per_student_by_month(filtered_ay, duration_data, service_filter),
    )


def _render_objectives(
    filtered_ay: pd.DataFrame,
    gpa_type, gpa_range, gpa_benchmark,
    l1, l2, l3, l4,
) -> html.Div:
    gpa_type      = gpa_type or 'Cumulative GPA'
    gpa_low       = gpa_range[0] if gpa_range else 2.0
    gpa_high      = gpa_range[1] if gpa_range else 3.0
    gpa_benchmark = gpa_benchmark if gpa_benchmark is not None else 2.5
    l1            = l1 or 'GPA'

    gpa_fig = charts.get_gpa_by_grade(filtered_ay, gpa_type, gpa_low, gpa_high, gpa_benchmark)
    l1_opts, l1_sel, l2_opts, l2_sel, l3_opts, l3_sel, l4_opts, l4_sel, sankey_fig, msg = (
        charts.get_sankey(filtered_ay, l1, l2, l3, l4, gpa_type, gpa_low, gpa_high)
    )
    return components.get_objectives_layout(
        gpa_type, gpa_low, gpa_high, gpa_benchmark, gpa_fig,
        l1_opts, l1_sel, l2_opts, l2_sel, l3_opts, l3_sel, l4_opts, l4_sel,
        sankey_fig, msg,
    )


def _render_objectives_yty(
    filtered_ay: pd.DataFrame, years: list,
    gpa_radio, gpa_bench, gpa_inc, gpa_year,
    fafsa_bench, fafsa_inc, fafsa_year,
    grad_bench, grad_inc, grad_year,
    pse_bench, pse_inc, pse_year,
) -> html.Div:
    return components.get_objectives_yty_layout(
        gpa_radio or 'Cumulative GPA',
        gpa_bench, gpa_inc, gpa_year,
        fafsa_bench, fafsa_inc, fafsa_year,
        grad_bench, grad_inc, grad_year,
        pse_bench, pse_inc, pse_year,
        years,
        charts.get_yty_gpa(filtered_ay, years, gpa_radio or 'Cumulative GPA', gpa_bench, gpa_inc, gpa_year),
        charts.get_yty_fafsa(filtered_ay, years, fafsa_bench, fafsa_inc, fafsa_year),
        charts.get_yty_graduation(filtered_ay, years, grad_bench, grad_inc, grad_year),
        charts.get_yty_pse(filtered_ay, years, pse_bench, pse_inc, pse_year),
    )


def _render_compare(
    filtered_ay_mapped: pd.DataFrame,
    all_original_districts: list,
    active_mappings: dict,
    current_district, range_slider, objective, gpa_type,
    renames,
) -> html.Div:
    """Render the compare page.

    Parameters
    ----------
    filtered_ay_mapped : pd.DataFrame
        Data with district names already renamed – used for all charts.
    all_original_districts : list
        Original (pre-mapping) district names for the rename modal.
    active_mappings : dict
        Current saved mappings – used to pre-populate modal groups.
    """
    district_list = sorted(filtered_ay_mapped['School Display Name'].dropna().unique().tolist())

    # Reset selection if the previously chosen district was renamed/removed
    if not current_district or current_district not in district_list:
        current_district = district_list[0] if district_list else None

    if not current_district:
        return html.Div('No districts available with current filters.')

    range_low  = range_slider[0] if range_slider else 0
    range_high = range_slider[1] if range_slider else 0
    objective  = objective or 'GPA'
    gpa_type   = gpa_type  or 'Cumulative GPA'

    district_ay = filtered_ay_mapped[filtered_ay_mapped['School Display Name'] == current_district]

    district_pie  = charts.get_service_time_pie(district_ay,       f'Service Time: {current_district}')
    program_pie   = charts.get_service_time_pie(filtered_ay_mapped, 'Service Time: Program-Wide')
    participation = charts.get_service_participation_compare(
        filtered_ay_mapped, district_ay, range_low, range_high
    )

    match objective:
        case 'GPA':
            hs = district_ay[district_ay['Grade Level'].isin(['9', '10', '11', '12'])]
            obj_chart = (
                html.Div([html.H4('No GPA data for current selection')],
                         className='graph no-data-container')
                if len(hs) == 0
                else charts.get_gpa_compare(filtered_ay_mapped, district_ay, gpa_type)
            )
        case 'FAFSA':
            seniors = district_ay[district_ay['Grade Level'] == '12']
            obj_chart = (
                html.Div([html.H4('No FAFSA data for current selection')],
                         className='graph no-data-container')
                if len(seniors) == 0
                else charts.get_fafsa_compare(
                    filtered_ay_mapped[filtered_ay_mapped['Grade Level'] == '12'], seniors
                )
            )
        case 'Graduation':
            seniors = district_ay[district_ay['Grade Level'] == '12']
            obj_chart = (
                html.Div([html.H4('No graduation data for current selection')],
                         className='graph no-data-container')
                if len(seniors) == 0
                else charts.get_graduation_compare(
                    filtered_ay_mapped[filtered_ay_mapped['Grade Level'] == '12'], seniors
                )
            )
        case 'Post Secondary Enrollment':
            seniors = district_ay[district_ay['Grade Level'] == '12']
            obj_chart = (
                html.Div([html.H4('No PSE data for current selection')],
                         className='graph no-data-container')
                if len(seniors) == 0
                else charts.get_pse_compare(
                    filtered_ay_mapped[filtered_ay_mapped['Grade Level'] == '12'], seniors
                )
            )
        case _:
            obj_chart = html.Div([html.H4('Select an objective')])

    return components.get_compare_layout(
        district_list, current_district, range_low, range_high,
        objective, gpa_type,
        district_pie, program_pie, participation, obj_chart,
        all_original_districts,   
        active_mappings,
        renames,
    )


# ── Callback registration ───────────────────────────────────────────────────────

def register_callbacks(app, data: DashboardData):
    """Register all dashboard callbacks."""

    # ------------------------------------------------------------------
    # DISTRICT RENAME  ①  –  open / close the modal  (clientside)
    # ------------------------------------------------------------------
    app.clientside_callback(
        """
        function(open_n, close_n, footer_close_n) {
            const ctx = dash_clientside.callback_context;
            if (!ctx.triggered.length) return window.dash_clientside.no_update;
            const pid = ctx.triggered[0].prop_id;
            if (pid.includes('open-rename-modal-btn')) {
                // Snapshot the drag-and-drop content area so we can restore on close
                var cols = document.querySelector('#district-rename-modal .modal-columns');
                if (cols) {
                    window._modalColumnsSnapshot = cols.innerHTML;
                }
                return {display: 'flex'};
            }
            // Closing without save — restore DOM to pre-interaction state
            var cols = document.querySelector('#district-rename-modal .modal-columns');
            if (cols && window._modalColumnsSnapshot) {
                cols.innerHTML = window._modalColumnsSnapshot;
            }
            window._modalColumnsSnapshot = null;
            return {display: 'none'};
        }
        """,
        Output('district-rename-modal', 'style'),
        Input('open-rename-modal-btn',        'n_clicks', allow_optional=True),
        Input('close-rename-modal-btn',       'n_clicks', allow_optional=True),
        Input('close-rename-modal-footer-btn','n_clicks', allow_optional=True),
        prevent_initial_call=True,
    )

    # ------------------------------------------------------------------
    # DISTRICT RENAME  ②  –  serialise modal DOM → pending store  (clientside)
    # Reads the current state of every custom drop-zone from the live DOM
    # and stores { group_name: [district, ...] } for the server callback.
    # ------------------------------------------------------------------
    app.clientside_callback(
        """
        function(n_clicks) {
            if (!n_clicks) return window.dash_clientside.no_update;

            var result = {};
            var zones = document.querySelectorAll('.district-drop-zone[data-group]');
            zones.forEach(function(zone) {
                var groupName = zone.getAttribute('data-group');
                result[groupName] = [];
                zone.querySelectorAll('.district-drag-item').forEach(function(item) {
                    var name = item.textContent.trim();
                    if (name) result[groupName].push(name);
                });
            });
            // Return {} when no groups exist  →  server will clear all mappings
            return result;
        }
        """,
        Output('district-pending-store', 'data'),
        Input('save-district-rename-btn', 'n_clicks', allow_optional=True),
        prevent_initial_call=True,
    )

    # ------------------------------------------------------------------
    # DISTRICT RENAME  ③  –  persist or reset mappings  (server-side)
    # A single callback handles both Save and Reset to avoid the need
    # for allow_duplicate on the output store.
    # ------------------------------------------------------------------
    '''
    @app.callback(
        Output('district-mappings-store', 'data'),
        Input('district-pending-store',      'data'),
        Input('reset-district-rename-btn',   'n_clicks', allow_optional=True),
        prevent_initial_call=True,
    )
    def _manage_district_mappings(pending_groups, reset_clicks):
        """Save groups→districts mapping to disk or reset all mappings."""
        trigger = ctx.triggered_id

        if trigger == 'reset-district-rename-btn':
            if not reset_clicks:
                return no_update
            district_names.reset_mappings()
            return {}

        if trigger == 'district-pending-store':
            # pending_groups is None only on the very first (suppressed) call
            if pending_groups is None:
                return no_update
            # Flatten { group: [districts] } → { district: group }
            flat: dict = {}
            for group_name, districts in pending_groups.items():
                for d in (districts or []):
                    flat[d] = group_name
            district_names.save_mappings(flat)
            return flat

        return no_update
    '''
        
    # ------------------------------------------------------------------
    # MAIN ORCHESTRATOR CALLBACK
    # ------------------------------------------------------------------
    @app.callback(
        [
            Output('page-contents',        'children'),
            Output('page-title',           'children'),
            Output('total-service-hours',  'children'),
            Output('total-students',       'children'),
            Output('total-schools',        'children'),
            Output('current-page',         'data'),
            Output('active-filters',       'children'),
            Output('filter-store',         'data'),
            Output('school-renames',       'data')
        ],
        [
            # Navigation & global
            Input('year-filter',        'value'),
            Input('demographics-btn',   'n_clicks'),
            Input('services-btn',       'n_clicks'),
            Input('services-yty-btn',   'n_clicks'),
            Input('objectives-btn',     'n_clicks'),
            Input('objectives-yty-btn', 'n_clicks'),
            Input('compare-btn',        'n_clicks'),
            # district mappings – triggers re-render when saved/reset 
            Input('district-mappings-store', 'data'),
            # Demographics chart clicks
            Input('enrollment-by-school',  'clickData', allow_optional=True),
            Input('enrollment-by-gender',    'clickData', allow_optional=True),
            Input('enrollment-by-ethnicity', 'clickData', allow_optional=True),
            Input('enrollment-by-grade',     'clickData', allow_optional=True),
            Input('enrollment-by-race',      'clickData', allow_optional=True),
            Input({'type': 'remove-filter-btn', 'key': ALL}, 'n_clicks', allow_optional=True),
            # Services controls
            Input('services-time-slider', 'value', allow_optional=True),
            Input('services-type-filter', 'value', allow_optional=True),
            # Services YTY controls
            Input('yty-time-slider',   'value', allow_optional=True),
            Input('yty-type-filter',   'value', allow_optional=True),
            # Compare controls
            Input('district-dropdown',          'value', allow_optional=True),
            Input('compare-service-ranges',     'value', allow_optional=True),
            Input('objective-compare-dropdown', 'value', allow_optional=True),
            Input('compare-gpa-radio',          'value', allow_optional=True),
            Input('reset-district-rename-btn',  'n_clicks', allow_optional=True),
            Input('district-pending-store',     'data'),
            # Objectives controls
            Input('gpa-radio',            'value', allow_optional=True),
            Input('gpa-range-slider',     'value', allow_optional=True),
            Input('gpa-benchmark-slider', 'value', allow_optional=True),
            Input('sankey-l1-dropdown',   'value', allow_optional=True),
            Input('sankey-l2-dropdown',   'value', allow_optional=True),
            Input('sankey-l3-dropdown',   'value', allow_optional=True),
            Input('sankey-l4-dropdown',   'value', allow_optional=True),
            # Objectives YTY controls
            Input('yty-gpa-radio',                  'value', allow_optional=True),
            Input('gpa-yty-benchmark-input',        'value', allow_optional=True),
            Input('gpa-yty-increase-input',         'value', allow_optional=True),
            Input('gpa-yty-benchmark-year',         'value', allow_optional=True),
            Input('fafsa-yty-benchmark-input',      'value', allow_optional=True),
            Input('fafsa-yty-increase-input',       'value', allow_optional=True),
            Input('fafsa-yty-benchmark-year',       'value', allow_optional=True),
            Input('graduation-yty-benchmark-input', 'value', allow_optional=True),
            Input('graduation-yty-increase-input',  'value', allow_optional=True),
            Input('graduation-yty-benchmark-year',  'value', allow_optional=True),
            Input('pse-yty-benchmark-input',        'value', allow_optional=True),
            Input('pse-yty-increase-input',         'value', allow_optional=True),
            Input('pse-yty-benchmark-year',         'value', allow_optional=True),
        ],
        [
            State('filter-store',   'data'),
            State('current-page',   'data'),
            State('school-renames', 'data')
        ],
        suppress_callback_exceptions=True,
    )
    def update_page(
        selected_year,
        _demo_btn, _svc_btn, _svc_yty_btn, _obj_btn, _obj_yty_btn, _cmp_btn,
        district_mappings,                    
        school_click, gender_click, ethnicity_click, grade_click, race_click,
        remove_clicks,
        services_threshold, services_type_filter,
        yty_threshold, yty_type_filter,
        current_district, compare_range, compare_objective, compare_gpa_type, reset_schools, pending_districts_store,
        gpa_type, gpa_range, gpa_benchmark,
        sankey_l1, sankey_l2, sankey_l3, sankey_l4,
        yty_gpa_radio,
        gpa_bench, gpa_inc, gpa_year,
        fafsa_bench, fafsa_inc, fafsa_year,
        grad_bench, grad_inc, grad_year,
        pse_bench, pse_inc, pse_year,
        active_filters, current_page, renames
    ):
        trigger = ctx.triggered_id

        # ── Filters ──────────────────────────────────────────────────────
        click_data = {
            'school':  school_click,
            'gender':    gender_click,
            'ethnicity': ethnicity_click,
            'grade':     grade_click,
            'race':      race_click,
        }
        filters = _handle_filter_update(trigger, active_filters or {}, click_data)

        # ── Page ─────────────────────────────────────────────────────────
        page = _determine_page(trigger, current_page)

        # ── Apply district renames ────────────────────────────────────────
        if trigger == 'district-pending-store' and pending_districts_store:
            flattened = {}
            for group_name, districts in pending_districts_store.items():
                for d in (districts or []):
                    flattened[d] = group_name
            active_mappings = flattened
        elif trigger == 'reset-district-rename-btn':
            active_mappings = {}
        else:
            active_mappings = renames

        renames = active_mappings or {}
        data.group_schools(renames)

        # ── Raw data (no district mapping applied yet) ───────────────────
        page_config = PAGE_CONFIG.get(page, {'uses_year': True})
        filtered_ay_raw = data.get_filtered_ay(filters)
        if page_config['uses_year']:
            filtered_ay_raw_page = filtered_ay_raw[
                filtered_ay_raw['High School AY'] == selected_year
            ]
        else:
            filtered_ay_raw_page = filtered_ay_raw

        # ── Render ───────────────────────────────────────────────────────
        match page:
            case 'demographics':
                contents = _render_demographics(filtered_ay_raw_page)

            case 'services':
                contents = _render_services(
                    filtered_ay_raw_page, services_threshold, services_type_filter
                )

            case 'services-yty':
                duration_data = data.get_filtered_duration_by_student(filters)
                contents = _render_services_yty(
                    filtered_ay_raw_page, duration_data, yty_threshold, yty_type_filter
                )

            case 'objectives':
                contents = _render_objectives(
                    filtered_ay_raw_page, gpa_type, gpa_range, gpa_benchmark,
                    sankey_l1, sankey_l2, sankey_l3, sankey_l4,
                )

            case 'objectives-yty':
                contents = _render_objectives_yty(
                    filtered_ay_raw_page, data.years,
                    yty_gpa_radio,
                    gpa_bench, gpa_inc, gpa_year,
                    fafsa_bench, fafsa_inc, fafsa_year,
                    grad_bench, grad_inc, grad_year,
                    pse_bench, pse_inc, pse_year,
                )

            case 'compare':
                # Original (pre-mapping) district names for the rename modal
                all_original = sorted(
                    filtered_ay_raw_page['Secondary School Name'].dropna().unique().tolist()
                )
                contents = _render_compare(
                    filtered_ay_raw_page,
                    all_original,
                    active_mappings,
                    current_district, compare_range, compare_objective, compare_gpa_type,
                    renames,
                )

            case _:
                contents = _render_demographics(filtered_ay_raw_page)
                page = 'demographics'

        # ── Header stats ─────────────────────────────────────────────────
        stats      = data.get_header_stats(filters, selected_year)
        page_title = f"CCREC Dashboard: {PAGE_CONFIG.get(page, {}).get('title', page)}"
        filter_tags = _build_filter_tags(filters)

        return (
            contents,
            page_title,
            stats['total_hours'],
            stats['total_students'],
            stats['total_schools'],
            page,
            filter_tags,
            filters,
            renames,
        )

