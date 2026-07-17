"""
Central constants, configuration, and mappings for the CCREC Dashboard.
"""

# =========================
# == SERVICE DEFINITIONS ==
# =========================
SERVICE_COLUMNS = [
    'Tutoring/Homework Assistance',
    'Mentoring',
    'Financial Aid Counseling/Advising',
    'Counseling/Advising',
    'College Visit',
    'Job Site Visit/Job Shadowing',
    'Summer Programs',
    'Educational Field Trips',
    'Student Workshops',
    'Parent/Family Workshops',
    'Family Counseling/ Advising',
    'Family College Visit',
    'Other Family Events',
]

SERVICE_CODE_TO_TYPE = {i + 1: name for i, name in enumerate(SERVICE_COLUMNS)}

# ==================
# == GRADE LEVELS ==
# ==================
HIGH_SCHOOL_GRADES = ['9', '10', '11', '12']
MIDDLE_SCHOOL_GRADES = ['7', '8']
ALL_GRADES = MIDDLE_SCHOOL_GRADES + HIGH_SCHOOL_GRADES + ['13']

# ================
# == MONTH DATA ==
# ================
MONTH_MAP = {
    1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
    5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
    9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec',
}

FISCAL_MONTH_ORDER = ['Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec',
                      'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']

# ==============
# == COLORS ====
# ==============
class Colors:
    """Application color palette."""
    # Primary brand colors
    PRIMARY = '#0F5C83'       # Blue
    SECONDARY = '#d75426'     # Orange
    TERTIARY = '#898E3E'      # Green

    # Neutrals
    BLACK = '#231F20'
    DARK_GREY = '#3A3A3C'
    CHARCOAL = '#6E7072'
    GREY = '#818386'
    LIGHT_GREY = '#A8AAAC'
    PALE_GREY = '#D9DADB'
    BACKGROUND = '#F0F1F2'
    WHITE = '#FFFFFF'

    # Chart-specific
    BENCHMARK = '#3A3A3C'
    PLOT_BG = '#F7F8F9'

    # Accent colors for extended palettes
    TAN = '#EDD9B4'
    BROWN = '#6B3F20'
    GOLD = '#C4882A'
    DARK_TEAL = '#2A3D4A'
    SAGE = '#7A8C5E'
    CYAN = '#17becf'


# Chart color sequence (for plotly colorway)
CHART_COLORWAY = [
    Colors.PRIMARY,
    Colors.SECONDARY,
    Colors.TERTIARY,
    Colors.CHARCOAL,
    Colors.TAN,
    Colors.GOLD,
    Colors.DARK_TEAL,
    Colors.LIGHT_GREY,
    Colors.SAGE,
    Colors.DARK_GREY,
]

# =====================
# == CODE MAPPINGS ====
# =====================
CODE_MAPPINGS = {
    'Gender Code': {
        1: 'Female',
        2: 'Male',
        3: 'Unknown',
        4: 'Gender Neutral',
    },
    'Ethnicity Code': {
        0: 'Not Hispanic or Latino',
        1: 'Hispanic or Latino',
        2: 'Unknown',
    },
    'Race Code': {
        1: 'American Indian or Alaskan Native',
        2: 'Asian',
        3: 'Black or African American',
        4: 'Native Hawaiian or Pacific Islander',
        5: 'White',
        6: 'Two or More Races',
        7: 'Unknown',
    },
    'HS Grad Status code': {
        1: 'Graduated',
        2: 'Did Not Graduate',
        3: 'Graduation Status Unknown',
        4: 'N/A',
        5: 'In Grade 13',
    },
    'FAFSA status code': {
        1: 'FAFSA Completed',
        2: 'FAFSA Not Completed',
        3: 'Not Collected',
        4: 'N/A',
    },
    'Algebra 1 Status': {
        1: 'Enrolled and Completed',
        2: 'Enrolled But Not Completed',
        3: 'Not Enrolled or Data Unavailable',
        4: 'N/A',
    },
}

# =========================
# == SERVICE COLUMN MAP ===
# =========================
SERVICE_COLUMN_RENAME = {
    'Service 1 Total': 'Tutoring/Homework Assistance',
    'Service 2 Total': 'Mentoring',
    'Service 3 Total': 'Financial Aid Counseling/Advising',
    'Service 4 Total': 'Counseling/Advising',
    'Service 5 Total': 'College Visit',
    'Service 6 Total': 'Job Site Visit/Job Shadowing',
    'Service 7 Total': 'Summer Programs',
    'Service 8 Total': 'Educational Field Trips',
    'Service 9 Total': 'Student Workshops',
    'Service 10 Total': 'Parent/Family Workshops',
    'Service 11 Total': 'Family Counseling/ Advising',
    'Service 12 Total': 'Family College Visit',
    'Service 13 Total': 'Other Family Events',
    'Algebra 1- Grade of Completion': 'Algebra 1 Status',
    'Algebra 1 Completion': 'Algebra 1 Status'
}

# ============================
# == PAGE CONFIGURATION ======
# ============================
PAGE_CONFIG = {
    'demographics': {'title': 'Demographics', 'uses_year': True},
    'services': {'title': 'Services', 'uses_year': True},
    'services-yty': {'title': 'Services YTY', 'uses_year': False},
    'objectives': {'title': 'Outcomes', 'uses_year': True},
    'objectives-yty': {'title': 'Outcomes YTY', 'uses_year': False},
    'compare': {'title': 'Compare', 'uses_year': True},
}

# ==========================
# == SANKEY LEVEL CONFIG ===
# ==========================
SANKEY_LEVEL_OPTIONS = {
    'GPA': ['School Display Name', 'Grade Level', 'Service Participation Level', 'FAFSA status code', 'Went on College Visit', 'HS Grad Status code', 'Post Secondary Enrollment', 'Post Secondary Graduation'],
    'School Display Name': ['Service Participation Level', 'Grade Level', 'GPA', 'FAFSA status code', 'Went on College Visit', 'HS Grad Status code', 'Post Secondary Enrollment', 'Post Secondary Graduation'],
    'Grade Level': ['Service Participation Level', 'School Display Name', 'GPA', 'FAFSA status code', 'Went on College Visit', 'HS Grad Status code', 'Post Secondary Enrollment', 'Post Secondary Graduation'],
    'Service Participation Level': ['GPA', 'School Display Name', 'FAFSA status code', 'Went on College Visit', 'HS Grad Status code', 'Post Secondary Enrollment', 'Post Secondary Graduation'],
    'FAFSA status code': ['Went on College Visit', 'HS Grad Status code', 'Post Secondary Enrollment', 'Post Secondary Graduation''College Visits and PSE'],
    'Went on College Visit': ['HS Grad Status code', 'Post Secondary Enrollment', 'Post Secondary Graduation', 'College Visits and PSE'],
    'HS Grad Status code': ['Post Secondary Enrollment', 'Post Secondary Graduation', 'College Visits and PSE'],
    'Post Secondary Enrollment': ['Post Secondary Graduation', 'College Visits and PSE'],
    'College Visits and PSE': ['Post Secondary Graduation'],
    'Post Secondary Graduation': [],
    'None': [],
}

# ====================
# == AY COLUMNS ======
# ====================
AY_COLUMNS_TO_KEEP = [
    'High School AY', 'Program Model Code', 'School NCES ID', 'Secondary School Name',
    'National CCREC Student ID', 'Student Type code', 'Gender Code',
    'Ethnicity Code', 'Race Code', 'Grade Level', 'Enrollment Status Code',
    'Service 1 Total', 'Service 2 Total', 'Service 3 Total',
    'Service 4 Total', 'Service 5 Total', 'Service 6 Total',
    'Service 7 Total', 'Service 8 Total', 'Service 9 Total',
    'Service 10 Total', 'Service 11 Total', 'Service 12 Total',
    'Service 13 Total', 'Tutoring/Homework Assistance',
    'Mentoring', 'Financial Aid Counseling/Advising', 'Counseling/Advising',
    'College Visit', 'Job Site Visit/Job Shadowing', 'Summer Programs',
    'Educational Field Trips', 'Student Workshops', 'Parent/Family Workshops',
    'Family Counseling/ Advising', 'Family College Visit',
    'Other Family Events','HS Grad Status code', 'FAFSA status code',
    'Algebra 1- Grade of Completion', 'Algebra 1 Status', 'Algebra 1 Completion', 'Final Term GPA', 'Cumulative GPA',
    'IPEDS numbers of the Schools Visited', 'First College Attended Name',
    'First College Attended IPEDS', 'Graduated Y/N', 'Degree Title',
    'Dual Enrollment', 'Dual Enrollment Degree', 'School Group Name',
]

# Unknown NCES ID placeholder
UNKNOWN_NCES_ID = '000099999999'