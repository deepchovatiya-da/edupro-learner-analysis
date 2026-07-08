# EduPro Learner Analytics

Descriptive analysis of learner demographics and course enrollment behavior on the EduPro platform, built as a project-based internship deliverable.

**Live dashboard:** https://deepchovatiya-edupro-learner-analysis.streamlit.app

## Overview

This project analyzes 3,000 learners, 60 courses, and 10,000 enrollment transactions to test whether age, gender, course category, or course level predict enrollment behavior on the platform. Every finding was statistically tested — normalized for group size and, where relevant, verified with chi-square significance testing — before being reported.

## Dataset

- **Users** (3,000 rows): UserID, UserName, Age (15–35), Gender
- **Courses** (60 rows): CourseID, CourseName, CourseCategory, CourseType, CourseLevel, CourseDuration, CourseRating
- **Transactions** (10,000 rows): TransactionID, UserID, CourseID, TransactionDate

## Key Findings

**1. Enrollment concentration among power users — strongest finding**
Top 10% of users account for 42% of all enrollments, roughly 4x what even distribution would produce. This is the most defensible, non-demographic finding in the dataset.

**2. Category popularity — Data Science (borderline signal)**
916 enrollments vs. a 12-category mean of 833 (z≈2.67, ~4–5% probability by chance). Does not hold when tested against age subgroups (chi2 p=0.179) — treated as a lead, not a confirmed pattern.

**3. Demographic questions — all four came back null:**
- Age does not predict enrollment volume (3.26–3.39 courses/learner across all age bands)
- Gender does not predict enrollment volume (3.34 vs 3.33 courses/learner; chi2 p=0.906)
- Age does not predict category preference (chi2 p=0.179)
- Course level does not predict demand once course supply is normalized (164–170 enrollments/course across all levels)

**4. Course duration vs. rating** — weak positive correlation (r≈0.21), explains ~4% of rating variance. Real but minor.

## Repository Structure

- **eda.ipynb**: Full analysis: merging, EDA, chi-square testing, correlation checks
- **app.py**: Streamlit dashboard (deployed)
- **edupro_data.xlsx**: Source dataset (Users, Courses, Transactions sheets)
- **requirements.txt**: Python dependencies for deployment
- **chart_age_rate.png**: Age vs enrollment rate (normalized)
- **chart_gender_rate.png**: Gender vs enrollment rate (normalized)
- **chart_category.png**: Category popularity with mean reference line
- **chart_level_rate.png**: Course level demand (normalized by supply)
- **chart_concentration.png**: Enrollment concentration (Lorenz-style curve)
- **chart_duration_rating.png**: Duration vs rating scatter
- **report.md**: Written findings summary

## Tech Stack

Python, pandas, matplotlib, scipy (chi-square testing), Streamlit

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Methodology Note

Raw counts were not trusted at face value. Several apparent patterns — course-level popularity, individual course rankings, age-group enrollment differences — turned out to be artifacts of unequal group sizes or a course-name duplication bug, and were corrected before being reported. Where testing showed no meaningful relationship, that null result is reported directly rather than omitted or dressed up as a finding.
