# "callbacks.py"
"""
callbacks.py
Registers all Dash callbacks.  The monolithic original callback is split into
four focused callbacks:

  1. navigate         — updates the URL when a nav button is clicked
  2. update_filters   — manages the filter-store dict and filter pill UI
  3. update_header_stats — refreshes the three KPI numbers in the header
  4. render_page      — builds page content from the current URL + filters

Helper functions (_apply_filters, _build_filter_tags) are module-level so they
can be shared between callbacks without being closures inside register_callbacks.
"""

import pandas as pd
from dash import Input, Output, State, html, dcc, no_update, ctx, ALL

import charts
import components
from constants import SERVICE_TYPES, PAGE_ROUTES, PAGE_TITLES, BUTTON_TO_ROUTE


# ── Module-level helpers ───────────────────────────────────────────────────────

def _apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    """Return a filtered view of *df* based on the active-filters dict."""
    result = df
    for col, val in filters.items():
        result = result[result[col] == val]
    return result


def _build_filter_tags(filters: dict) -> list:
    """Build the list of removable filter-pill Span elements."""
    return [
        html.Span([
            f'{key} = {value}',
            html.Button(
                'x',
                id={'type': 'remove-filter-btn', 'key': key},
                n_clicks=0,
            ),
        ], id='filter-buttons')
        for key, value in filters.items()
    ]


# ── Page-builder helpers ───────────────────────────────────────────────────────

def _get_demographics_page(AY: pd.DataFrame) -> html.Div:
    return components.get_demographics_layout(
        charts.get_enrollment_by_district(AY),
        charts.get_enrollment_by_gender(AY),
        charts.get_enrollment_by_ethnicity(AY),
        charts.get_enrollment_by_grade(AY),
        charts.get_enrollment_by_race(AY),
    )


def _get_services_page(
    AY: pd.DataFrame,
    threshold: float | None,
    services_type_filter: list[str] | None,
) -> html.Div:
    threshold            = threshold or 0
    services_type_filter = services_type_filter or SERVICE_TYPES

    return components.get_services_layout(
        threshold,
        SERVICE_TYPES,
        services_type_filter,
        charts.get_participation_and_avg_time(AY),
        charts.get_participation_by_grade(AY, threshold, services_type_filter),
        charts.get_service_time_by_grade(AY, services_type_filter),
    )


def _get_services_yty_page(
    AY: pd.DataFrame,
    duration_by_student_month_type: pd.DataFrame,
    agg_services_df: pd.DataFrame,
    threshold: float | None,
    service_type_filter: list[str] | None,
) -> html.Div:
    threshold           = threshold or 0
    service_type_filter = service_type_filter or SERVICE_TYPES

    return components.get_yty_layout(
        threshold,
        SERVICE_TYPES,
        service_type_filter,
        charts.get_y_t_y_service_time_by_type(AY),
        charts.get_y_t_y_enrollments(AY),
        charts.get_participation_by_month(AY, duration_by_student_month_type, threshold, service_type_filter),
        charts.get_hours_per_student_by_month(AY, agg_services_df, service_type_filter),
    )


def _get_objectives_page(
    AY: pd.DataFrame,
    gpa_type: str | None,
    gpa_range,
    gpa_benchmark: float | None,
    sankey_l1_option: str | None,
    sankey_l2_option: str | None,
    sankey_l3_option: str | None,
    sankey_l4_option: str | None,
) -> html.Div:
    # NOTE: college_visits data is available in register_callbacks if needed
    # for future sankey levels (e.g. college-visit tracking).
    gpa_type      = gpa_type or 'Cumulative GPA'
    gpa_low       = gpa_range[0] if gpa_range else 2.0
    gpa_high      = gpa_range[1] if gpa_range else 3.0
    gpa_benchmark = gpa_benchmark if gpa_benchmark is not None else 2.5

    (l1_opts, l1_sel, l2_opts, l2_sel,
     l3_opts, l3_sel, l4_opts, l4_sel, sankey) = charts.get_sankey(
        AY, sankey_l1_option, sankey_l2_option, sankey_l3_option, sankey_l4_option,
    )

    return components.get_objectives_layout(
        gpa_type, gpa_low, gpa_high, gpa_benchmark,
        charts.get_gpa_by_grade(AY, gpa_type, gpa_low, gpa_high, gpa_benchmark),
        l1_opts, l1_sel, l2_opts, l2_sel, l3_opts, l3_sel, l4_opts, l4_sel,
        charts.get_alg1_by_grade(AY),
        charts.get_fafsa(AY),
        sankey,
    )


def _get_objective_yty_page(
    AY: pd.DataFrame,
    years: list[str],
    yty_gpa_radio,
    gpa_yty_benchmark_input,
    gpa_yty_increase_input,
    gpa_yty_benchmark_year,
    fafsa_yty_benchmark_input,
    fafsa_yty_increase_input,
    fafsa_yty_benchmark_year,
    graduation_yty_benchmark_input,
    graduation_yty_increase_input,
    graduation_yty_benchmark_year,
    pse_yty_benchmark_input,
    pse_yty_increase_input,
    pse_yty_benchmark_year,
) -> html.Div:
    yty_gpa_radio = yty_gpa_radio or 'Cumulative GPA'

    return components.get_objectives_yty_layout(
        yty_gpa_radio,
        gpa_yty_benchmark_input,  gpa_yty_increase_input,  gpa_yty_benchmark_year,
        fafsa_yty_benchmark_input, fafsa_yty_increase_input, fafsa_yty_benchmark_year,
        graduation_yty_benchmark_input, graduation_yty_increase_input, graduation_yty_benchmark_year,
        pse_yty_benchmark_input, pse_yty_increase_input, pse_yty_benchmark_year,
        years,
        charts.get_yty_gpa(AY, years, yty_gpa_radio, yty_gpa_radio,
                           gpa_yty_benchmark_input, gpa_yty_increase_input, gpa_yty_benchmark_year),
        charts.get_yty_fafsa(AY, years, fafsa_yty_benchmark_input,
                             fafsa_yty_increase_input, fafsa_yty_benchmark_year),
        charts.get_yty_graduation(AY, years, graduation_yty_benchmark_input,
                                  graduation_yty_increase_input, graduation_yty_benchmark_year),
        charts.get_yty_pse(AY, years, pse_yty_benchmark_input,
                           pse_yty_increase_input, pse_yty_benchmark_year),
    )


def _get_compare_page(
    AY: pd.DataFrame,
    current_district: str | None,
    compare_range_slider,
    compare_objective: str | None,
    gpa_type: str | None,
) -> html.Div:
    district_list    = sorted(AY['District'].drop_duplicates().tolist())
    current_district = current_district or district_list[0]
    range_low        = compare_range_slider[0] if compare_range_slider else 5
    range_high       = compare_range_slider[1] if compare_range_slider else 10
    compare_objective = compare_objective or 'GPA'
    gpa_type          = gpa_type or 'Cumulative GPA'

    district_AY  = AY[AY['District'] == current_district]
    seniors_mask = AY['Grade Level'] == '12'
    dist_seniors = district_AY['Grade Level'] == '12'

    match compare_objective:
        case 'GPA':
            objective_compare = charts.get_gpa_compare(AY, district_AY, gpa_type)
        case 'FAFSA':
            objective_compare = charts.get_fafsa_compare(
                AY[seniors_mask], district_AY[dist_seniors])
        case 'Graduation':
            objective_compare = charts.get_graduation_compare(
                AY[seniors_mask], district_AY[dist_seniors])
        case 'Post Secondary Enrollment':
            objective_compare = charts.get_pse_compare(
                AY[seniors_mask], district_AY[dist_seniors])
        case _:
            objective_compare = charts.no_data_figure('Select an objective')

    return components.get_compare_layout(
        district_list, current_district, range_low, range_high,
        compare_objective, gpa_type,
        charts.get_service_time_pie(district_AY, f'Service Time by Category — {current_district}'),
        charts.get_service_time_pie(AY, 'Service Time by Category — Program Wide'),
        charts.get_service_participation_compare(AY, district_AY, range_low, range_high),
        objective_compare,
    )


# ── Callback registration ──────────────────────────────────────────────────────

def register_callbacks(
    app,
    AY_df: pd.DataFrame,
    agg_services_df: pd.DataFrame,
    duration_by_student_month_type: pd.DataFrame,
    college_visits: pd.DataFrame,
) -> None:

    # ── 1. Navigation — update URL when a nav button is clicked ───────────────
    @app.callback(
        Output('url', 'pathname'),
        [Input('demographics-btn',   'n_clicks'),
         Input('services-btn',       'n_clicks'),
         Input('services-yty-btn',   'n_clicks'),
         Input('objectives-btn',     'n_clicks'),
         Input('objectives-yty-btn', 'n_clicks'),
         Input('compare-btn',        'n_clicks')],
        prevent_initial_call=True,
    )
    def navigate(*_):
        return BUTTON_TO_ROUTE.get(ctx.triggered_id, no_update)

    # ── 2. Filter store — handle chart clicks and filter-pill removal ──────────
    @app.callback(
        [Output('filter-store',   'data'),
         Output('active-filters', 'children')],
        [Input('enrollment-by-district',  'clickData', allow_optional=True),
         Input('enrollment-by-gender',    'clickData', allow_optional=True),
         Input('enrollment-by-ethnicity', 'clickData', allow_optional=True),
         Input('enrollment-by-grade',     'clickData', allow_optional=True),
         Input('enrollment-by-race',      'clickData', allow_optional=True),
         Input({'type': 'remove-filter-btn', 'key': ALL}, 'n_clicks')],
        State('filter-store', 'data'),
        prevent_initial_call=True,
    )
    def update_filters(
        district_click, gender_click, ethnicity_click,
        grade_click, race_click, _remove_clicks,
        active_filters: dict,
    ):
        trigger = ctx.triggered_id
        filters = active_filters.copy()

        if isinstance(trigger, dict) and trigger.get('type') == 'remove-filter-btn':
            filters.pop(trigger['key'], None)
        elif trigger == 'enrollment-by-district' and district_click:
            filters['District']      = district_click['points'][0]['x']
        elif trigger == 'enrollment-by-gender' and gender_click:
            filters['Gender Code']   = gender_click['points'][0]['label']
        elif trigger == 'enrollment-by-ethnicity' and ethnicity_click:
            filters['Ethnicity Code']= ethnicity_click['points'][0]['label']
        elif trigger == 'enrollment-by-grade' and grade_click:
            filters['Grade Level']   = str(grade_click['points'][0]['x'])
        elif trigger == 'enrollment-by-race' and race_click:
            filters['Race Code']     = race_click['points'][0]['y']

        return filters, _build_filter_tags(filters)

    # ── 3. Header stats — fire only when year or filter-store changes ──────────
    @app.callback(
        [Output('total-service-hours', 'children'),
         Output('total-students',      'children'),
         Output('total-schools',       'children')],
        [Input('year-filter',   'value'),
         Input('filter-store',  'data')],
    )
    def update_header_stats(selected_year: str, active_filters: dict):
        filtered = _apply_filters(AY_df, active_filters)
        year_df  = filtered[filtered['High School AY'] == selected_year]

        total_hours   = round(year_df[SERVICE_TYPES].sum().sum() / 60, 2)
        total_students = len(year_df)
        total_schools  = len(
            year_df[year_df['School NCES ID'] != '000099999999']['School NCES ID'].drop_duplicates()
        )
        return total_hours, total_students, total_schools

    # ── 4. Page render — fires on URL change, year change, filter change,
    #        or any page-local control change ────────────────────────────────────
    @app.callback(
        [Output('page-contents', 'children'),
         Output('page-title',    'children')],

        [Input('url',          'pathname'),
         Input('year-filter',  'value'),
         Input('filter-store', 'data'),

         # Services page
         Input('services-time-slider', 'value',   allow_optional=True),
         Input('services-type-filter', 'value',   allow_optional=True),
         # Services YTY page
         Input('yty-time-slider',      'value',   allow_optional=True),
         Input('yty-type-filter',      'value',   allow_optional=True),
         # Compare page
         Input('district-dropdown',          'value', allow_optional=True),
         Input('compare-service-ranges',     'value', allow_optional=True),
         Input('objective-compare-dropdown', 'value', allow_optional=True),
         Input('compare-gpa-radio',          'value', allow_optional=True),
         # Objectives page
         Input('gpa-radio',           'value', allow_optional=True),
         Input('gpa-range-slider',    'value', allow_optional=True),
         Input('gpa-benchmark-slider','value', allow_optional=True),
         Input('sankey-l1-dropdown',  'value', allow_optional=True),
         Input('sankey-l2-dropdown',  'value', allow_optional=True),
         Input('sankey-l3-dropdown',  'value', allow_optional=True),
         Input('sankey-l4-dropdown',  'value', allow_optional=True),
         # Objectives YTY page
         Input('yty-gpa-radio',                 'value', allow_optional=True),
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
         Input('pse-yty-benchmark-year',         'value', allow_optional=True)],
    )
    def render_page(
        pathname, selected_year, active_filters,
        # Services
        services_threshold, services_type_filter,
        # Services YTY
        yty_threshold, yty_type_filter,
        # Compare
        current_district, compare_range_slider, compare_objective, compare_gpa_type,
        # Objectives
        gpa_type, gpa_range, gpa_benchmark,
        sankey_l1_option, sankey_l2_option, sankey_l3_option, sankey_l4_option,
        # Objectives YTY
        yty_gpa_radio,
        gpa_yty_benchmark_input,  gpa_yty_increase_input,  gpa_yty_benchmark_year,
        fafsa_yty_benchmark_input, fafsa_yty_increase_input, fafsa_yty_benchmark_year,
        graduation_yty_benchmark_input, graduation_yty_increase_input, graduation_yty_benchmark_year,
        pse_yty_benchmark_input, pse_yty_increase_input, pse_yty_benchmark_year,
    ):
        trigger   = ctx.triggered_id
        page      = PAGE_ROUTES.get(pathname, 'demographics')
        filtered  = _apply_filters(AY_df, active_filters)
        year_df   = filtered[filtered['High School AY'] == selected_year]
        all_years = AY_df['High School AY'].drop_duplicates().tolist()

        match page:
            case 'demographics':
                contents = _get_demographics_page(year_df)
            case 'services':
                contents = _get_services_page(year_df, services_threshold, services_type_filter)
            case 'services-yty':
                contents = _get_services_yty_page(
                    filtered,
                    duration_by_student_month_type.copy(),
                    agg_services_df.copy(),
                    yty_threshold, yty_type_filter,
                )
            case 'objectives':
                contents = _get_objectives_page(
                    year_df, gpa_type, gpa_range, gpa_benchmark,
                    sankey_l1_option, sankey_l2_option, sankey_l3_option, sankey_l4_option,
                )
            case 'objectives-yty':
                contents = _get_objective_yty_page(
                    filtered, all_years, yty_gpa_radio,
                    gpa_yty_benchmark_input,  gpa_yty_increase_input,  gpa_yty_benchmark_year,
                    fafsa_yty_benchmark_input, fafsa_yty_increase_input, fafsa_yty_benchmark_year,
                    graduation_yty_benchmark_input, graduation_yty_increase_input, graduation_yty_benchmark_year,
                    pse_yty_benchmark_input, pse_yty_increase_input, pse_yty_benchmark_year,
                )
            case 'compare':
                contents = _get_compare_page(
                    year_df, current_district, compare_range_slider,
                    compare_objective, compare_gpa_type,
                )
            case _:
                contents = _get_demographics_page(year_df)
                page     = 'demographics'

        # Only update the page title when navigating or on initial load —
        # not when a page-local control (slider, dropdown, etc.) changes.
        if trigger in (None, 'url'):
            page_label = f'CCREC Grant Level Dashboard: {PAGE_TITLES.get(page, page)}'
        else:
            page_label = no_update

        return contents, page_label