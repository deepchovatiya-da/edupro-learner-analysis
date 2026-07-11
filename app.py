import streamlit as st
import pandas as pd

# Set up the main layout and title of the Streamlit app
st.set_page_config(page_title="EduPro Learner Analytics", layout="wide")

# ==========================================
# 1. DATA LOADING & PREPARATION
# ==========================================

# Load the raw data from the Excel file sheets
users = pd.read_excel("edupro_data.xlsx", sheet_name="Users")
courses = pd.read_excel("edupro_data.xlsx", sheet_name="Courses")
transactions = pd.read_excel("edupro_data.xlsx", sheet_name="Transactions")

# Merge all three tables together into one master dataframe ('df')
df = transactions.merge(users, on="UserID").merge(courses, on="CourseID")

# Create age buckets
bins = [0, 17, 24, 29, 35]
labels = ["<18", "18-24", "25-29", "30-35"]
df["AgeGroup"] = pd.cut(df["Age"], bins=bins, labels=labels)

st.title("EduPro Learner Analytics Dashboard")

# ==========================================
# 2. SIDEBAR FILTERS
# ==========================================

st.sidebar.header("Filters")

age_filter = st.sidebar.multiselect("Age Group", options=labels, default=labels)
gender_filter = st.sidebar.multiselect("Gender", options=df["Gender"].unique(), default=list(df["Gender"].unique()))
category_filter = st.sidebar.multiselect("Course Category", options=df["CourseCategory"].unique(), default=list(df["CourseCategory"].unique()))
level_filter = st.sidebar.multiselect("Course Level", options=df["CourseLevel"].unique(), default=list(df["CourseLevel"].unique()))

# ==========================================
# 3. APPLYING FILTERS 
# ==========================================

# Filter the master dataframe based on user selections
filtered = df[
    df["AgeGroup"].isin(age_filter) &
    df["Gender"].isin(gender_filter) &
    df["CourseCategory"].isin(category_filter) &
    df["CourseLevel"].isin(level_filter)
]

# Deduplicate for accurate user/course level metrics
filtered_users = filtered.drop_duplicates(subset=["UserID"])
filtered_courses = filtered.drop_duplicates(subset=["CourseID"])

# ==========================================
# 4. DASHBOARD VISUALIZATIONS
# ==========================================

# ---------- Top-line KPIs ----------
col1, col2, col3 = st.columns(3)
col1.metric("Total Enrollments (filtered)", f"{len(filtered):,}")
col2.metric("Unique Learners (filtered)", f"{filtered_users['UserID'].nunique():,}")
col3.metric("Unique Courses (filtered)", f"{filtered_courses['CourseID'].nunique():,}")

st.markdown("---")

# ---------- Module 1: Enrollment Concentration ----------
st.header("1. Enrollment Concentration Among Users")

if not filtered.empty:
    user_enrollment_counts = filtered.groupby("UserID")["TransactionID"].count().sort_values(ascending=False)
    top_10_pct = max(1, int(len(user_enrollment_counts) * 0.1)) 
    top_10_share = user_enrollment_counts.head(top_10_pct).sum() / user_enrollment_counts.sum()

    st.metric("Top 10% of users' share of total enrollments", f"{top_10_share*100:.1f}%")
    
    st.write("**Distribution of Courses per Learner**")
    enrollment_distribution = user_enrollment_counts.value_counts().sort_index()
    
    st.bar_chart(enrollment_distribution)
    st.caption(
        "X-axis: Number of courses taken. Y-axis: Number of learners. "
        "Notice how a small subset of highly active learners accounts for a disproportionate share of enrollments."
    )
else:
    st.write("No data available for the current filter selection.")

st.markdown("---")

# ---------- Module 2: Course Category Popularity ----------
st.header("2. Course Category Popularity")
if not filtered.empty:
    category_counts = filtered["CourseCategory"].value_counts()
    cat_mean = category_counts.mean()

    # Display the mean as text above the chart since native Streamlit charts don't use dashed lines
    st.write(f"**Average Enrollments per Category:** {cat_mean:.0f}")
    
    # REPLACED MATPLOTLIB: Now using native Streamlit interactive chart
    st.bar_chart(category_counts)
else:
    st.write("No data available for the current filter selection.")

st.markdown("---")

# ---------- Module 3: Learner Demographic Overview ----------
st.header("3. Learner Demographic Overview")
col1, col2 = st.columns(2)

with col1:
    st.write("**Age Distribution**")
    st.bar_chart(filtered_users["Age"].value_counts().sort_index())
with col2:
    st.write("**Gender Distribution**")
    st.bar_chart(filtered_users["Gender"].value_counts())

st.markdown("---")

# ---------- Module 4: Age-wise Enrollment Analysis ----------
st.header("4. Age-wise Enrollment Analysis")
age_enrollments = filtered["AgeGroup"].value_counts()
filtered_users_per_group = filtered_users["AgeGroup"].value_counts()

age_rate = (age_enrollments / filtered_users_per_group).fillna(0)
st.bar_chart(age_rate)
st.caption("Per-learner enrollment rate by age group. Age does not strongly predict enrollment volume in this dataset.")

st.markdown("---")

# ---------- Module 5: Gender-based Course Preference Analysis ----------
st.header("5. Gender-based Course Preference Analysis")
gender_counts_users = filtered_users["Gender"].value_counts()
gender_counts_enroll = filtered["Gender"].value_counts()

gender_rate = (gender_counts_enroll / gender_counts_users).fillna(0)
st.bar_chart(gender_rate)
st.caption("Per-learner enrollment rate by gender. Gender does not predict enrollment behavior in this dataset.")

st.markdown("---")

# ---------- Module 6: Course Duration vs. Rating ----------
st.header("6. Course Duration vs. Rating")

if len(filtered_courses) > 1:
    corr = filtered_courses["CourseDuration"].corr(filtered_courses["CourseRating"])
    st.write(f"**Correlation Coefficient (r): {corr:.2f}**")
    
    st.scatter_chart(
        data=filtered_courses,
        x="CourseDuration",
        y="CourseRating",
        color="#2E86C1" 
    )
    st.caption("Weak positive correlation. Explains ~4% of rating variance — real, but small.")
else:
    st.write("Not enough course data in current filter to calculate correlation or plot chart.")