import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_db():
    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE,
            password TEXT,
            address TEXT,
            is_admin BOOLEAN DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            quantity INTEGER,
            price REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            medicine_id INTEGER,
            quantity INTEGER,
            total REAL,
            FOREIGN KEY (medicine_id) REFERENCES medicines (id)
        )
    """)

    admin_email = "admin@pharmacy.com"
    admin_password = hash_password("admin123")
    cursor.execute("""
        INSERT OR IGNORE INTO users (name, email, password, address, is_admin)
        VALUES (?, ?, ?, ?, ?)
    """, ("Admin", admin_email, admin_password, "Admin HQ", 1))

    conn.commit()
    conn.close()
    print("Database created successfully!")

if __name__ == "__main__":
    create_db()
