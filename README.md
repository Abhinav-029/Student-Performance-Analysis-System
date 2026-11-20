# Student Performance Analysis System

A beginner-friendly Python + Streamlit application for recording student marks and analyzing academic performance.

## Features
- Add student records with unique student IDs
- Validate required fields and marks (0–100)
- Calculate total, percentage, grade and pass status automatically
- Dashboard with class statistics and charts
- Individual student subject-wise analysis
- Delete records and export data to CSV
- Persistent local storage in `data/students.csv`

## Technology stack
- Python 3
- Streamlit
- Pandas
- Matplotlib
- CSV for local data storage

## Run locally
1. Install Python 3.10 or newer.
2. Open a terminal in this project folder.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the application:

   ```bash
   streamlit run app.py
   ```

5. Open the local URL shown in the terminal (usually http://localhost:8501).

## Grading logic
Percentage = (sum of marks in all subjects / number of subjects)

- A+: 90 and above
- A: 80–89.99
- B: 70–79.99
- C: 60–69.99
- D: 50–59.99
- F: below 50

Pass status requires at least 33 marks in every subject. These are sample rules and can be adjusted for an institution.

## Project structure
```
Student_Performance_Analysis_System/
├── app.py
├── requirements.txt
├── README.md
├── PROJECT_REPORT.md
└── data/
    └── .gitkeep
```
