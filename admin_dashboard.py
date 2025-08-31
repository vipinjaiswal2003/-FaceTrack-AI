import pandas as pd
from PyQt5.QtWidgets import QDialog, QMessageBox, QFileDialog, QTableWidgetItem
from PyQt5.uic import loadUi
from database import get_connection

class AdminDashboard(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("resources/admin_dashboard.ui", self)
        self.loadButton.clicked.connect(self.load_attendance)
        self.exportButton.clicked.connect(self.export_attendance)

    def load_attendance(self):
        roll = self.rollInput.text().strip()
        start = self.startDate.date().toString("yyyy-MM-dd")
        end = self.endDate.date().toString("yyyy-MM-dd")

        conn = get_connection()
        where = ["DATE(a.timestamp) BETWEEN %s AND %s"]
        params = [start, end]

        if roll:
            where.append("u.roll_no = %s")
            params.append(roll)

        query = f"""
        SELECT u.name, u.roll_no, a.status, a.timestamp
        FROM attendance a
        JOIN users u ON a.user_id = u.user_id
        WHERE {' AND '.join(where)}
        ORDER BY a.timestamp DESC
        """
        try:
            df = pd.read_sql(query, conn, params=params)
        except Exception as e:
            QMessageBox.critical(self, "DB Error", f"Failed to query: {e}")
            conn.close()
            return
        conn.close()

        self.attendanceTable.setRowCount(len(df))
        self.attendanceTable.setColumnCount(4)
        self.attendanceTable.setHorizontalHeaderLabels(["Name", "Roll No", "Status", "Timestamp"])

        for i, row in df.iterrows():
            self.attendanceTable.setItem(i, 0, QTableWidgetItem(str(row['name'])))
            self.attendanceTable.setItem(i, 1, QTableWidgetItem(str(row['roll_no'])))
            self.attendanceTable.setItem(i, 2, QTableWidgetItem(str(row['status'])))
            self.attendanceTable.setItem(i, 3, QTableWidgetItem(str(row['timestamp'])))

    def export_attendance(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save CSV", "", "CSV Files (*.csv)")
        if not path:
            return
        roll = self.rollInput.text().strip()
        start = self.startDate.date().toString("yyyy-MM-dd")
        end = self.endDate.date().toString("yyyy-MM-dd")

        conn = get_connection()
        where = ["DATE(a.timestamp) BETWEEN %s AND %s"]
        params = [start, end]

        if roll:
            where.append("u.roll_no = %s")
            params.append(roll)

        query = f"""
        SELECT u.name, u.roll_no, a.status, a.timestamp
        FROM attendance a
        JOIN users u ON a.user_id = u.user_id
        WHERE {' AND '.join(where)}
        ORDER BY a.timestamp DESC
        """
        try:
            df = pd.read_sql(query, conn, params=params)
            df.to_csv(path, index=False)
            QMessageBox.information(self, "Export", "Attendance exported successfully!")
        except Exception as e:
            QMessageBox.critical(self, "DB Error", f"Failed to export: {e}")
        finally:
            conn.close()
