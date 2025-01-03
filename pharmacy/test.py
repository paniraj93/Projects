import sqlite3

def inspect_admin_credentials():
    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()

    # Check the admin credentials in the users table
    cursor.execute('SELECT id, name, email, password, is_admin FROM users WHERE is_admin = 1')
    admin_data = cursor.fetchone()
    conn.close()

    if admin_data:
        print(f"Admin Credentials: {admin_data}")
    else:
        print("No admin credentials found!")

if __name__ == "__main__":
    inspect_admin_credentials()
