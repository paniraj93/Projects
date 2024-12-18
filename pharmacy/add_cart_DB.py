import sqlite3

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('pharmacy.db')

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Create the cart table
cursor.execute("""
CREATE TABLE IF NOT EXISTS cart (
    user_id INTEGER NOT NULL,
    medicine_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    PRIMARY KEY (user_id, medicine_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (medicine_id) REFERENCES medicines(id)
);
""")

print("Cart table created successfully!")

# Commit the changes and close the connection
conn.commit()
conn.close()
