from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
import sqlite3
import hashlib
import os
import smtplib
from email.mime.text import MIMEText
import random
import string
from functools import wraps
from datetime import datetime
import json
from PIL import Image
import plotly.express as px
import base64

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
UPLOAD_FOLDER = 'static/prescriptions'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Database connection helper
def get_db():
    conn = sqlite3.connect('pharmacy.db')
    conn.row_factory = sqlite3.Row
    return conn

def is__admin():
    user_id = session.get('user_id')
    if user_id:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT is_admin FROM users WHERE id = ?', (user_id,))
        result = cursor.fetchone()
        db.close()
        if result and result[0] == 1:  # Check if is_admin is TRUE (1)
            return True
    return False

def is_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('is_admin'):
            return redirect(url_for('home'))  # Redirect to a page for non-admin users
        return f(*args, **kwargs)  # Call the decorated function if admin
    return decorated_function

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Admin required decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or not session.get('is_admin'):
            flash('Admin access required')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Email sending function
def send_otp_email(email, otp):
    sender_email = os.getenv('EMAIL')
    sender_password = 'suos gktg lmjz dfoi'
    
    msg = MIMEText(f'Your OTP for verification is: {otp}')
    msg['Subject'] = 'Pharmacy - Email Verification OTP'
    msg['From'] = sender_email
    msg['To'] = email
    
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(sender_email, sender_password)
            smtp_server.sendmail(sender_email, email, msg.as_string())
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

# Routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        
        db = get_db()
        cursor = db.cursor()
        
        # Check if user exists
        cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
        user = cursor.fetchone()
        
        if user:
            session['user_id'] = user['id']
            session['is_admin'] = user['is_admin']  # Store is_admin in session
            
            flash('Login successful')
            
            if user['is_admin']:  # Check if the user is an admin
                return redirect(url_for('admin_dashboard'))  # Redirect to admin dashboard
            else:
                return redirect(url_for('home'))  # Redirect to home for regular users
        else:
            flash('Invalid email or password')
        
        db.close()
    
    return render_template('login.html')

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not is__admin():  # Ensure the user is an admin
        flash('You do not have access to this page.')
        return redirect(url_for('home'))  # Redirect to home for non-admin users
    
    return render_template('admin_dashboard.html')

@app.route('/view_users')
@login_required
@is_admin  # Only allow access if the user is an admin
def view_users():
    db = get_db()
    cursor = db.cursor()
    
    # Query to get all users (or any user-related information)
    cursor.execute('SELECT * FROM users where is_admin = 0')
    users = cursor.fetchall()
    db.close()
    
    return render_template('view_users.html', users=users)


@app.route('/')
def home():
    page = request.args.get('page', 1, type=int)
    per_page = 9  # Number of medicines per page
    
    db = get_db()
    cursor = db.cursor()
    
    # Get total number of non-banned medicines
    cursor.execute('SELECT COUNT(*) FROM medicines WHERE is_banned = 0')
    total_medicines = cursor.fetchone()[0]
    
    # Calculate total pages
    total_pages = (total_medicines + per_page - 1) // per_page
    
    # Get medicines for current page
    offset = (page - 1) * per_page
    cursor.execute('''
        SELECT * FROM medicines 
        WHERE is_banned = 0 
        ORDER BY name ASC 
        LIMIT ? OFFSET ?
    ''', (per_page, offset))
    
    medicines = cursor.fetchall()
    db.close()
    
    return render_template('home.html', 
                       medicines=medicines,
                       page=page,
                       total_pages=total_pages,
                       max=max,
                       min=min)


@app.route('/search')
def search():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    db = get_db()
    cursor = db.cursor()
    
    # Get total matching medicines
    cursor.execute('''
        SELECT COUNT(*) FROM medicines 
        WHERE is_banned = 0 
        AND (name LIKE ? OR manufacturer_name LIKE ? OR short_composition1 LIKE ?)
    ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
    
    total_medicines = cursor.fetchone()[0]
    total_pages = (total_medicines + per_page - 1) // per_page
    
    # Get matching medicines for current page
    offset = (page - 1) * per_page
    cursor.execute('''
        SELECT * FROM medicines 
        WHERE is_banned = 0 
        AND (name LIKE ? OR manufacturer_name LIKE ? OR short_composition1 LIKE ?)
        ORDER BY name ASC 
        LIMIT ? OFFSET ?
    ''', (f'%{query}%', f'%{query}%', f'%{query}%', per_page, offset))
    
    medicines = cursor.fetchall()
    db.close()
    
    return render_template('home.html',
                         medicines=medicines,
                         page=page,
                         total_pages=total_pages)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        address = request.form['address']
        
        # Generate OTP
        otp = ''.join(random.choices(string.digits, k=6))
        session['signup_data'] = {'name': name, 'email': email, 'password': password, 'address': address, 'otp': otp}

        # Send OTP email
        if send_otp_email(email, otp):
            flash('OTP sent to your email. Please verify.')
            return redirect(url_for('verify_otp'))
        else:
            flash('Error sending OTP. Please try again.')

    return render_template('signup.html')

# Route: Verify OTP
@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if 'signup_data' not in session:
        return redirect(url_for('signup'))

    if request.method == 'POST':
        entered_otp = request.form['otp']
        generated_otp = session['signup_data']['otp']
        
        if entered_otp == generated_otp:
            # Add user to the database
            db = get_db()
            cursor = db.cursor()
            signup_data = session.pop('signup_data')
            cursor.execute('''
                INSERT INTO users (name, email, password, address)
                VALUES (?, ?, ?, ?)
            ''', (signup_data['name'], signup_data['email'], signup_data['password'], signup_data['address']))
            db.commit()
            db.close()

            flash('Signup successful! You can now log in.')
            return redirect(url_for('login'))
        else:
            flash('Invalid OTP. Please try again.')

    return render_template('verify_otp.html')


@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    if 'user_id' not in session:
        flash('Please login to add items to cart')
        return redirect(url_for('login'))
    
    medicine_id = request.form.get('medicine_id')
    quantity = int(request.form.get('quantity', 1))
    
    if not medicine_id or quantity <= 0:
        flash('Invalid request')
        return redirect(url_for('home'))
    
    db = get_db()
    cursor = db.cursor()
    
    # Check if medicine exists and has enough stock
    cursor.execute('SELECT * FROM medicines WHERE id = ?', (medicine_id,))
    medicine = cursor.fetchone()
    
    if not medicine:
        flash('Medicine not found')
        return redirect(url_for('home'))
    
    if medicine['stock'] < quantity:
        flash('Not enough stock available')
        return redirect(url_for('home'))
    
    # Check if medicine requires prescription
    if medicine['requires_prescription'] == 1:
        # You might want to handle prescription upload here
        flash('This medicine requires a prescription. Please upload one.')
        return redirect(url_for('upload_prescription', medicine_id=medicine_id))
    
    # Check if item already in cart, update quantity if it is
    cursor.execute('''
        SELECT * FROM cart 
        WHERE user_id = ? AND medicine_id = ?
    ''', (session['user_id'], medicine_id))
    
    cart_item = cursor.fetchone()
    
    try:
        if cart_item:
            new_quantity = cart_item['quantity'] + quantity
            cursor.execute('''
                UPDATE cart 
                SET quantity = ? 
                WHERE user_id = ? AND medicine_id = ?
            ''', (new_quantity, session['user_id'], medicine_id))
        else:
            cursor.execute('''
                INSERT INTO cart (user_id, medicine_id, quantity)
                VALUES (?, ?, ?)
            ''', (session['user_id'], medicine_id, quantity))
        
        db.commit()
        flash('Item added to cart successfully')
    except sqlite3.Error as e:
        db.rollback()
        flash('Error adding item to cart')
        print(f"Database error: {e}")
    finally:
        db.close()
    
    return redirect(url_for('view_cart'))

@app.route('/cart')
@login_required
def view_cart():
    db = get_db()
    cursor = db.cursor()
    
    # Get cart items with medicine details
    cursor.execute('''
        SELECT c.id, c.quantity, m.name, m.price, m.stock, m.requires_prescription,
               (c.quantity * m.price) as subtotal
        FROM cart c
        JOIN medicines m ON c.medicine_id = m.id
        WHERE c.user_id = ?
    ''', (session['user_id'],))
    
    cart_items = cursor.fetchall()
    
    # Calculate total
    total = sum(item['subtotal'] for item in cart_items)
    
    db.close()
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/cart/update', methods=['POST'])
@login_required
def update_cart():
    cart_id = request.form.get('cart_id')
    quantity = int(request.form.get('quantity', 0))
    
    if quantity <= 0:
        return remove_from_cart(cart_id)
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute('''
            UPDATE cart 
            SET quantity = ? 
            WHERE id = ? AND user_id = ?
        ''', (quantity, cart_id, session['user_id']))
        db.commit()
        flash('Cart updated successfully')
    except sqlite3.Error:
        db.rollback()
        flash('Error updating cart')
    finally:
        db.close()
    
    return redirect(url_for('view_cart'))

@app.route('/cart/remove/<int:cart_id>')
@login_required
def remove_from_cart(cart_id):
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute('''
            DELETE FROM cart 
            WHERE id = ? AND user_id = ?
        ''', (cart_id, session['user_id']))
        db.commit()
        flash('Item removed from cart')
    except sqlite3.Error:
        db.rollback()
        flash('Error removing item from cart')
    finally:
        db.close()
    
    return redirect(url_for('view_cart'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        
        db = get_db()
        cursor = db.cursor()
        
        # Check if email exists in the users table
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if user:
            # Generate OTP
            otp = ''.join(random.choices(string.digits, k=6))
            
            # Store OTP in the otp_verification table
            cursor.execute(''' 
            INSERT INTO otp_verification (email, otp, purpose) 
            VALUES (?, ?, ?) 
            ''', (email, otp, 'forgot_password'))
            db.commit()
            
            # Send OTP email
            if send_otp_email(email, otp):
                flash('Please check your email for OTP verification')
                return redirect(url_for('verify_forgot_password_otp', email=email))  # Redirect to OTP verification
            else:
                flash('Error sending OTP email')
        else:
            flash('Email not found')
        
        db.close()
    
    return render_template('forgot_password.html')

@app.route('/verify_forgot_password_otp', methods=['GET', 'POST'])
def verify_forgot_password_otp():
    email = request.args.get('email', '')
    
    if request.method == 'POST':
        otp = request.form['otp']
        
        db = get_db()
        cursor = db.cursor()
        
        # Check if OTP matches
        cursor.execute(''' 
        SELECT * FROM otp_verification WHERE email = ? AND otp = ? AND purpose = 'forgot_password' 
        ''', (email, otp))
        
        otp_record = cursor.fetchone()
        
        if otp_record:
            # Allow the user to reset their password
            return redirect(url_for('reset_password', email=email))
        else:
            flash('Invalid OTP')
        
        db.close()
    
    return render_template('verify_forgot_password_otp.html', email=email)

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    email = request.args.get('email', '')
    
    if request.method == 'POST':
        new_password = request.form['password']
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
        
        db = get_db()
        cursor = db.cursor()
        
        # Update the password for the user
        cursor.execute(''' 
        UPDATE users SET password = ? WHERE email = ? 
        ''', (hashed_password, email))
        db.commit()
        db.close()
        
        flash('Password reset successfully')
        return redirect(url_for('login'))  # Redirect to the login page after password reset
    
    return render_template('reset_password.html', email=email)

import os
from werkzeug.utils import secure_filename

# Check if file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from PIL import Image
import io

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

@app.route('/upload_prescription/<int:medicine_id>', methods=['GET', 'POST'])
@login_required
def upload_prescription(medicine_id):
    if request.method == 'POST':
        if 'prescription' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['prescription']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            # Open the uploaded file using Pillow
            image = Image.open(file.stream)
            
            # Convert the image to RGB and then to JPG
            image = image.convert("RGB")
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format="JPEG")
            img_byte_arr.seek(0)  # Rewind the byte array to the beginning
            
            # Get the byte data
            img_data = img_byte_arr.read()
            
            # Insert the prescription details (image bytes) into the database
            db = get_db()
            cursor = db.cursor()
            
            cursor.execute('''
                INSERT INTO prescriptions (user_id, medicine_id, prescription_file) 
                VALUES (?, ?, ?)
            ''', (session['user_id'], medicine_id, img_data))  # Pass img_data as bytes
            db.commit()
            db.close()
            
            flash('Prescription uploaded and converted successfully')
            return redirect(url_for('view_cart'))  # Redirect to cart or any desired page
        else:
            flash('Invalid file type')
    
    return render_template('upload_prescription.html', medicine_id=medicine_id)


@app.route('/view_orders')
@login_required  # Ensure the user is logged in
def view_orders():
    db = get_db()
    cursor = db.cursor()
    
    # Query to join orders with medicines, assuming the orders table has a medicine_id
    cursor.execute('''
        SELECT o.id, m.name AS medicine_name, oi.quantity, o.total_amount AS total_price, o.status, o.created_at AS order_date
        FROM orders o
        JOIN order_details oi ON o.id = oi.order_id
        JOIN medicines m ON oi.medicine_id = m.id
        WHERE o.user_id = ?
    ''', (session['user_id'],))
    
    orders = cursor.fetchall()
    db.close()
    
    return render_template('view_orders.html', orders=orders)



@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    db = get_db()
    cursor = db.cursor()
    
    # Get cart items with medicine details
    cursor.execute(''' 
        SELECT c.id, c.quantity, m.id AS medicine_id, m.name, m.price, (c.quantity * m.price) as subtotal
        FROM cart c
        JOIN medicines m ON c.medicine_id = m.id
        WHERE c.user_id = ?
    ''', (session['user_id'],))
    
    cart_items = cursor.fetchall()
    
    if not cart_items:
        flash('Your cart is empty')
        return redirect(url_for('home'))
    
    # Calculate total price
    total = sum(item['subtotal'] for item in cart_items)

    if request.method == 'POST':
        # Handle order submission (for simplicity, no payment gateway here)
        order_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        order_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Insert order into the database
        cursor.execute('''
            INSERT INTO orders (user_id, total_amount, status, created_at)
            VALUES (?, ?, ?, ?)
        ''', (session['user_id'], total, 'Pending', order_date))
        db.commit()

        # Fetch the newly inserted order ID (this is necessary as it's AUTOINCREMENT in the 'orders' table)
        order_id = cursor.lastrowid

        # Add items to the order details table
        for item in cart_items:
            cursor.execute('''
                INSERT INTO order_details (order_id, medicine_id, quantity, price_per_unit, prescription_image)
                VALUES (?, ?, ?, ?, ?)
            ''', (order_id, item['medicine_id'], item['quantity'], item['price'], None))  # Assuming None for prescription_image
        db.commit()

        # Clear the user's cart after order
        cursor.execute('DELETE FROM cart WHERE user_id = ?', (session['user_id'],))
        db.commit()
        
        # Redirect to a success page or order details page
        flash('Order placed successfully!')
        return redirect(url_for('order_success', order_id=order_id))


    db.close()
    
    return render_template('checkout.html', cart_items=cart_items, total=total)


@app.route('/view_prescriptions')
@login_required
def view_prescriptions():
    user_id = session.get('user_id')
    db = get_db()
    cursor = db.cursor()

    # Fetch prescriptions with medicine names for the logged-in user
    cursor.execute('''
        SELECT p.id, p.medicine_id, p.prescription_file, p.status, p.created_at, m.name AS medicine_name
        FROM prescriptions p
        JOIN medicines m ON p.medicine_id = m.id
        WHERE p.user_id = ?
    ''', (user_id,))
    prescriptions = cursor.fetchall()

    db.close()

    # Prepare prescriptions with base64-encoded images
    prescriptions_with_images = []
    for prescription in prescriptions:
        # Convert prescription_row to dictionary
        prescription_dict = dict(prescription)
        prescription_dict['prescription_file'] = base64.b64encode(prescription_dict['prescription_file']).decode('utf-8')
        prescriptions_with_images.append(prescription_dict)

    return render_template('view_prescriptions.html', prescriptions=prescriptions_with_images)

@app.route('/update_prescription_status/<int:prescription_id>', methods=['POST'])
@login_required
def update_prescription_status(prescription_id):
    # Ensure the user is an admin
    if not session.get('is_admin'):
        flash('You do not have permission to access this page.')
        return redirect(url_for('home'))  # Redirect to home or any appropriate page

    # Get the new status from the form
    new_status = request.form['status']
    
    # Update the prescription status in the database
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Update the status in the prescriptions table
        cursor.execute('''
            UPDATE prescriptions
            SET status = ?
            WHERE id = ?
        ''', (new_status, prescription_id))
        
        # Get the medicine_id from the prescription
        cursor.execute('''
            SELECT medicine_id, user_id
            FROM prescriptions 
            WHERE id = ? AND status = ?
        ''', (prescription_id, "Approved"))
        medicine = cursor.fetchone()

        # Ensure the medicine_id exists
        if not medicine:
            flash('No matching prescription found.')
            db.rollback()
            return redirect(url_for('admin_view_prescriptions'))

        # Check if the item is already in the cart
        cursor.execute('''
            SELECT * FROM cart 
            WHERE user_id = ? AND medicine_id = ?
        ''', (medicine['user_id'], medicine['medicine_id']))
        cart_item = cursor.fetchone()
        
        if cart_item:
            # Update the quantity if the item exists in the cart
            quantity = 1
            new_quantity = cart_item['quantity'] + quantity
            cursor.execute('''
                UPDATE cart 
                SET quantity = ? 
                WHERE user_id = ? AND medicine_id = ?
            ''', (new_quantity, medicine['user_id'], medicine['medicine_id']))
        else:
            # Insert a new item into the cart
            cursor.execute('''
                INSERT INTO cart (user_id, medicine_id, quantity)
                VALUES (?, ?, ?)
            ''', (medicine['user_id'], medicine['medicine_id'], 1))
        
        db.commit()
        flash('Item added to cart successfully.')
    
    except sqlite3.Error as e:
        db.rollback()
        flash('Error adding item to cart.')
        print(f"Database error: {e}")
    
    finally:
        db.close()

    flash('Prescription status updated successfully.')
    return redirect(url_for('admin_view_prescriptions'))  # Redirect to the prescriptions view page


@app.route('/admin_view_prescriptions')
@login_required
def admin_view_prescriptions():
    # Ensure the user is an admin
    if not session.get('is_admin'):
        flash('You do not have permission to access this page.')
        return redirect(url_for('home'))  # Redirect to home or any appropriate page

    # Fetch prescriptions along with medicine names
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT p.id, p.medicine_id, p.prescription_file, p.status, p.created_at, m.name AS medicine_name
        FROM prescriptions p
        JOIN medicines m ON p.medicine_id = m.id
    ''')
    prescriptions = cursor.fetchall()

    # Convert prescription files from binary to base64
    for i, prescription in enumerate(prescriptions):
        prescription_dict = dict(prescription)  # Convert sqlite3.Row to dict
        if isinstance(prescription_dict['prescription_file'], bytes):
            prescription_dict['prescription_file'] = base64.b64encode(prescription_dict['prescription_file']).decode('utf-8')
        prescriptions[i] = prescription_dict  # Replace the row with the dict

    db.close()

    return render_template('admin_view_prescriptions.html', prescriptions=prescriptions)



@app.route('/order_success/<order_id>')
@login_required
def order_success(order_id):
    # Fetch order details based on order_id
    db = get_db()
    cursor = db.cursor()

    cursor.execute('''
        SELECT o.id, o.user_id, o.total_amount, o.status, o.created_at
        FROM orders o
        WHERE o.id = ?
    ''', (order_id,))
    order = cursor.fetchone()

    if not order:
        flash('Order not found!')
        return redirect(url_for('home'))

    db.close()
    
    return render_template('order_success.html', order=order)

@app.route('/sales_dashboard')
def sales_dashboard():
    # Connect to the database and fetch sales data
    db = get_db()
    cursor = db.cursor()
    
    # Fetch sales data: You can modify the SQL query according to your database schema
    cursor.execute('''
        SELECT created_at as date, SUM(total_amount) as daily_sales
        FROM orders
        GROUP BY date
        ORDER BY date
    ''')
    sales_data = cursor.fetchall()

    # Prepare data for plotting (convert to lists)
    dates = [row['date'] for row in sales_data]
    sales = [row['daily_sales'] for row in sales_data]
    
    # Create a plotly graph for sales trends
    fig = px.line(x=dates, y=sales, labels={'x': 'Date', 'y': 'Sales Amount'}, title="Sales Trends Over Time")
    graph_html = fig.to_html(full_html=False)

    db.close()

    return render_template('sales_dashboard.html', graph_html=graph_html)

@app.route('/sales_by_category')
def sales_by_category():
    db = get_db()
    cursor = db.cursor()

    # Fetch sales data by category
    cursor.execute('''
        SELECT c.name AS category_name, SUM(o.total_amount) AS total_sales
        FROM orders o
        JOIN order_details od ON o.id = od.order_id
        JOIN medicines m ON od.medicine_id = m.id
        JOIN categories c ON m.category_id = c.id
        GROUP BY c.name
    ''')
    category_sales = cursor.fetchall()

    categories = [row['category_name'] for row in category_sales]
    sales = [row['total_sales'] for row in category_sales]

    # Create a pie chart using Plotly
    fig = px.pie(names=categories, values=sales, title="Sales by Category")
    pie_chart_html = fig.to_html(full_html=False)

    db.close()

    return render_template('sales_by_category.html', pie_chart_html=pie_chart_html)

@app.route('/view_medicines', defaults={'page': 1})
@app.route('/view_medicines/<int:page>')
@login_required
def view_medicines(page=1):
    # Define how many medicines to display per page
    per_page = 9
    offset = (page - 1) * per_page
    
    db = get_db()
    cursor = db.cursor()
    
    # Query to fetch medicines for the current page
    cursor.execute('''
        SELECT * FROM medicines LIMIT ? OFFSET ?
    ''', (per_page, offset))
    medicines = cursor.fetchall()
    
    # Query to get the total number of medicines
    cursor.execute('SELECT COUNT(*) FROM medicines')
    total_medicines = cursor.fetchone()[0]
    
    db.close()

    # Calculate the total number of pages
    total_pages = (total_medicines // per_page) + (1 if total_medicines % per_page > 0 else 0)
    
    return render_template('view_medicines.html', medicines=medicines, page=page, total_pages=total_pages)

@app.route('/increase_stock/<int:medicine_id>', methods=['GET', 'POST'])
@login_required
def increase_stock(medicine_id):
    db = get_db()
    cursor = db.cursor()

    # Check if the medicine exists
    cursor.execute('SELECT * FROM medicines WHERE id = ?', (medicine_id,))
    medicine = cursor.fetchone()

    if not medicine:
        flash("Medicine not found!", "error")
        return redirect(url_for('view_medicines', page=1))

    if request.method == 'POST':
        # Get the stock increment value from the form
        increase_amount = request.form.get('increase_amount', type=int)

        if increase_amount and increase_amount > 0:
            # Update the stock quantity in the database
            cursor.execute('UPDATE medicines SET stock = stock + ? WHERE id = ?', (increase_amount, medicine_id))
            db.commit()

            flash(f"Stock increased by {increase_amount} units.", "success")
            return redirect(url_for('view_medicines', page=1))
        else:
            flash("Please enter a valid quantity.", "error")

    # Render the page for increasing stock
    return render_template('increase_stock.html', medicine=medicine)

@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)