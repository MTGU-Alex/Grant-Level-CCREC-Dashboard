# "constants.py"  ←  NEW FILE
"""
constants.py
Shared constants used across all CCREC dashboard modules.
Centralising these here eliminates duplication and makes
renaming / extending service types a single-place change.
"""

# ── Service types ──────────────────────────────────────────────────────────────

SERVICE_TYPES: list[str] = [
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

# Integer code → display name (used during data ingestion)
SERVICE_CODE_TO_TYPE: dict[int, str] = {
    1:  'Tutoring/Homework Assistance',
    2:  'Mentoring',
    3:  'Financial Aid Counseling/Advising',
    4:  'Counseling/Advising',
    5:  'College Visit',
    6:  'Job Site Visit/Job Shadowing',
    7:  'Summer Programs',
    8:  'Educational Field Trips',
    9:  'Student Workshops',
    10: 'Parent/Family Workshops',
    11: 'Family Counseling/ Advising',
    12: 'Family College Visit',
    13: 'Other Family Events',
}

# ── Grade levels ───────────────────────────────────────────────────────────────

GRADE_LEVELS_HS: list[str]  = ['9', '10', '11', '12']
GRADE_LEVELS_ALL: list[str] = ['7', '8', '9', '10', '11', '12']

# ── URL / page routing ─────────────────────────────────────────────────────────

# URL pathname  →  internal page key
PAGE_ROUTES: dict[str, str] = {
    '/':               'demographics',
    '/demographics':   'demographics',
    '/services':       'services',
    '/services-yty':   'services-yty',
    '/objectives':     'objectives',
    '/objectives-yty': 'objectives-yty',
    '/compare':        'compare',
}

# Internal page key  →  human-readable title suffix
PAGE_TITLES: dict[str, str] = {
    'demographics':   'Demographics',
    'services':       'Services',
    'services-yty':   'Services Year-to-Year',
    'objectives':     'Objectives',
    'objectives-yty': 'Objectives Year-to-Year',
    'compare':        'District Comparison',
}

# Navigation button component id  →  URL pathname
BUTTON_TO_ROUTE: dict[str, str] = {
    'demographics-btn':   '/demographics',
    'services-btn':       '/services',
    'services-yty-btn':   '/services-yty',
    'objectives-btn':     '/objectives',
    'objectives-yty-btn': '/objectives-yty',
    'compare-btn':        '/compare',
}