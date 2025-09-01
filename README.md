# FaceTrack AI (PyQt5 + OpenCV + MySQL)

A desktop application with two portals:
- **Student Portal**: Enroll new students via face capture and mark attendance (auto Login/Logout).
- **Admin Portal**: Secure login to view, filter, and export attendance reports.

## 1) Features
- Face registration & recognition (using `face_recognition` which uses deep learning under the hood).
- MySQL backend with normalized tables (`users`, `attendance`, `admins`).
- Auto-toggling **Login/Logout** based on last record for the day.
- Admin dashboard with filters (date range, roll no) + CSV export.
- Clean PyQt5 GUI.

## 2) Requirements / Installation

> **Windows note (face_recognition/dlib)**: If you face issues installing `dlib` when installing `face-recognition`, try:
> - `pip install cmake`
> - Then either use `pip install dlib-bin` (Windows prebuilt) OR install via Conda (`conda install -c conda-forge dlib`).
> - Then `pip install face-recognition`.
> - If you face issues installing dlib when installing face-recognition:
> - Download the precompiled dlib wheel for Python 3.10 (64-bit):dlib-19.22.99-cp310-cp310-win_amd64.whl

### Steps
```bash
# 1) Create & activate a virtual environment (recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
# source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt
```

## 3) MySQL Setup
Create a database and grant privileges to your user.
```sql
CREATE DATABASE attendance_db;
```

Edit **database.py** with your MySQL `host`, `user`, and `password` if needed.

Initialize tables and create a default admin user:
```bash
python setup_db.py
```
This creates tables and ensures a default admin:
- **username**: `admin`
- **password**: `admin123`
(Change later from the DB for security.)

## 4) Run the App
```bash
python main.py
```

## 5) Default Workflow
- **Student Portal → Enroll**: Captures a single frame, extracts a 128-d face encoding, and stores it as BLOB.
- **Student Portal → Mark Attendance**: Captures current frame, matches against stored encodings, and toggles Login/Logout for **today**.
- **Admin Portal**: Login (admin/admin123). Filter by date range and roll no. Export CSV.

## 6) Project Structure
```
FaceRecognitionAttendance/
│── main.py
│── student_window.py
│── admin_login.py
│── admin_dashboard.py
│── database.py
│── models.py
│── setup_db.py
│── requirements.txt
│── README.md
│── resources/
│   ├── main.ui
│   ├── student.ui
│   ├── admin_login.ui
│   └── admin_dashboard.ui
│── images/
│   └── .gitkeep
```

## 7) Notes
- Ensure good lighting and the face is straight to the camera during enrollment.
- If recognition fails frequently, consider capturing multiple images per user and averaging encodings (extension idea).
- `CURDATE()` in MySQL is used for per-day Login/Logout toggling; adjust to your timezone settings if your DB server is remote.
