from database import create_tables, get_connection, fetchall, execute
import bcrypt

def ensure_default_admin():
    # Create default admin (admin/admin123) if no admins exist
    rows = fetchall("SELECT COUNT(*) FROM admins")
    if rows and rows[0][0] == 0:
        username = "admin"
        raw = "admin123".encode('utf-8')
        hashed = bcrypt.hashpw(raw, bcrypt.gensalt()).decode('utf-8')
        execute("INSERT INTO admins (username, password_hash) VALUES (%s,%s)", (username, hashed))
        print("Default admin created: username=admin, password=admin123")

if __name__ == "__main__":
    create_tables()
    ensure_default_admin()
    print("Database initialized.")
