import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QWidget, QVBoxLayout
from PyQt5.uic import loadUi
from student_window import StudentWindow
from admin_login import AdminLogin
from admin_dashboard import AdminDashboard

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Face Recognition Attendance System")
        central = QWidget()
        layout = QVBoxLayout(central)

        self.btn_student = QPushButton("Open Student Portal")
        self.btn_admin = QPushButton("Open Admin Portal")

        layout.addWidget(self.btn_student)
        layout.addWidget(self.btn_admin)
        self.setCentralWidget(central)

        self.btn_student.clicked.connect(self.open_student)
        self.btn_admin.clicked.connect(self.open_admin)

    def open_student(self):
        self.student = StudentWindow(self)
        self.student.show()

    def open_admin(self):
        login = AdminLogin(self)
        if login.exec_() == login.Accepted:
            self.admin = AdminDashboard(self)
            self.admin.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.resize(360, 160)
    w.show()
    sys.exit(app.exec_())
