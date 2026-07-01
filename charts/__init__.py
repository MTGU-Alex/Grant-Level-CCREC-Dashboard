"""
Chart creation modules for the CCREC Dashboard.
"""

from charts.common import get_empty_figure, safe_chart, configure_theme
from charts.demographics import (
    get_enrollment_by_district,
    get_enrollment_by_gender,
    get_enrollment_by_ethnicity,
    get_enrollment_by_grade,
    get_enrollment_by_race,
)
from charts.services import (
    get_participation_and_avg_time,
    get_participation_by_grade,
    get_service_time_by_grade,
)
from charts.services_yty import (
    get_yty_service_time_by_type,
    get_yty_enrollments,
    get_participation_by_month,
    get_hours_per_student_by_month,
)
from charts.objectives import (
    get_gpa_by_grade,
    get_fafsa,
    get_graduation,
    get_pse,
    get_alg_1,
    get_sankey,
)
from charts.objectives_yty import (
    get_benchmark_line,
    get_yty_gpa,
    get_yty_fafsa,
    get_yty_graduation,
    get_yty_pse,
    get_yty_alg_1,
)
from charts.compare import (
    get_service_time_pie,
    get_service_participation_compare,
    get_gpa_compare,
    get_fafsa_compare,
    get_graduation_compare,
    get_pse_compare,
)