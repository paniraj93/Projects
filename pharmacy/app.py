from flask import Flask, render_template, request, redirect, url_for, session, Response
import sqlite3
import hashlib
import io
import matplotlib.pyplot as plt

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Helper function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Route: Home/Login
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hash_password(request.form['password'])

        conn = sqlite3.connect('pharmacy.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, is_admin FROM users WHERE email = ? AND password = ?", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['user_name'] = user[1]
            session['is_admin'] = user[2]
            return redirect(url_for('dashboard') if user[2] else url_for('homepage'))
        else:
            return "Invalid credentials. Please try again."

    return render_template('login.html')

# Route: User Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = hash_password(request.form['password'])
        address = request.form['address']

        conn = sqlite3.connect('pharmacy.db')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (name, email, password, address, is_admin) VALUES (?, ?, ?, ?, ?)",
                           (name, email, password, address, 0))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Email already exists. Please use a different email."
        finally:
            conn.close()
        return redirect(url_for('login'))

    return render_template('signup.html')

# Route: Admin Dashboard
@app.route('/dashboard')
def dashboard():
    if 'is_admin' in session and session['is_admin']:
        conn = sqlite3.connect('pharmacy.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, quantity, price FROM medicines")
        medicines = cursor.fetchall()
        conn.close()
        return render_template('dashboard.html', medicines=medicines)
    return redirect(url_for('login'))

# Route: Homepage for Regular Users
@app.route('/homepage')
def homepage():
    if 'user_id' in session and not session.get('is_admin', False):
        return render_template('homepage.html')
    return redirect(url_for('login'))

# Route: Add Medicine
@app.route('/add_medicine', methods=['GET', 'POST'])
def add_medicine():
    if 'is_admin' in session and session['is_admin']:
        if request.method == 'POST':
            name = request.form['name']
            quantity = int(request.form['quantity'])
            price = float(request.form['price'])

            conn = sqlite3.connect('pharmacy.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO medicines (name, quantity, price) VALUES (?, ?, ?)", (name, quantity, price))
            conn.commit()
            conn.close()
            return redirect(url_for('dashboard'))

        return render_template('add_medicine.html')

    return redirect(url_for('login'))

# Route: Update Medicine
@app.route('/update_medicine', methods=['GET', 'POST'])
def update_medicine():
    if 'is_admin' in session and session['is_admin']:
        if request.method == 'POST':
            medicine_id = int(request.form['medicine_id'])
            quantity = int(request.form['quantity'])

            conn = sqlite3.connect('pharmacy.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE medicines SET quantity = quantity + ? WHERE id = ?", (quantity, medicine_id))
            conn.commit()
            conn.close()
            return redirect(url_for('dashboard'))

        conn = sqlite3.connect('pharmacy.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM medicines")
        medicines = cursor.fetchall()
        conn.close()
        return render_template('update_medicine.html', medicines=medicines)

    return redirect(url_for('login'))

# Route: Sales Graph
@app.route('/sales_graph')
def sales_graph():
    conn = sqlite3.connect('pharmacy.db')
    cursor = conn.cursor()
    cursor.execute("""
        SELECT m.name, SUM(s.quantity) AS total_sold
        FROM sales s
        JOIN medicines m ON s.medicine_id = m.id
        GROUP BY m.id
    """)
    data = cursor.fetchall()
    conn.close()

    if not data:
        return "No sales data available!"

    medicines = [row[0] for row in data]
    quantities = [row[1] for row in data]

    plt.figure(figsize=(10, 6))
    plt.bar(medicines, quantities, color='skyblue')
    plt.title('Sales by Medicine')
    plt.xlabel('Medicine')
    plt.ylabel('Quantity Sold')
    plt.xticks(rotation=45)
    plt.tight_layout()

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return Response(img, mimetype='image/png')

# Route: Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# Route: Search Medicines
@app.route('/search_medicine', methods=['GET', 'POST'])
def search_medicine():
    if 'user_id' in session:
        medicines = []
        if request.method == 'POST':
            search_query = request.form['query']
            conn = sqlite3.connect('pharmacy.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, quantity, price FROM medicines WHERE name LIKE ?", ('%' + search_query + '%',))
            medicines = cursor.fetchall()
            conn.close()
        
        return render_template('search_medicine.html', medicines=medicines)

    return redirect(url_for('login'))

# Route: Add to Cart
@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    if 'user_id' in session:
        medicine_id = int(request.form['medicine_id'])
        quantity = int(request.form['quantity'])

        conn = sqlite3.connect('pharmacy.db')
        cursor = conn.cursor()
        
        # Check if medicine exists
        cursor.execute("SELECT quantity FROM medicines WHERE id = ?", (medicine_id,))
        medicine = cursor.fetchone()

        if not medicine or quantity > medicine[0]:
            conn.close()
            return "Insufficient stock or invalid medicine."

        # Add to user's cart (or update if it exists)
        cursor.execute("""
            INSERT INTO cart (user_id, medicine_id, quantity)
            VALUES (?, ?, ?)
            ON CONFLICT(user_id, medicine_id) DO UPDATE SET quantity = quantity + excluded.quantity
        """, (session['user_id'], medicine_id, quantity))
        conn.commit()
        conn.close()
        return redirect(url_for('search_medicine'))

    return redirect(url_for('login'))

# Route: View Cart
@app.route('/view_cart', methods=['GET'])
def view_cart():
    if 'user_id' in session:
        conn = sqlite3.connect('pharmacy.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.medicine_id, m.name, c.quantity, m.price, (c.quantity * m.price) AS total_price
            FROM cart c
            JOIN medicines m ON c.medicine_id = m.id
            WHERE c.user_id = ?
        """, (session['user_id'],))
        cart_items = cursor.fetchall()
        conn.close()

        total_cost = sum(item[4] for item in cart_items)
        return render_template('view_cart.html', cart_items=cart_items, total_cost=total_cost)

    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
