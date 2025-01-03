import sqlite3
import hashlib
from datetime import datetime

def create_database():
    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()

    # Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        address TEXT NOT NULL,
        is_verified BOOLEAN DEFAULT 0,
        is_admin BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # OTP verification table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS otp_verification (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        otp TEXT NOT NULL,
        purpose TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Medicines table - Updated to match CSV structure
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        is_banned INTEGER DEFAULT 0,
        manufacturer_name TEXT,
        type TEXT,
        pack_size_label TEXT,
        short_composition1 TEXT,
        short_composition2 TEXT,
        stock INTEGER DEFAULT 100,
        requires_prescription INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Cart table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        medicine_id INTEGER,
        quantity INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (medicine_id) REFERENCES medicines (id)
    )
    ''')

    # Orders table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        total_amount REAL NOT NULL,
        status TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')

    # Order details table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS order_details (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER,
        medicine_id INTEGER,
        quantity INTEGER NOT NULL,
        price_per_unit REAL NOT NULL,
        prescription_image TEXT,
        FOREIGN KEY (order_id) REFERENCES orders (id),
        FOREIGN KEY (medicine_id) REFERENCES medicines (id)
    )
    ''')

    # Sales table for analytics
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_id INTEGER,
        quantity INTEGER NOT NULL,
        total_amount REAL NOT NULL,
        sale_date DATE NOT NULL,
        FOREIGN KEY (medicine_id) REFERENCES medicines (id)
    )
    ''')

    # Create admin user
    admin_password = hashlib.sha256("admin123".encode()).hexdigest()
    try:
        cursor.execute('''
        INSERT INTO users (name, email, password, address, is_verified, is_admin)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', ('Admin', 'admin@pharmacy.com', admin_password, 'Admin Address', 1, 1))
    except sqlite3.IntegrityError:
        print("Admin user already exists")

    # Insert some banned medicines with corrected structure
    banned_medicines = [
        (1, 'Heroin', 1000.0, 1, 'Illegal', 'Opioid', '1g', 'Diacetylmorphine', None, 0),
        (2, 'Cocaine', 1000.0, 1, 'Illegal', 'Stimulant', '1g', 'Cocaine Hydrochloride', None, 0),
        (3, 'Methamphetamine', 1000.0, 1, 'Illegal', 'Stimulant', '1g', 'Methamphetamine HCl', None, 0)
    ]

    for medicine in banned_medicines:
        try:
            cursor.execute('''
            INSERT OR REPLACE INTO medicines 
            (id, name, price, is_banned, manufacturer_name, type, pack_size_label, 
            short_composition1, short_composition2, stock)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', medicine)
        except sqlite3.IntegrityError:
            print(f"Medicine {medicine[1]} already exists")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()
    print("Database created successfully!")