def campus_navigation(request):
    return {
        "nav_admin": [("students","Students"),("faculty","Faculty"),("departments","Departments"),("courses","Courses"),("subjects","Subjects"),("attendance","Attendance"),("examinations","Examinations"),("results","Results"),("fees","Fees"),("payments","Payments"),("timetable","Timetable"),("notices","Notices"),("materials","Study materials")],
        "nav_faculty": [("subjects","My subjects"),("attendance","Attendance"),("examinations","Examinations"),("results","Results"),("timetable","Timetable"),("notices","Notices"),("materials","Study materials")],
        "nav_student": [("students","My profile"),("attendance","Attendance"),("results","Results"),("fees","Fees"),("timetable","Timetable"),("notices","Notices"),("materials","Study materials")],
    }
