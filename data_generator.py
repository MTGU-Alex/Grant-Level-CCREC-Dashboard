"""
CCREC Practice Data Generator
==============================
Generates realistic AYData and ServiceData CSV files for dashboard testing.

Outputs:
    - practice_AYData.csv (~25,000 rows)
    - practice_ServiceData.csv (~300,000-400,000 rows)

Run:
    python generate_practice_data.py
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import os

print("=" * 60)
print("CCREC Practice Data Generator")
print("=" * 60)

# ============================
# REPRODUCIBILITY
# ============================
np.random.seed(42)
random.seed(42)

# ============================
# CONFIGURATION
# ============================

YEARS = ['2020-2021', '2021-2022', '2022-2023', '2023-2024', '2024-2025']
TARGET_STUDENTS_PER_YEAR = 5000
ATTRITION_RATE = 0.10
RETENTION_RATE = 0.03
SERVICE_PARTICIPATION_RATE = 0.85  # 85% of students get at least some service

# ============================
# DISTRICT & SCHOOL CONFIG
# ============================

DISTRICTS = {
    1: {
        'name': 'Riverside Unified',
        'size': 'large',
        'target_pct': 0.150,
        'schools': {
            990000100001: {'grades': (7, 8), 'name': 'Riverside Middle School'},
            990000100002: {'grades': (9, 12), 'name': 'Riverside High School'},
        },
    },
    2: {
        'name': 'Central City Schools',
        'size': 'large',
        'target_pct': 0.144,
        'schools': {
            990000200001: {'grades': (7, 8), 'name': 'Central City Middle'},
            990000200002: {'grades': (9, 12), 'name': 'Central City High'},
        },
    },
    3: {
        'name': 'Westfield Public Schools',
        'size': 'large',
        'target_pct': 0.138,
        'schools': {
            990000300001: {'grades': (7, 8), 'name': 'Westfield Middle'},
            990000300002: {'grades': (9, 12), 'name': 'Westfield High'},
        },
    },
    4: {
        'name': 'Oak Valley School District',
        'size': 'medium',
        'target_pct': 0.104,
        'schools': {
            990000400001: {'grades': (7, 12), 'name': 'Oak Valley Academy'},
        },
    },
    5: {
        'name': 'Prairie View ISD',
        'size': 'medium',
        'target_pct': 0.098,
        'schools': {
            990000500001: {'grades': (7, 12), 'name': 'Prairie View School'},
        },
    },
    6: {
        'name': 'Mountain Ridge Schools',
        'size': 'medium',
        'target_pct': 0.092,
        'schools': {
            990000600001: {'grades': (7, 12), 'name': 'Mountain Ridge Academy'},
        },
    },
    7: {
        'name': 'Lakewood Consolidated',
        'size': 'medium',
        'target_pct': 0.086,
        'schools': {
            990000700001: {'grades': (7, 12), 'name': 'Lakewood School'},
        },
    },
    8: {
        'name': 'Pinecrest Schools',
        'size': 'small',
        'target_pct': 0.070,
        'schools': {
            990000800001: {'grades': (7, 12), 'name': 'Pinecrest School'},
        },
    },
    9: {
        'name': 'Cedar Hills SD',
        'size': 'small',
        'target_pct': 0.064,
        'schools': {
            990000900001: {'grades': (7, 12), 'name': 'Cedar Hills School'},
        },
    },
    10: {
        'name': 'Brookside Academy',
        'size': 'small',
        'target_pct': 0.054,
        'schools': {
            990001000001: {'grades': (7, 12), 'name': 'Brookside Academy'},
        },
    },
}

# Validate district percentages sum to 1
total_pct = sum(d['target_pct'] for d in DISTRICTS.values())
assert abs(total_pct - 1.0) < 0.01, f"District percentages sum to {total_pct}, expected 1.0"

# ============================
# DEMOGRAPHIC DISTRIBUTIONS
# ============================

# Race: 1=Native, 2=Asian, 3=Black, 4=Hawaiian/PI, 5=White, 6=Two+, 7=Unknown
RACE_PROBS = [0.05, 0.03, 0.28, 0.03, 0.37, 0.05, 0.19]
RACE_CODES = [1, 2, 3, 4, 5, 6, 7]

# Gender: 1=Female, 2=Male, 3=Unknown, 4=Gender Neutral
GENDER_PROBS = [0.55, 0.42, 0.02, 0.01]
GENDER_CODES = [1, 2, 3, 4]

# Ethnicity: 0=Not Hispanic, 1=Hispanic, 2=Unknown
ETHNICITY_PROBS = [0.55, 0.40, 0.05]
ETHNICITY_CODES = [0, 1, 2]

# ============================
# SERVICE CONFIGURATION
# ============================

# Service code → (participation_rate, avg_total_hours_for_participants, typical_session_minutes, avg_sessions_per_year)
SERVICE_CONFIG = {
    1: {'name': 'Tutoring/Homework Assistance', 'part_rate': 0.20, 'avg_hours': 2.0, 'session_min': 35, 'sessions': 3.4},
    2: {'name': 'Mentoring', 'part_rate': 0.15, 'avg_hours': 1.0, 'session_min': 30, 'sessions': 2.0},
    3: {'name': 'Financial Aid Counseling/Advising', 'part_rate': 0.32, 'avg_hours': 1.5, 'session_min': 25, 'sessions': 3.6},
    4: {'name': 'Counseling/Advising', 'part_rate': 0.50, 'avg_hours': 3.0, 'session_min': 30, 'sessions': 6.0},
    5: {'name': 'College Visit', 'part_rate': 0.25, 'avg_hours': 5.0, 'session_min': 150, 'sessions': 2.0},
    6: {'name': 'Job Site Visit/Job Shadowing', 'part_rate': 0.04, 'avg_hours': 4.5, 'session_min': 135, 'sessions': 2.0},
    7: {'name': 'Summer Programs', 'part_rate': 0.015, 'avg_hours': 6.5, 'session_min': 195, 'sessions': 2.0},
    8: {'name': 'Educational Field Trips', 'part_rate': 0.025, 'avg_hours': 5.5, 'session_min': 165, 'sessions': 2.0},
    9: {'name': 'Student Workshops', 'part_rate': 0.40, 'avg_hours': 2.5, 'session_min': 50, 'sessions': 3.0},
    10: {'name': 'Parent/Family Workshops', 'part_rate': 0.07, 'avg_hours': 3.5, 'session_min': 90, 'sessions': 2.3},
    11: {'name': 'Family Counseling/ Advising', 'part_rate': 0.10, 'avg_hours': 0.5, 'session_min': 30, 'sessions': 1.0},
    12: {'name': 'Family College Visit', 'part_rate': 0.005, 'avg_hours': 4.0, 'session_min': 120, 'sessions': 2.0},
    13: {'name': 'Other Family Events', 'part_rate': 0.003, 'avg_hours': 0.5, 'session_min': 30, 'sessions': 1.0},
}

# Monthly distribution of services (academic year: Jul=start, Jun=end)
# Weights for when services occur (different for summer vs academic services)
ACADEMIC_MONTH_WEIGHTS = {
    7: 0.02, 8: 0.03, 9: 0.11, 10: 0.11, 11: 0.09,
    12: 0.04, 1: 0.12, 2: 0.14, 3: 0.12, 4: 0.11, 5: 0.08, 6: 0.03,
}

SUMMER_MONTH_WEIGHTS = {
    6: 0.20, 7: 0.50, 8: 0.30,
}

# Services that are summer-concentrated
SUMMER_SERVICES = {7}  # Summer Programs

# Grade-specific service adjustments
# Financial Aid and College Visit more common for upper grades
GRADE_SERVICE_MULTIPLIERS = {
    # service_code: {grade: multiplier}
    3: {7: 0.1, 8: 0.2, 9: 0.5, 10: 0.7, 11: 1.2, 12: 1.8},  # Financial Aid
    5: {7: 0.1, 8: 0.2, 9: 0.5, 10: 0.8, 11: 1.3, 12: 1.6},  # College Visit
    6: {7: 0.0, 8: 0.1, 9: 0.5, 10: 1.0, 11: 1.5, 12: 1.5},  # Job Site
    1: {7: 1.3, 8: 1.3, 9: 1.2, 10: 1.0, 11: 0.8, 12: 0.6},  # Tutoring (more for younger)
}

# ============================
# COLLEGE DATA
# ============================

COLLEGES = [
    ('State University', '100001'),
    ('Community College of the Valley', '100002'),
    ('Technical Institute', '100003'),
    ('Liberal Arts College', '100004'),
    ('City University', '100005'),
    ('Regional State College', '100006'),
    ('Westfield Community College', '100007'),
    ('Mountain State University', '100008'),
    ('Prairie Community College', '100009'),
    ('Riverside Technical College', '100010'),
    ('Central State University', '100011'),
    ('Oak Valley Community College', '100012'),
    ('Lakewood College', '100013'),
    ('Cedar Hills Community College', '100014'),
    ('Brookside State University', '100015'),
    ('Northern University', '100016'),
    ('Southern Technical', '100017'),
    ('Eastern State College', '100018'),
    ('Western Community College', '100019'),
    ('Metropolitan University', '100020'),
]

# Additional IPEDS codes for college visits (includes the enrollment colleges + more)
COLLEGE_VISIT_IPEDS = [f'{100000 + i}' for i in range(1, 51)]


# ============================
# HELPER FUNCTIONS
# ============================

def generate_student_id():
    """Generate a unique 8-digit student ID."""
    generate_student_id.counter += 1
    return 10000000 + generate_student_id.counter


generate_student_id.counter = 0


def assign_district_and_school(grade, district_id):
    """Assign appropriate school NCES ID based on grade and district."""
    district = DISTRICTS[district_id]
    schools = district['schools']

    for nces_id, info in schools.items():
        grade_min, grade_max = info['grades']
        if grade_min <= grade <= grade_max:
            return nces_id

    # Fallback: first school
    return list(schools.keys())[0]


def generate_correlated_scores(n):
    """
    Generate correlated academic and engagement scores.
    Returns two arrays in [0.05, 0.95] range with ~0.35 correlation.
    """
    # Generate correlated normals
    z1 = np.random.normal(0, 1, n)
    z2 = 0.35 * z1 + np.sqrt(1 - 0.35 ** 2) * np.random.normal(0, 1, n)

    # Convert to [0,1] via logistic function (approximates normal CDF)
    academic = 1 / (1 + np.exp(-z1 * 0.8))
    engagement = 1 / (1 + np.exp(-z2 * 0.8))

    # Clip to avoid extreme values
    academic = np.clip(academic, 0.05, 0.95)
    engagement = np.clip(engagement, 0.05, 0.95)

    return academic, engagement


def calculate_gpa(academic_score, noise_std=0.25):
    """Convert academic score to GPA (0-4 scale)."""
    # Map [0.05, 0.95] → approximately [0.8, 3.9]
    gpa = 0.7 + academic_score * 3.2 + np.random.normal(0, noise_std)
    return np.clip(gpa, 0.5, 4.0)


def get_year_start(academic_year):
    """Get the start year from academic year string."""
    return int(academic_year.split('-')[0])


def get_service_dates(academic_year, month, n_sessions):
    """Generate random service dates within a given month of the academic year."""
    year_start = get_year_start(academic_year)

    if month >= 7:
        year = year_start
    else:
        year = year_start + 1

    # Days in month (simplified)
    days_in_month = {
        1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31,
    }

    max_day = days_in_month[month]
    dates = []
    for _ in range(n_sessions):
        day = random.randint(1, max_day)
        try:
            dates.append(datetime(year, month, day))
        except ValueError:
            dates.append(datetime(year, month, max_day))

    return dates


# ============================
# STUDENT LIFECYCLE MANAGEMENT
# ============================

print("\n[1/5] Generating student cohorts...")

# Master student registry
# Each student has fixed attributes assigned on creation
student_registry = {}  # student_id → {demographics, scores, district, etc.}

# Track active students per year
year_rosters = {}  # year → list of (student_id, grade)

# Grade distribution for initial cohort (weighted toward 9-11)
INITIAL_GRADE_WEIGHTS = {7: 0.14, 8: 0.14, 9: 0.18, 10: 0.18, 11: 0.18, 12: 0.18}

# New student entry grade distribution (70% grade 7, rest spread across 8-11)
NEW_STUDENT_GRADE_WEIGHTS = {7: 0.60, 8: 0.15, 9: 0.12, 10: 0.08, 11: 0.05}


def create_student(grade, district_id, year_index):
    """Create a new student with demographics and scores."""
    student_id = generate_student_id()

    academic_score, engagement_score = generate_correlated_scores(1)
    academic_score = float(academic_score[0])
    engagement_score = float(engagement_score[0])

    # Add slight engagement improvement for students entering later years
    # (program has matured)
    engagement_score = min(0.95, engagement_score + year_index * 0.02)

    student_registry[student_id] = {
        'gender': np.random.choice(GENDER_CODES, p=GENDER_PROBS),
        'ethnicity': np.random.choice(ETHNICITY_CODES, p=ETHNICITY_PROBS),
        'race': np.random.choice(RACE_CODES, p=RACE_PROBS),
        'academic_score': academic_score,
        'engagement_score': engagement_score,
        'district_id': district_id,
        'entry_grade': grade,
    }

    return student_id


def assign_districts_for_cohort(n_students):
    """Assign districts to a group of students based on target percentages."""
    district_ids = list(DISTRICTS.keys())
    district_probs = [DISTRICTS[d]['target_pct'] for d in district_ids]
    # Normalize (in case of rounding)
    total = sum(district_probs)
    district_probs = [p / total for p in district_probs]
    return np.random.choice(district_ids, size=n_students, p=district_probs)


# Generate Year 1 (all new students)
grades_list = list(INITIAL_GRADE_WEIGHTS.keys())
grades_probs = list(INITIAL_GRADE_WEIGHTS.values())
initial_grades = np.random.choice(grades_list, size=TARGET_STUDENTS_PER_YEAR, p=grades_probs)
initial_districts = assign_districts_for_cohort(TARGET_STUDENTS_PER_YEAR)

year_1_roster = []
for i in range(TARGET_STUDENTS_PER_YEAR):
    sid = create_student(int(initial_grades[i]), int(initial_districts[i]), 0)
    year_1_roster.append((sid, int(initial_grades[i])))

year_rosters[YEARS[0]] = year_1_roster
print(f"  Year 1 ({YEARS[0]}): {len(year_1_roster)} students")

# Generate subsequent years
for year_idx in range(1, len(YEARS)):
    year = YEARS[year_idx]
    prev_year = YEARS[year_idx - 1]
    prev_roster = year_rosters[prev_year]

    new_roster = []

    # Process returning students
    for sid, grade in prev_roster:
        # Seniors leave (grade 12)
        if grade >= 12:
            continue

        # Grade 13 students don't continue in main roster
        if grade == 13:
            continue

        # Attrition check
        if np.random.random() < ATTRITION_RATE:
            continue

        # Retention check (3% don't advance)
        if np.random.random() < RETENTION_RATE:
            new_roster.append((sid, grade))  # Same grade
        else:
            new_roster.append((sid, grade + 1))  # Advance

    # Add new students to reach target
    n_needed = TARGET_STUDENTS_PER_YEAR - len(new_roster)
    if n_needed > 0:
        new_grades_list = list(NEW_STUDENT_GRADE_WEIGHTS.keys())
        new_grades_probs = list(NEW_STUDENT_GRADE_WEIGHTS.values())
        new_grades = np.random.choice(new_grades_list, size=n_needed, p=new_grades_probs)
        new_districts = assign_districts_for_cohort(n_needed)

        for i in range(n_needed):
            sid = create_student(int(new_grades[i]), int(new_districts[i]), year_idx)
            new_roster.append((sid, int(new_grades[i])))

    year_rosters[year] = new_roster
    returning_count = len(new_roster) - n_needed
    print(f"  Year {year_idx + 1} ({year}): {len(new_roster)} students "
          f"({returning_count} returning, {n_needed} new)")

# ============================
# GENERATE GRADE 13 STUDENTS
# ============================

print("\n[2/5] Determining outcomes and generating Grade 13 students...")

# We'll process all seniors first to determine who graduates and enrolls in PSE,
# then add a small subset as grade 13 in the following year.

# First, let's build the main AY records and determine senior outcomes
senior_outcomes = {}  # (student_id, year) → {graduated, fafsa, pse, college, ...}

for year_idx, year in enumerate(YEARS):
    roster = year_rosters[year]
    for sid, grade in roster:
        if grade == 12:
            student = student_registry[sid]
            academic = student['academic_score']
            engagement = student['engagement_score']

            # Year-over-year improvement bonus
            year_bonus = year_idx * 0.015

            # Graduation probability
            grad_prob = 0.55 + 0.25 * academic + 0.12 * engagement + year_bonus
            grad_prob = np.clip(grad_prob, 0.15, 0.96)
            graduated = np.random.random() < grad_prob

            # FAFSA probability (strongly correlated with financial aid services
            # which we haven't generated yet - use engagement as proxy)
            fafsa_service_proxy = engagement > 0.4  # ~60% of students
            fafsa_bonus = 0.18 if fafsa_service_proxy else 0
            fafsa_prob = 0.30 + 0.18 * engagement + 0.12 * academic + fafsa_bonus + year_bonus * 0.5
            fafsa_prob = np.clip(fafsa_prob, 0.10, 0.90)
            fafsa_completed = np.random.random() < fafsa_prob

            # FAFSA status assignment
            if fafsa_completed:
                fafsa_status = 1  # Completed
            else:
                # Among non-completers: 70% "Not Completed", 20% "Not Collected", 10% N/A
                fafsa_roll = np.random.random()
                if fafsa_roll < 0.70:
                    fafsa_status = 2  # Not Completed
                elif fafsa_roll < 0.90:
                    fafsa_status = 3  # Not Collected
                else:
                    fafsa_status = 4  # N/A

            # PSE probability (among graduates)
            pse_enrolled = False
            college_name = None
            college_ipeds = None
            if graduated:
                fafsa_pse_bonus = 0.20 if fafsa_completed else 0
                pse_prob = 0.12 + 0.20 * academic + 0.12 * engagement + fafsa_pse_bonus + year_bonus * 0.5
                pse_prob = np.clip(pse_prob, 0.08, 0.85)
                pse_enrolled = np.random.random() < pse_prob

                if pse_enrolled:
                    college_idx = np.random.randint(0, len(COLLEGES))
                    college_name = COLLEGES[college_idx][0]
                    college_ipeds = COLLEGES[college_idx][1]

            # Graduation status code
            if graduated:
                grad_status = 1
            else:
                grad_roll = np.random.random()
                if grad_roll < 0.75:
                    grad_status = 2  # Did Not Graduate
                else:
                    grad_status = 3  # Status Unknown

            senior_outcomes[(sid, year)] = {
                'graduated': graduated,
                'grad_status': grad_status,
                'fafsa_status': fafsa_status,
                'fafsa_completed': fafsa_completed,
                'pse_enrolled': pse_enrolled,
                'college_name': college_name,
                'college_ipeds': college_ipeds,
            }

# Add Grade 13 students (PSE enrollees from previous year's seniors)
grade_13_additions = {}  # year → list of (student_id, 13)

for year_idx in range(1, len(YEARS)):
    year = YEARS[year_idx]
    prev_year = YEARS[year_idx - 1]
    grade_13_students = []

    for (sid, outcome_year), outcome in senior_outcomes.items():
        if outcome_year == prev_year and outcome['pse_enrolled']:
            # ~70% of PSE enrollees get tracked as grade 13
            if np.random.random() < 0.70:
                grade_13_students.append((sid, 13))

    grade_13_additions[year] = grade_13_students
    if grade_13_students:
        year_rosters[year] = year_rosters[year] + grade_13_students
        print(f"  Added {len(grade_13_students)} Grade 13 students to {year}")


# ============================
# BUILD AY DATA RECORDS
# ============================

print("\n[3/5] Building AY data records and service totals...")

ay_records = []

for year_idx, year in enumerate(YEARS):
    roster = year_rosters[year]

    for sid, grade in roster:
        student = student_registry[sid]
        academic = student['academic_score']
        engagement = student['engagement_score']
        district_id = student['district_id']

        # Determine school NCES ID
        if grade == 13:
            nces_id = 99999999  # Will be padded to 000099999999
        else:
            nces_id = assign_district_and_school(grade, district_id)

        # Determine if this is a new or continuing student
        is_first_year = True
        for prev_year_idx in range(year_idx):
            prev_roster = year_rosters[YEARS[prev_year_idx]]
            if any(s == sid for s, g in prev_roster):
                is_first_year = False
                break
        student_type = 1 if is_first_year else 2

        # Program model code (1-3, slightly varies by district size)
        district_size = DISTRICTS[district_id]['size']
        if district_size == 'large':
            program_model = np.random.choice([1, 2, 3], p=[0.5, 0.3, 0.2])
        elif district_size == 'medium':
            program_model = np.random.choice([1, 2, 3], p=[0.6, 0.3, 0.1])
        else:
            program_model = np.random.choice([1, 2], p=[0.7, 0.3])

        # === SERVICE GENERATION ===
        service_totals = {}
        for svc_code in range(1, 14):
            service_totals[svc_code] = 0.0

        # Determine if student gets any services (85% do)
        gets_services = np.random.random() < SERVICE_PARTICIPATION_RATE

        if gets_services and grade <= 12:
            # Add year-over-year engagement improvement
            year_eng_bonus = year_idx * 0.015
            effective_engagement = min(0.95, engagement + year_eng_bonus)

            for svc_code, svc_config in SERVICE_CONFIG.items():
                base_rate = svc_config['part_rate']
                avg_hours = svc_config['avg_hours']

                # Apply grade multiplier if applicable
                grade_mult = 1.0
                if svc_code in GRADE_SERVICE_MULTIPLIERS:
                    grade_mult = GRADE_SERVICE_MULTIPLIERS[svc_code].get(grade, 1.0)

                # Engagement-modified participation rate
                # engagement=0.5 → rate stays same, higher → increased
                eng_modifier = 0.4 + effective_engagement * 1.2  # Range [0.4, 1.54]
                adj_rate = base_rate * grade_mult * eng_modifier
                adj_rate = min(adj_rate, 0.95)

                if np.random.random() < adj_rate:
                    # Student participates — determine total minutes
                    # Variation around average (lognormal-ish distribution)
                    hours = avg_hours * np.exp(np.random.normal(0, 0.4))
                    hours = max(0.1, hours)  # At least 6 minutes
                    service_totals[svc_code] = round(hours * 60, 1)  # Store as minutes

        # === GPA ===
        final_term_gpa = None
        cumulative_gpa = None

        if grade in [9, 10, 11, 12]:
            # 10-15% missing GPA
            if np.random.random() > 0.12:
                # Add some noise year-to-year but keep it related to academic score
                year_noise = np.random.normal(0, 0.15)
                cumulative_gpa = round(calculate_gpa(academic, 0.20), 2)
                # Final term can differ slightly from cumulative
                final_term_gpa = round(cumulative_gpa + np.random.normal(0, 0.3), 2)
                final_term_gpa = round(np.clip(final_term_gpa, 0.5, 4.0), 2)
                cumulative_gpa = round(np.clip(cumulative_gpa, 0.5, 4.0), 2)

        # === GRADUATION & FAFSA (Seniors only) ===
        grad_status_code = 4  # N/A for non-seniors
        fafsa_status_code = 4  # N/A for non-seniors

        if grade == 12:
            outcome = senior_outcomes.get((sid, year))
            if outcome:
                grad_status_code = outcome['grad_status']
                fafsa_status_code = outcome['fafsa_status']
            else:
                grad_status_code = 4
                fafsa_status_code = 4
        elif grade == 13:
            grad_status_code = 5  # In Grade 13

        # === PSE DATA ===
        first_college_name = None
        first_college_ipeds = None
        pse_graduated = None

        if grade == 12:
            outcome = senior_outcomes.get((sid, year))
            if outcome and outcome['pse_enrolled']:
                first_college_name = outcome['college_name']
                first_college_ipeds = outcome['college_ipeds']
        elif grade == 13:
            # Grade 13 students have their PSE data from senior year
            prev_year = YEARS[year_idx - 1] if year_idx > 0 else None
            if prev_year:
                outcome = senior_outcomes.get((sid, prev_year))
                if outcome and outcome['pse_enrolled']:
                    first_college_name = outcome['college_name']
                    first_college_ipeds = outcome['college_ipeds']
                    # Very few complete in 1 year (certificate programs)
                    pse_graduated = 'Y' if np.random.random() < 0.03 else 'N'

        # === COLLEGE VISITS IPEDS ===
        ipeds_visited = None
        if service_totals.get(5, 0) > 0:  # If participated in College Visit service
            n_visits = np.random.choice([1, 2, 3, 4, 5], p=[0.3, 0.35, 0.2, 0.1, 0.05])
            visited_codes = random.sample(COLLEGE_VISIT_IPEDS, min(n_visits, len(COLLEGE_VISIT_IPEDS)))
            ipeds_visited = ', '.join(visited_codes)

        # === ALGEBRA 1 STATUS ===
        if grade == 7:
            alg1 = np.random.choice([1, 2, 3, 4], p=[0.05, 0.25, 0.65, 0.05])
        elif grade == 8:
            alg1 = np.random.choice([1, 2, 3, 4], p=[0.40, 0.25, 0.30, 0.05])
        elif grade == 9:
            alg1 = np.random.choice([1, 2, 3, 4], p=[0.70, 0.15, 0.10, 0.05])
        elif grade in [10, 11, 12]:
            alg1 = np.random.choice([1, 2, 3, 4], p=[0.85, 0.05, 0.05, 0.05])
        else:
            alg1 = 4  # N/A for grade 13

        # === DUAL ENROLLMENT ===
        dual_enrollment = 'N'
        dual_degree = None
        if grade == 10 and np.random.random() < 0.03:
            dual_enrollment = 'Y'
        elif grade == 11 and np.random.random() < 0.10:
            dual_enrollment = 'Y'
        elif grade == 12 and np.random.random() < 0.15:
            dual_enrollment = 'Y'
            if np.random.random() < 0.02:
                dual_degree = 'Associate of Arts'

        # === BUILD RECORD ===
        record = {
            'High School AY': year,
            'Program Model Code': program_model,
            'School NCES ID': nces_id,
            'National CCREC Student ID': sid,
            'Student Type code': student_type,
            'Gender Code': student['gender'],
            'Ethnicity Code': student['ethnicity'],
            'Race Code': student['race'],
            'Grade Level': grade,
            'Enrollment Status Code': 1,
            'Service 1 Total': service_totals[1],
            'Service 2 Total': service_totals[2],
            'Service 3 Total': service_totals[3],
            'Service 4 Total': service_totals[4],
            'Service 5 Total': service_totals[5],
            'Service 6 Total': service_totals[6],
            'Service 7 Total': service_totals[7],
            'Service 8 Total': service_totals[8],
            'Service 9 Total': service_totals[9],
            'Service 10 Total': service_totals[10],
            'Service 11 Total': service_totals[11],
            'Service 12 Total': service_totals[12],
            'Service 13 Total': service_totals[13],
            'HS Grad Status code': grad_status_code,
            'FAFSA status code': fafsa_status_code,
            'Algebra 1- Grade of Completion': alg1,
            'Final Term GPA': final_term_gpa,
            'Cumulative GPA': cumulative_gpa,
            'IPEDS numbers of the Schools Visited': ipeds_visited,
            'First College Attended Name': first_college_name,
            'First College Attended IPEDS': first_college_ipeds,
            'Graduated Y/N': pse_graduated,
            'Degree Title': 'Certificate' if pse_graduated == 'Y' else None,
            'Dual Enrollment': dual_enrollment,
            'Dual Enrollment Degree': dual_degree,
        }

        ay_records.append(record)

    print(f"  {year}: {len([r for r in ay_records if r['High School AY'] == year])} records")

# Create AY DataFrame
ay_df = pd.DataFrame(ay_records)
print(f"\n  Total AY records: {len(ay_df)}")


# ============================
# GENERATE SERVICE DETAIL RECORDS
# ============================

print("\n[4/5] Generating service detail records (this may take a moment)...")

service_records = []
records_generated = 0

for year_idx, year in enumerate(YEARS):
    year_start = get_year_start(year)
    year_ay_records = ay_df[ay_df['High School AY'] == year]

    for _, row in year_ay_records.iterrows():
        sid = row['National CCREC Student ID']
        grade = row['Grade Level']

        if grade == 13:
            continue  # Grade 13 students don't receive new services

        for svc_code in range(1, 14):
            total_minutes = row[f'Service {svc_code} Total']
            if total_minutes <= 0:
                continue

            svc_config = SERVICE_CONFIG[svc_code]
            session_mean_min = svc_config['session_min']

            # Determine number of sessions
            n_sessions = max(1, int(round(total_minutes / session_mean_min)))
            # Add some randomness to session count
            n_sessions = max(1, n_sessions + np.random.choice([-1, 0, 0, 0, 1]))

            # Distribute minutes across sessions
            if n_sessions == 1:
                session_minutes = [total_minutes]
            else:
                # Random split with some variation
                raw_split = np.random.dirichlet(np.ones(n_sessions) * 2)
                session_minutes = (raw_split * total_minutes).tolist()
                # Round to nearest minute, ensure sum matches
                session_minutes = [max(5, round(m)) for m in session_minutes]
                # Adjust last session to make sum exact
                diff = total_minutes - sum(session_minutes[:-1])
                session_minutes[-1] = max(5, round(diff))

            # Determine months for sessions
            if svc_code in SUMMER_SERVICES:
                month_weights = SUMMER_MONTH_WEIGHTS
            else:
                month_weights = ACADEMIC_MONTH_WEIGHTS

            months = list(month_weights.keys())
            weights = list(month_weights.values())
            weights_norm = [w / sum(weights) for w in weights]
            session_months = np.random.choice(months, size=n_sessions, p=weights_norm)

            # Generate individual service records
            for i in range(n_sessions):
                month = int(session_months[i])
                minutes = session_minutes[i] if i < len(session_minutes) else session_mean_min

                # Generate date
                if month >= 7:
                    date_year = year_start
                else:
                    date_year = year_start + 1

                days_in_month = {
                    1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
                    7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31,
                }
                day = random.randint(1, days_in_month[month])
                try:
                    service_date = datetime(date_year, month, day)
                except ValueError:
                    service_date = datetime(date_year, month, days_in_month[month])

                service_records.append({
                    'Academic Year': year,
                    'National CCREC Student ID': sid,
                    'Service Date': service_date.strftime('%m/%d/%Y'),
                    'Service Type Code': svc_code,
                    'Service Time': round(minutes, 1),
                })

                records_generated += 1

    print(f"  {year}: {len([r for r in service_records if r['Academic Year'] == year])} service records")

service_df = pd.DataFrame(service_records)
print(f"\n  Total service records: {len(service_df)}")


# ============================
# VALIDATION & STATISTICS
# ============================

print("\n[5/5] Validating data and writing files...")

# Validate student consistency across years
print("\n  --- Validation Checks ---")

# Check: students who appear in consecutive years should have advancing grades
issues = 0
for year_idx in range(1, len(YEARS)):
    year = YEARS[year_idx]
    prev_year = YEARS[year_idx - 1]

    current = ay_df[ay_df['High School AY'] == year][['National CCREC Student ID', 'Grade Level']]
    previous = ay_df[ay_df['High School AY'] == prev_year][['National CCREC Student ID', 'Grade Level']]

    merged = current.merge(previous, on='National CCREC Student ID', suffixes=('_curr', '_prev'))
    merged = merged[merged['Grade Level_prev'] < 13]  # Exclude grade 13

    # Students should advance by 0 (retained) or 1 (normal)
    merged['advancement'] = merged['Grade Level_curr'] - merged['Grade Level_prev']
    invalid = merged[(merged['advancement'] != 1) & (merged['advancement'] != 0)]
    issues += len(invalid)

print(f"  Grade advancement issues: {issues}")

# Statistics
print("\n  --- Dataset Statistics ---")
for year in YEARS:
    year_data = ay_df[ay_df['High School AY'] == year]
    seniors = year_data[year_data['Grade Level'] == 12]
    n_seniors = len(seniors)
    if n_seniors > 0:
        grad_rate = (seniors['HS Grad Status code'] == 1).mean() * 100
        fafsa_rate = (seniors['FAFSA status code'] == 1).mean() * 100
        grad_w_pse = seniors[(seniors['HS Grad Status code'] == 1)]
        if len(grad_w_pse) > 0:
            pse_rate = grad_w_pse['First College Attended Name'].notna().mean() * 100
        else:
            pse_rate = 0
    else:
        grad_rate = fafsa_rate = pse_rate = 0

    hs_students = year_data[year_data['Grade Level'].isin([9, 10, 11, 12])]
    valid_gpas = hs_students['Cumulative GPA'].dropna()
    avg_gpa = valid_gpas.mean() if len(valid_gpas) > 0 else 0

    print(f"  {year}: {len(year_data)} students | "
          f"Seniors: {n_seniors} | "
          f"Grad: {grad_rate:.1f}% | "
          f"FAFSA: {fafsa_rate:.1f}% | "
          f"PSE: {pse_rate:.1f}% | "
          f"Avg GPA: {avg_gpa:.2f}")

# Service statistics
print("\n  --- Service Statistics ---")
for svc_code, config in SERVICE_CONFIG.items():
    col = f'Service {svc_code} Total'
    participants = ay_df[ay_df[col] > 0]
    total_students = len(ay_df[ay_df['Grade Level'] <= 12])
    part_rate = len(participants) / total_students * 100 if total_students > 0 else 0
    avg_hours = participants[col].mean() / 60 if len(participants) > 0 else 0
    print(f"  Service {svc_code:2d} ({config['name'][:30]:30s}): "
          f"Participation: {part_rate:5.1f}% | Avg Hours: {avg_hours:.1f}")


# ============================
# WRITE FILES
# ============================

output_dir = os.path.dirname(os.path.abspath(__file__))
ay_file = os.path.join(output_dir, 'practice_AYData.csv')
service_file = os.path.join(output_dir, 'practice_ServiceData.csv')

# Clean up NaN display
ay_df_out = ay_df.copy()

# Ensure NCES ID is integer (will be zero-padded by the dashboard)
ay_df_out['School NCES ID'] = ay_df_out['School NCES ID'].astype(int)

# Write files
ay_df_out.to_csv(ay_file, index=False)
service_df.to_csv(service_file, index=False)

print(ay_file)
print(service_file)

print(f"\n  Files written:")
print(f"    AY Data:      {ay_file}")
print(f"    Service Data:  {service_file}")
print(f"\n  AY file size:      {os.path.getsize(ay_file) / 1024 / 1024:.1f} MB")
print(f"  Service file size: {os.path.getsize(service_file) / 1024 / 1024:.1f} MB")

print("\n" + "=" * 60)
print("Data generation complete!")
print("=" * 60)
print(f"\nTo use with the dashboard:")
print(f"  python main.py \"{output_dir}\"")
print(f"\nOr rename files to match expected naming:")
print(f"  practice_AYData.csv → Contains 'aydata' ✓")
print(f"  practice_ServiceData.csv → Contains 'servicedata' ✓")