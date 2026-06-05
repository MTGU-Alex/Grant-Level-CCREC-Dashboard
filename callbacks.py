"""
Callback registration for the CCREC Dashboard.
Single orchestrator callback with modular handler functions.
"""

from dash import Input, Output, State, html, dcc, ctx, ALL
import pandas as pd

import charts
import components
from constants import SERVICE_COLUMNS, PAGE_CONFIG
from data_service import DashboardData


def _build_filter_tags(filters: dict) -> list:
    """Create removable filter tag components."""
    tags = []
    for key, value in filters.items():
        tags.append(
            html.Span([
                f'{key} = {value}',
                html.Button('×', id={'type': 'remove-filter-btn', 'key': key}, n_clicks=0),
            ], className='filter-tag')
        )
    return tags


def _handle_filter_update(trigger, filters: dict, click_data: dict) -> dict:
    """Process filter additions/removals based on the trigger."""
    filters = filters.copy()

    if isinstance(trigger, dict) and trigger.get('type') == 'remove-filter-btn':
        filters.pop(trigger['key'], None)
    elif trigger == 'enrollment-by-district' and click_data.get('district'):
        filters['District'] = click_data['district']['points'][0]['x']
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
    # Pattern-matching IDs come through as dicts — not a navigation event
    if isinstance(trigger, dict):
        return current_page

    page_map = {
        'demographics-btn': 'demographics',
        'services-btn': 'services',
        'services-yty-btn': 'services-yty',
        'objectives-btn': 'objectives',
        'objectives-yty-btn': 'objectives-yty',
        'compare-btn': 'compare',
    }
    return page_map.get(trigger, current_page)


# =============================
# == PAGE HANDLER FUNCTIONS ===
# =============================

def _render_demographics(filtered_ay: pd.DataFrame) -> html.Div:
    """Render the demographics page."""
    return components.get_demographics_layout(
        charts.get_enrollment_by_district(filtered_ay),
        charts.get_enrollment_by_gender(filtered_ay),
        charts.get_enrollment_by_ethnicity(filtered_ay),
        charts.get_enrollment_by_grade(filtered_ay),
        charts.get_enrollment_by_race(filtered_ay),
    )


def _render_services(filtered_ay: pd.DataFrame, threshold, service_filter) -> html.Div:
    """Render the services page."""
    threshold = threshold or 0
    service_filter = service_filter or SERVICE_COLUMNS.copy()

    return components.get_services_layout(
        threshold,
        SERVICE_COLUMNS,
        service_filter,
        charts.get_participation_and_avg_time(filtered_ay),
        charts.get_participation_by_grade(filtered_ay, threshold, service_filter),
        charts.get_service_time_by_grade(filtered_ay),
    )


def _render_services_yty(
    filtered_ay: pd.DataFrame,
    duration_data: pd.DataFrame,
    threshold, service_filter
) -> html.Div:
    """Render the services YTY page."""
    threshold = threshold or 0
    service_filter = service_filter or SERVICE_COLUMNS.copy()

    return components.get_services_yty_layout(
        threshold,
        SERVICE_COLUMNS,
        service_filter,
        charts.get_yty_service_time_by_type(filtered_ay),
        charts.get_yty_enrollments(filtered_ay),
        charts.get_participation_by_month(filtered_ay, duration_data, threshold, service_filter),
        charts.get_hours_per_student_by_month(filtered_ay, duration_data, service_filter),
    )


def _render_objectives(
    filtered_ay: pd.DataFrame,
    gpa_type, gpa_range, gpa_benchmark,
    l1, l2, l3, l4
) -> html.Div:
    """Render the objectives page."""
    gpa_type = gpa_type or 'Cumulative GPA'
    gpa_low = gpa_range[0] if gpa_range else 2.0
    gpa_high = gpa_range[1] if gpa_range else 3.0
    gpa_benchmark = gpa_benchmark if gpa_benchmark is not None else 2.5
    l1 = l1 or 'GPA'

    gpa_fig = charts.get_gpa_by_grade(filtered_ay, gpa_type, gpa_low, gpa_high, gpa_benchmark)
    l1_opts, l1_sel, l2_opts, l2_sel, l3_opts, l3_sel, l4_opts, l4_sel, sankey_fig, return_message = (
        charts.get_sankey(filtered_ay, l1, l2, l3, l4, gpa_type, gpa_low, gpa_high)
    )

    return components.get_objectives_layout(
        gpa_type, gpa_low, gpa_high, gpa_benchmark, gpa_fig,
        l1_opts, l1_sel, l2_opts, l2_sel, l3_opts, l3_sel, l4_opts, l4_sel,
        sankey_fig, return_message
    )

def _render_objectives_yty(
    filtered_ay: pd.DataFrame, years: list,
    gpa_radio, gpa_bench, gpa_inc, gpa_year,
    fafsa_bench, fafsa_inc, fafsa_year,
    grad_bench, grad_inc, grad_year,
    pse_bench, pse_inc, pse_year
) -> html.Div:
    """Render the objectives YTY page."""
    gpa_type = gpa_radio or 'Cumulative GPA'

    return components.get_objectives_yty_layout(
        gpa_type,
        gpa_bench, gpa_inc, gpa_year,
        fafsa_bench, fafsa_inc, fafsa_year,
        grad_bench, grad_inc, grad_year,
        pse_bench, pse_inc, pse_year,
        years,
        charts.get_yty_gpa(filtered_ay, years, gpa_type, gpa_bench, gpa_inc, gpa_year),
        charts.get_yty_fafsa(filtered_ay, years, fafsa_bench, fafsa_inc, fafsa_year),
        charts.get_yty_graduation(filtered_ay, years, grad_bench, grad_inc, grad_year),
        charts.get_yty_pse(filtered_ay, years, pse_bench, pse_inc, pse_year),
    )

def _render_compare(
    filtered_ay: pd.DataFrame,
    current_district, range_slider, objective, gpa_type
) -> html.Div:
    """Render the compare page."""
    district_list = sorted(filtered_ay['District'].dropna().unique().tolist())
    current_district = current_district or (district_list[0] if district_list else None)

    if not current_district:
        return html.Div("No districts available with current filters.")

    range_low = range_slider[0] if range_slider else 5
    range_high = range_slider[1] if range_slider else 10
    objective = objective or 'GPA'
    gpa_type = gpa_type or 'Cumulative GPA'

    district_ay = filtered_ay[filtered_ay['District'] == current_district]

    district_pie = charts.get_service_time_pie(district_ay, f'Service Time: {current_district}')
    program_pie = charts.get_service_time_pie(filtered_ay, 'Service Time: Program-Wide')
    participation = charts.get_service_participation_compare(filtered_ay, district_ay, range_low, range_high)

    # Objective comparison chart
    match objective:
        case 'GPA':
            hs_students = district_ay[district_ay['Grade Level'].isin(['9', '10', '11', '12'])]
            if len(hs_students) == 0:
                obj_chart = html.Div([html.H4('No GPA data for current selection')], className='graph no-data-container')
            else:
                obj_chart = charts.get_gpa_compare(filtered_ay, district_ay, gpa_type)
        case 'FAFSA':
            seniors = district_ay[district_ay['Grade Level'] == '12']
            if len(seniors) == 0:
                obj_chart = html.Div([html.H4('No FAFSA data for current selection')], className='graph no-data-container')
            else:
                obj_chart = charts.get_fafsa_compare(
                    filtered_ay[filtered_ay['Grade Level'] == '12'], seniors
                )
        case 'Graduation':
            seniors = district_ay[district_ay['Grade Level'] == '12']
            if len(seniors) == 0:
                obj_chart = html.Div([html.H4('No graduation data for current selection')], className='graph no-data-container')
            else:
                obj_chart = charts.get_graduation_compare(
                    filtered_ay[filtered_ay['Grade Level'] == '12'], seniors
                )
        case 'Post Secondary Enrollment':
            seniors = district_ay[district_ay['Grade Level'] == '12']
            if len(seniors) == 0:
                obj_chart = html.Div([html.H4('No PSE data for current selection')], className='graph no-data-container')
            else:
                obj_chart = charts.get_pse_compare(
                    filtered_ay[filtered_ay['Grade Level'] == '12'], seniors
                )
        case _:
            obj_chart = html.Div([html.H4('Select an objective')])

    return components.get_compare_layout(
        district_list, current_district, range_low, range_high,
        objective, gpa_type, district_pie, program_pie, participation, obj_chart,
    )


# ============================
# == CALLBACK REGISTRATION ===
# ============================

def register_callbacks(app, data: DashboardData):
    """Register the main orchestrator callback."""

    @app.callback(
        [
            Output('page-contents', 'children'),
            Output('page-title', 'children'),
            Output('total-service-hours', 'children'),
            Output('total-students', 'children'),
            Output('total-schools', 'children'),
            Output('current-page', 'data'),
            Output('active-filters', 'children'),
            Output('filter-store', 'data'),
        ],
        [
            # Navigation & global
            Input('year-filter', 'value'),
            Input('demographics-btn', 'n_clicks'),
            Input('services-btn', 'n_clicks'),
            Input('services-yty-btn', 'n_clicks'),
            Input('objectives-btn', 'n_clicks'),
            Input('objectives-yty-btn', 'n_clicks'),
            Input('compare-btn', 'n_clicks'),
            # Demographics clicks
            Input('enrollment-by-district', 'clickData', allow_optional=True),
            Input('enrollment-by-gender', 'clickData', allow_optional=True),
            Input('enrollment-by-ethnicity', 'clickData', allow_optional=True),
            Input('enrollment-by-grade', 'clickData', allow_optional=True),
            Input('enrollment-by-race', 'clickData', allow_optional=True),
            Input({'type': 'remove-filter-btn', 'key': ALL}, 'n_clicks', allow_optional=True),
            # Services controls
            Input('services-time-slider', 'value', allow_optional=True),
            Input('services-type-filter', 'value', allow_optional=True),
            # Services YTY controls
            Input('yty-time-slider', 'value', allow_optional=True),
            Input('yty-type-filter', 'value', allow_optional=True),
            # Compare controls
            Input('district-dropdown', 'value', allow_optional=True),
            Input('compare-service-ranges', 'value', allow_optional=True),
            Input('objective-compare-dropdown', 'value', allow_optional=True),
            Input('compare-gpa-radio', 'value', allow_optional=True),
            # Objectives controls
            Input('gpa-radio', 'value', allow_optional=True),
            Input('gpa-range-slider', 'value', allow_optional=True),
            Input('gpa-benchmark-slider', 'value', allow_optional=True),
            Input('sankey-l1-dropdown', 'value', allow_optional=True),
            Input('sankey-l2-dropdown', 'value', allow_optional=True),
            Input('sankey-l3-dropdown', 'value', allow_optional=True),
            Input('sankey-l4-dropdown', 'value', allow_optional=True),
            # Objectives YTY controls
            Input('yty-gpa-radio', 'value', allow_optional=True),
            Input('gpa-yty-benchmark-input', 'value', allow_optional=True),
            Input('gpa-yty-increase-input', 'value', allow_optional=True),
            Input('gpa-yty-benchmark-year', 'value', allow_optional=True),
            Input('fafsa-yty-benchmark-input', 'value', allow_optional=True),
            Input('fafsa-yty-increase-input', 'value', allow_optional=True),
            Input('fafsa-yty-benchmark-year', 'value', allow_optional=True),
            Input('graduation-yty-benchmark-input', 'value', allow_optional=True),
            Input('graduation-yty-increase-input', 'value', allow_optional=True),
            Input('graduation-yty-benchmark-year', 'value', allow_optional=True),
            Input('pse-yty-benchmark-input', 'value', allow_optional=True),
            Input('pse-yty-increase-input', 'value', allow_optional=True),
            Input('pse-yty-benchmark-year', 'value', allow_optional=True),
        ],
        [
            State('filter-store', 'data'),
            State('current-page', 'data'),
        ],
        suppress_callback_exceptions=True,
    )
    def update_page(
        selected_year,
        # Nav buttons (values unused, just triggers)
        _demo_btn, _svc_btn, _svc_yty_btn, _obj_btn, _obj_yty_btn, _cmp_btn,
        # Demographics clicks
        district_click, gender_click, ethnicity_click, grade_click, race_click,
        remove_clicks,
        # Services
        services_threshold, services_type_filter,
        # Services YTY
        yty_threshold, yty_type_filter,
        # Compare
        current_district, compare_range, compare_objective, compare_gpa_type,
        # Objectives
        gpa_type, gpa_range, gpa_benchmark,
        sankey_l1, sankey_l2, sankey_l3, sankey_l4,
        # Objectives YTY
        yty_gpa_radio,
        gpa_bench, gpa_inc, gpa_year,
        fafsa_bench, fafsa_inc, fafsa_year,
        grad_bench, grad_inc, grad_year,
        pse_bench, pse_inc, pse_year,
        # State
        active_filters, current_page
    ):
        trigger = ctx.triggered_id

        # --- Filter Management ---
        click_data = {
            'district': district_click,
            'gender': gender_click,
            'ethnicity': ethnicity_click,
            'grade': grade_click,
            'race': race_click,
        }
        filters = _handle_filter_update(trigger, active_filters or {}, click_data)

        # --- Page Determination ---
        page = _determine_page(trigger, current_page)

        # --- Data Filtering ---
        page_config = PAGE_CONFIG.get(page, {'uses_year': True})
        filtered_ay = data.get_filtered_ay(filters)
        if page_config['uses_year']:
            filtered_ay_for_page = filtered_ay[filtered_ay['High School AY'] == selected_year]
        else:
            filtered_ay_for_page = filtered_ay

        # --- Page Rendering ---
        match page:
            case 'demographics':
                contents = _render_demographics(filtered_ay_for_page)
            case 'services':
                contents = _render_services(filtered_ay_for_page, services_threshold, services_type_filter)
            case 'services-yty':
                duration_data = data.get_filtered_duration_by_student(filters)
                contents = _render_services_yty(filtered_ay_for_page, duration_data, yty_threshold, yty_type_filter)
            case 'objectives':
                contents = _render_objectives(
                    filtered_ay_for_page, gpa_type, gpa_range, gpa_benchmark,
                    sankey_l1, sankey_l2, sankey_l3, sankey_l4,
                )
            case 'objectives-yty':
                contents = _render_objectives_yty(
                    filtered_ay_for_page, data.years,
                    yty_gpa_radio, gpa_bench, gpa_inc, gpa_year,
                    fafsa_bench, fafsa_inc, fafsa_year,
                    grad_bench, grad_inc, grad_year,
                    pse_bench, pse_inc, pse_year,
                )
            case 'compare':
                contents = _render_compare(
                    filtered_ay_for_page, current_district,
                    compare_range, compare_objective, compare_gpa_type,
                )
            case _:
                contents = _render_demographics(filtered_ay_for_page)
                page = 'demographics'

        # --- Header Stats ---
        stats = data.get_header_stats(filters, selected_year)
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
        )