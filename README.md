# Smart College Management System

A role-based college portal built with Python and Django. Administrators manage college data, faculty handle assigned academic work, and students view their own records.

> README mein Windows ke commands Command Prompt (CMD) ke liye diye gaye hain. GitHub par publish karne se pehle neeche ka **GitHub par upload** section padhein.

## Features

- **Admin, Faculty, Student** roles with protected dashboards.
- Departments, courses, faculty, student profiles and subject assignments.
- Attendance records with duplicate-per-day protection and attendance percentage calculation.
- Examinations, marks, grade calculation and controlled result publication.
- Fee ledgers, payment records and automatic outstanding balances.
- Weekly timetable with faculty/classroom time-conflict validation.
- Notices and authenticated study-material downloads.
- Searchable lists, Django admin console, password-reset pages and responsive layout.
- SQLite for local use; optional MySQL settings are included.

## Requirements

- Windows 10/11
- Python 3.12 recommended. Python 3.10+ is supported by the dependency range.
- Internet connection for the first package installation.
- Git for the GitHub upload steps.

## First-time setup and run (Windows)

1. Download the ZIP and select **Extract All**. Open the extracted `Smart_College_Management_System` folder.
2. In File Explorer, click the folder address bar, type `cmd`, and press **Enter**. This opens Command Prompt in the project folder.
3. Check that the prompt is in the project folder and that `setup.ps1` is present:

   ```cmd
   dir setup.ps1
   ```

4. Run setup from CMD. Do not double-click `.ps1` files; Windows may open them in Notepad.

   ```cmd
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\setup.ps1"
   ```

   Setup creates a Python virtual environment, installs packages, and applies database migrations. The first install can take a few minutes.

5. Start the website:

   ```cmd
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\start.ps1"
   ```

6. Open <http://127.0.0.1:8000> in a browser.

Keep the terminal window open while using the website. To stop the server, press **Ctrl+C** in that window.

## Run it again later

After the first setup, there is no need to run `setup.ps1` again. Each time you want to open the project:

1. Open Command Prompt in the project folder (File Explorer address bar → type `cmd` → Enter).
2. Run:

   ```cmd
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\start.ps1"
   ```

3. Visit <http://127.0.0.1:8000>.

The local `db.sqlite3` file stores the college data. Keep it if you need those records next time. It is intentionally excluded from GitHub.

## Demo accounts

The included local demo database has these fictional accounts:

| Role | Username | Password |
| --- | --- | --- |
| Admin | `campusadmin` | `CampusDemo!26` |
| Faculty | `faculty.demo` | `CampusDemo!26` |
| Student | `student.demo` | `CampusDemo!26` |

For a new/empty database (for example, after cloning the GitHub repository), create demo records with:

```cmd
.venv\Scripts\python.exe manage.py seed_demo
```

Demo passwords are for local evaluation only. Change or remove demo accounts before entering real college data or deploying the application.

## How to use the portal

### Administrator's first data setup

1. Sign in as Admin and open **Admin console**. User accounts are created here.
2. Create a **Department**, then a **Course** that belongs to it.
3. Create Faculty and Student users and assign the correct role. Add their Faculty or Student profiles; a student profile needs a course and semester.
4. Create **Subjects** and assign each subject to its course, semester, and (if applicable) faculty member.
5. Add timetable entries, attendance, exams, results, fees, payments, notices, and study materials as needed.

### Main workflows

- **Attendance:** Faculty opens Attendance, chooses the assigned subject/student/date, and saves Present, Absent, or Late. A student can view only their own records.
- **Exams and results:** Create an examination and enter marks. Set `Published` only when students should be able to see the result. Grades are calculated from the percentage.
- **Fees:** Add a fee amount and due date, then add payments. The outstanding balance is calculated from payments.
- **Timetable:** Add a subject, faculty, weekday, start/end time, and room. Conflicting room or faculty time slots are rejected.
- **Notices and learning material:** Publish notices for everyone, students, or faculty. Upload PDF, DOC/DOCX, PPT/PPTX, or TXT study files up to 10 MB. Downloads require sign-in and an allowed role.

### Role permissions

- **Admin:** Manage accounts and college records, publish results/notices, and access the admin console.
- **Faculty:** View assigned subjects/timetable; manage assigned academic work such as attendance, exams, results, notices, and materials.
- **Student:** View their profile, attendance, published results, fees, timetable, notices, and materials.

## GitHub par upload kaise karein

### A. GitHub repository banayein

1. Sign in to [GitHub](https://github.com/).
2. Click **New repository**.
3. Repository name rakhein, for example `smart-college-management-system`.
4. Public ya Private choose karein. Agar local project push kar rahe hain, **Add a README**, `.gitignore`, aur License ko initialize karne wale options unchecked rakhein.
5. **Create repository** par click karein. GitHub aapko repository URL dega, for example `https://github.com/YOUR-USERNAME/smart-college-management-system.git`.

### B. Project folder se push karein

Install Git for Windows if `git --version` command nahi chalta. Phir project folder mein CMD kholkar ye commands ek-ek karke chalayein:

```cmd
git init
git add .
git status --short
git commit -m "Initial commit: Smart College Management System"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/smart-college-management-system.git
git push -u origin main
```

GitHub URL mein `YOUR-USERNAME` ko apne GitHub username se aur repo name ko apne banaye repository name se replace karein. GitHub sign-in maange to browser/device login flow ya Personal Access Token use karein; GitHub account password ko Git prompt mein paste na karein.

If `git remote add origin` says `origin` already exists, update the URL and push:

```cmd
git remote set-url origin https://github.com/YOUR-USERNAME/smart-college-management-system.git
git push -u origin main
```

If Git says there is nothing to commit, check `git status` and `git log --oneline`. The files may already have a commit; continue with the branch, remote, and push commands as appropriate.

### C. GitHub par bhejne se pehle security check

`.gitignore` excludes `.env`, `db.sqlite3`, virtual environments, generated files, uploaded `media/`, and ZIP archives. Check before committing:

```cmd
git check-ignore .env db.sqlite3
git status --short
```

Do **not** force-add ignored database, `.env`, real student data, passwords, or private uploads. `.env.example` is safe to share because it contains placeholders. The database is local; people who clone the repository run migrations and optionally `seed_demo` to create a fresh local database.

## Optional MySQL configuration

SQLite is the default and is recommended for the first run. To use MySQL instead:

1. Create a MySQL database with `utf8mb4` encoding.
2. Copy `.env.example` to `.env` and set `DB_ENGINE=mysql`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`.
3. Set a unique `SECRET_KEY`, set `DEBUG=False`, and configure `ALLOWED_HOSTS` for the deployment.
4. Run `.venv\Scripts\python.exe manage.py migrate`.

Never commit `.env`. For production, use HTTPS, a production-grade secret, database backups, SMTP for password reset, and a properly configured static/media file server. The bundled Django development server is for local development and demonstration, not public hosting.

## Project structure

```text
smart_college/       Django settings, URLs, ASGI/WSGI
campus/              Models, forms, views, role permissions, admin, migrations
templates/           Login, dashboard, data lists and forms
static/campus.css    Responsive interface styles
docs/                Project report template and ER diagram
manage.py             Django command entry point
setup.ps1             First-time Windows setup
start.ps1             Start the local development server
package.ps1           Rebuild the distributable ZIP
```

## Academic submission notes

Fill in your own name, roll number, college, department, project guide, and academic year in `docs/PROJECT_REPORT.md`. The optional scope—online payment gateway, SMS/email integration, QR attendance, mobile app, library/hostel/transport, and AI analytics—has not been implemented in this initial version.
