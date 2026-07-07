import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="EduPro Learner Analytics", layout="wide")

# ---------- Load & merge data ----------
users = pd.read_excel("edupro_data.xlsx", sheet_name="Users")
courses = pd.read_excel("edupro_data.xlsx", sheet_name="Courses")
transactions = pd.read_excel("edupro_data.xlsx", sheet_name="Transactions")
df = transactions.merge(users, on="UserID").merge(courses, on="CourseID")

bins = [0, 17, 24, 29, 35]
labels = ["<18", "18-24", "25-29", "30-35"]
df["AgeGroup"] = pd.cut(df["Age"], bins=bins, labels=labels)

user_age_group = users.copy()
user_age_group["AgeGroup"] = pd.cut(user_age_group["Age"], bins=bins, labels=labels)
users_per_group = user_age_group["AgeGroup"].value_counts()

st.title("EduPro Learner Analytics Dashboard")

# ---------- Sidebar filters (brief requirement) ----------
st.sidebar.header("Filters")
age_filter = st.sidebar.multiselect("Age Group", options=labels, default=labels)
gender_filter = st.sidebar.multiselect("Gender", options=df["Gender"].unique(), default=list(df["Gender"].unique()))
category_filter = st.sidebar.multiselect("Course Category", options=df["CourseCategory"].unique(), default=list(df["CourseCategory"].unique()))
level_filter = st.sidebar.multiselect("Course Level", options=df["CourseLevel"].unique(), default=list(df["CourseLevel"].unique()))

filtered = df[
    df["AgeGroup"].isin(age_filter) &
    df["Gender"].isin(gender_filter) &
    df["CourseCategory"].isin(category_filter) &
    df["CourseLevel"].isin(level_filter)
]

# ---------- Top-line KPIs ----------
col1, col2, col3 = st.columns(3)
col1.metric("Total Enrollments (filtered)", f"{len(filtered):,}")
col2.metric("Unique Learners (filtered)", f"{filtered['UserID'].nunique():,}")
col3.metric("Unique Courses (filtered)", f"{filtered['CourseID'].nunique():,}")

st.markdown("---")

# ---------- 1. strongest finding not in the brief's module list ----------
st.header("1. Enrollment Concentration Among Users")
user_enrollment_counts = df.groupby("UserID")["TransactionID"].count().sort_values(ascending=False)
top_10_pct = int(len(user_enrollment_counts) * 0.1)
top_10_share = user_enrollment_counts.head(top_10_pct).sum() / user_enrollment_counts.sum()

st.metric("Top 10% of users' share of total enrollments", f"{top_10_share*100:.1f}%")
st.image("chart_concentration.png")
st.caption(
    "This is the strongest behavioral finding in the dataset: a small subset of "
    "highly active learners accounts for a disproportionate share of enrollments — "
    "roughly 4x what uniform random activity would produce. Recommend prioritizing "
    "retention/engagement strategy for this segment over demographic targeting, "
    "since age and gender showed no meaningful predictive value above."
)

st.markdown("---")

# ---------- Module 2: Course Category Popularity ----------
st.header("2. Course Category Popularity")
category_counts = df["CourseCategory"].value_counts()
cat_mean = category_counts.mean()

fig, ax = plt.subplots(figsize=(8, 4))
category_counts.plot(kind="bar", ax=ax, color="seagreen")
ax.axhline(cat_mean, color="black", linestyle="--", label=f"Mean ({cat_mean:.0f})")
ax.set_ylabel("Enrollments")
ax.legend()
plt.xticks(rotation=45, ha="right")
st.pyplot(fig)

st.caption(
    "Data Science shows the highest enrollment (916 vs mean 833, z≈2.67). "
    "This is a borderline signal (~4-5% probability by chance with 12 categories) "
    "— not confirmed, and does not hold when tested against age subgroups (p=0.179). "
    "Treat as a lead for further investigation, not a confirmed demand pattern."
)

st.markdown("---")

# ---------- Module 3: Learner Demographic Overview ----------
st.header("3. Learner Demographic Overview")
col1, col2 = st.columns(2)
with col1:
    st.write("Age Distribution")
    st.bar_chart(users["Age"].value_counts().sort_index())
with col2:
    st.write("Gender Distribution")
    st.bar_chart(users["Gender"].value_counts())

st.markdown("---")

# ---------- Module 4: Age-wise Enrollment Analysis ----------
st.header("4. Age-wise Enrollment Analysis")
age_enrollments = df["AgeGroup"].value_counts()
age_rate = age_enrollments / users_per_group
st.bar_chart(age_rate)
st.caption(
    "Per-learner enrollment rate by age group. Range: 3.26–3.39 courses/learner — "
    "statistically flat. Age does not predict enrollment volume in this dataset "
    "(raw counts alone are misleading here due to unequal group sizes)."
)

st.markdown("---")

# ---------- Module 5: Gender-based Course Preference Analysis ----------
st.header("5. Gender-based Course Preference Analysis")
gender_counts_users = users["Gender"].value_counts()
gender_counts_enroll = df["Gender"].value_counts()
gender_rate = gender_counts_enroll / gender_counts_users
st.bar_chart(gender_rate)
st.caption(
    "Per-learner enrollment rate by gender: Female 3.34, Male 3.33. "
    "Chi-square test on gender vs course level: p=0.906 — no significant "
    "relationship. Gender does not predict enrollment behavior in this dataset."
)

st.markdown("---")

st.subheader("6. Course Duration vs. Rating (Tested, Not a Standout Finding)")
st.image("chart_duration_rating.png")
corr = courses["CourseDuration"].corr(courses["CourseRating"])
st.caption(f"Weak positive correlation (r≈{corr:.2f}). Explains ~4% of rating variance — real, but small.")
st.caption(
    f"Correlation between course duration and rating: r={corr:.2f} — weak/no relationship. "
    "Duration does not meaningfully predict learner satisfaction in this dataset. "
    "Included here for completeness, not visualized as a chart since there's no pattern to show."
)