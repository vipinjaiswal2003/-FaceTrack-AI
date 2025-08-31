import bcrypt
from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.uic import loadUi
from database import get_connection

class AdminLogin(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("resources/admin_login.ui", self)
        self.loginButton.clicked.connect(self.try_login)

    def try_login(self):
        username = self.usernameInput.text().strip()
        password = self.passwordInput.text().encode('utf-8')
        if not username or not password:
            QMessageBox.warning(self, "Missing", "Enter username and password.")
            return
        conn = get_connection()
        cur = conn.cursor()
        try:
            cur.execute("SELECT password_hash FROM admins WHERE username=%s", (username,))
            row = cur.fetchone()
            if not row:
                QMessageBox.critical(self, "Error", "Invalid credentials.")
                return
            pw_hash = row[0].encode('utf-8')
            if bcrypt.checkpw(password, pw_hash):
                self.accept()  # success
            else:
                QMessageBox.critical(self, "Error", "Invalid credentials.")
        finally:
            cur.close(); conn.close()
