import cv2
import numpy as np
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from database import get_connection
from models import encode_face, compare_faces


class StudentWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("resources/student.ui", self)

        # Camera setup
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # Start the camera feed immediately
        self.start_camera()

        # Button actions
        self.enrollButton.clicked.connect(self.enroll_student)
        self.attendanceButton.clicked.connect(self.mark_attendance)

    # ---------------- Camera Methods ----------------
    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            QMessageBox.critical(self, "Camera Error", "Could not access camera.")
            return
        self.timer.start(30)  # update every 30 ms (~30 FPS)

    def stop_camera(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        self.timer.stop()

    def update_frame(self):
        if not self.cap:
            return
        ok, frame = self.cap.read()
        if not ok:
            return
        # Convert frame for display
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qt_img = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.videoLabel.setPixmap(QPixmap.fromImage(qt_img))

    def _capture_frame(self):
        """Capture one frame for recognition/enrollment"""
        if not self.cap:
            self.start_camera()
        ok, frame = self.cap.read()
        return frame if ok else None

    def closeEvent(self, event):
        """Stop camera when window closes"""
        self.stop_camera()
        event.accept()

    # ---------------- Enroll Student ----------------
    def enroll_student(self):
        name = self.nameInput.text().strip()
        roll = self.rollInput.text().strip()
        dept = self.deptInput.text().strip()
        if not name or not roll:
            QMessageBox.warning(self, "Missing Data", "Name and Roll No are required.")
            return

        frame = self._capture_frame()
        if frame is None:
            QMessageBox.critical(self, "Camera Error", "Could not capture image.")
            return

        encoding = encode_face(frame)
        if encoding is None:
            QMessageBox.warning(self, "Face Not Detected", "Please ensure your face is clearly visible.")
            return

        enc_bytes = encoding.astype(np.float64).tobytes()
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (name, roll_no, department, face_encoding) VALUES (%s,%s,%s,%s)",
                (name, roll, dept, enc_bytes)
            )
            conn.commit()
            QMessageBox.information(self, "Enrolled", f"{name} ({roll}) enrolled successfully.")
            self.nameInput.clear(); self.rollInput.clear(); self.deptInput.clear()
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "DB Error", f"Failed to enroll: {e}")
        finally:
            cur.close(); conn.close()

    # ---------------- Mark Attendance ----------------
    def mark_attendance(self):
        frame = self._capture_frame()
        if frame is None:
            QMessageBox.critical(self, "Camera Error", "Could not capture image.")
            return

        enc = encode_face(frame)
        if enc is None:
            QMessageBox.warning(self, "Face Not Detected", "Please ensure your face is clearly visible.")
            return

        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT user_id, face_encoding FROM users")
            rows = cur.fetchall()
            if not rows:
                QMessageBox.information(self, "No Users", "No enrolled users found.")
                return
            ids = [r[0] for r in rows]
            known = [np.frombuffer(r[1], dtype=np.float64) for r in rows]

            idx = compare_faces(known, enc)
            if idx is None:
                QMessageBox.warning(self, "Unknown Face", "Face not recognized. Please enroll first.")
                return

            user_id = ids[idx]
            # Toggle Login/Logout
            cur.execute(
                "SELECT status FROM attendance WHERE user_id=%s AND DATE(timestamp)=CURDATE() "
                "ORDER BY timestamp DESC LIMIT 1",
                (user_id,)
            )
            last = cur.fetchone()
            next_status = 'Logout' if (last and last[0] == 'Login') else 'Login'
            cur.execute("INSERT INTO attendance (user_id, status) VALUES (%s,%s)", (user_id, next_status))
            conn.commit()
            QMessageBox.information(self, "Attendance", f"{next_status} recorded.")
        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "DB Error", f"Failed to mark attendance: {e}")
        finally:
            cur.close(); conn.close()
