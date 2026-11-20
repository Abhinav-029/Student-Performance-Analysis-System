import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DATA_FILE = DATA_DIR / "students.csv"

SUBJECTS = ["English", "Mathematics", "Science", "Computer", "Social Studies"]
COLUMNS = ["student_id", "name", "class_name", *SUBJECTS, "total", "percentage", "grade", "result"]

st.set_page_config(page_title="Student Performance Analysis", page_icon="🎓", layout="wide")

def grade_for(percentage):
    if percentage >= 90: return "A+"
    if percentage >= 80: return "A"
    if percentage >= 70: return "B"
    if percentage >= 60: return "C"
    if percentage >= 50: return "D"
    return "F"

def load_data():
    if DATA_FILE.exists():
        df = pd.read_csv(DATA_FILE)
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = 0 if col in SUBJECTS + ["total", "percentage"] else ""
        return df[COLUMNS]
    return pd.DataFrame(columns=COLUMNS)

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def prepare_record(student_id, name, class_name, marks):
    total = sum(marks.values())
    percentage = total / len(SUBJECTS)
    return {
        "student_id": str(student_id).strip(),
        "name": str(name).strip(),
        "class_name": str(class_name).strip(),
        **marks,
        "total": total,
        "percentage": round(percentage, 2),
        "grade": grade_for(percentage),
        "result": "Pass" if min(marks.values()) >= 33 else "Needs Improvement"
    }

if "students" not in st.session_state:
    st.session_state.students = load_data()

st.title("🎓 Student Performance Analysis System")
st.caption("A Python-based application to manage student marks and analyze academic performance.")

with st.sidebar:
    st.header("Navigation")
    page = st.radio("Choose a section", ["Dashboard", "Add Student", "Manage Records", "Analysis", "About Project"])
    st.divider()
    st.caption("Marks are entered out of 100 for each subject.")
    st.caption("Pass criterion: at least 33 marks in every subject.")

df = st.session_state.students.copy()

if page == "Dashboard":
    st.subheader("Class Overview")
    if df.empty:
        st.info("No student records yet. Open **Add Student** to enter the first record.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Students", len(df))
        c2.metric("Class Average", f"{df['percentage'].mean():.1f}%")
        c3.metric("Highest Percentage", f"{df['percentage'].max():.1f}%")
        c4.metric("Students Passed", int((df["result"] == "Pass").sum()))

        left, right = st.columns(2)
        with left:
            st.markdown("#### Grade Distribution")
            counts = df["grade"].value_counts().reindex(["A+", "A", "B", "C", "D", "F"], fill_value=0)
            fig, ax = plt.subplots()
            ax.bar(counts.index, counts.values)
            ax.set_ylabel("Number of students")
            ax.set_xlabel("Grade")
            ax.set_title("Students by Grade")
            st.pyplot(fig)
            plt.close(fig)
        with right:
            st.markdown("#### Subject-wise Average")
            averages = df[SUBJECTS].mean()
            fig, ax = plt.subplots()
            ax.bar(averages.index, averages.values)
            ax.set_ylim(0, 100)
            ax.set_ylabel("Average marks")
            ax.set_title("Average Marks per Subject")
            ax.tick_params(axis="x", rotation=25)
            st.pyplot(fig)
            plt.close(fig)

        st.markdown("#### Recent Student Records")
        st.dataframe(df[["student_id", "name", "class_name", "total", "percentage", "grade", "result"]].tail(10),
                     use_container_width=True, hide_index=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download all records (CSV)", csv, "student_records.csv", "text/csv")

elif page == "Add Student":
    st.subheader("Add a Student Record")
    with st.form("student_form", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        student_id = c1.text_input("Student ID *")
        name = c2.text_input("Student Name *")
        class_name = c3.text_input("Class / Section", placeholder="e.g. B.Tech AI&ML - A")
        st.markdown("#### Enter subject marks (0–100)")
        cols = st.columns(5)
        marks = {}
        for col, subject in zip(cols, SUBJECTS):
            marks[subject] = col.number_input(subject, min_value=0, max_value=100, value=0, step=1)
        submitted = st.form_submit_button("Save Student Record", type="primary")
        if submitted:
            if not student_id.strip() or not name.strip():
                st.error("Student ID and Student Name are required.")
            elif student_id.strip() in st.session_state.students["student_id"].astype(str).values:
                st.error("This Student ID already exists. Use a unique ID.")
            else:
                record = prepare_record(student_id, name, class_name, marks)
                st.session_state.students = pd.concat([st.session_state.students, pd.DataFrame([record])], ignore_index=True)
                save_data(st.session_state.students)
                st.success(f"Record saved for {name}. Grade: {record['grade']} ({record['percentage']}%).")

elif page == "Manage Records":
    st.subheader("Manage Student Records")
    if df.empty:
        st.info("No records available. Add a student first.")
    else:
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.markdown("#### Delete a record")
        ids = df["student_id"].astype(str).tolist()
        selected_id = st.selectbox("Select Student ID", ids)
        if st.button("Delete Selected Record", type="secondary"):
            st.session_state.students = st.session_state.students[
                st.session_state.students["student_id"].astype(str) != selected_id
            ].reset_index(drop=True)
            save_data(st.session_state.students)
            st.success(f"Deleted student ID {selected_id}.")
            st.rerun()
        st.download_button("⬇️ Export records as CSV", df.to_csv(index=False).encode("utf-8"),
                           "student_records.csv", "text/csv")

elif page == "Analysis":
    st.subheader("Individual Student Analysis")
    if df.empty:
        st.info("Add student records to view analysis.")
    else:
        choices = df["student_id"].astype(str) + " — " + df["name"].astype(str)
        selected = st.selectbox("Choose student", choices.tolist())
        selected_id = selected.split(" — ")[0]
        student = df[df["student_id"].astype(str) == selected_id].iloc[0]
        c1, c2, c3 = st.columns(3)
        c1.metric("Percentage", f"{student['percentage']:.2f}%")
        c2.metric("Grade", str(student["grade"]))
        c3.metric("Result", str(student["result"]))
        st.markdown(f"**Student:** {student['name']}  |  **Class:** {student['class_name']}")
        fig, ax = plt.subplots()
        ax.bar(SUBJECTS, [student[s] for s in SUBJECTS])
        ax.set_ylim(0, 100)
        ax.set_ylabel("Marks out of 100")
        ax.set_title(f"Subject-wise Performance — {student['name']}")
        ax.tick_params(axis="x", rotation=25)
        st.pyplot(fig)
        plt.close(fig)
        weakest = min(SUBJECTS, key=lambda s: student[s])
        strongest = max(SUBJECTS, key=lambda s: student[s])
        st.info(f"Strongest subject: **{strongest}** ({student[strongest]}/100). "
                f"Subject needing most attention: **{weakest}** ({student[weakest]}/100).")

elif page == "About Project":
    st.subheader("Project Information")
    st.markdown("""
    **Objective:** To develop a simple application that stores student marks and converts them
    into useful academic performance summaries.

    **Technologies:** Python, Streamlit, Pandas, Matplotlib and CSV file storage.

    **Main modules:**
    - Data entry and validation
    - Total, percentage, grade and pass-status calculation
    - Student record management
    - Class dashboard and subject-wise visualization
    - Individual student analysis and CSV export

    **Grading scale:** A+ (90–100), A (80–89), B (70–79), C (60–69),
    D (50–59), F (below 50). A student is marked Pass only if every subject
    has at least 33 marks.

    **Storage:** Records are saved locally in `data/students.csv`.
    """)
    # st.warning("This is an educational demonstration project. The grading thresholds can be changed to match an institution's rules.")

st.divider()
st.caption("Student Performance Analysis System | Developed using Python")
