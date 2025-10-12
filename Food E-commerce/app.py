from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# ===============================
# DATABASE CONNECTION
# ===============================
db = mysql.connector.connect(
    host="localhost",
    user="root",             # your MySQL username
    password="",             # your MySQL password
    database="foodweb_db"
)

# ===============================
# AUTH DECORATORS
# ===============================
def login_required(f):
    """Restrict access to logged-in users only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please log in first to access this page.", "warning")
            return redirect(url_for('login', next=request.path))
        return f(*args, **kwargs)
    return decorated_function


def guest_only(f):
    """Restrict access to *non-logged-in* users only."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' in session:
            flash("You’re already logged in!", "info")
            return redirect(request.referrer or url_for('homepage'))
        return f(*args, **kwargs)
    return decorated_function


# ===============================
# ROUTES
# ===============================
@app.route('/')
def index():
    """Render public index page."""
    return render_template("index.html")



@app.route('/homepage')
@login_required
def homepage():
    """Render homepage for logged-in users."""
    return render_template("homepage.html")


@app.route('/reload')
def reload():
    """Reload homepage."""
    return redirect(url_for("homepage"))


# ===============================
# LOGIN
# ===============================
@app.route('/login', methods=['GET', 'POST'])
@guest_only
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT * FROM accounts WHERE email = %s", (email,))
            user = cursor.fetchone()

            if user and check_password_hash(user['account_password'], password):
                session['user_id'] = user['account_id']
                session['first_name'] = user['first_name']
                session['email'] = user['email']

                flash(f"Welcome back, {user['first_name']}!", "success")

                next_page = request.args.get('next')
                return redirect(next_page or url_for('homepage'))  # 👈 Redirects to homepage
            else:
                flash("Invalid email or password. Please try again.", "error")
                return redirect(url_for('login'))

        except mysql.connector.Error as err:
            print("Database error:", err)
            flash("An error occurred while logging in. Please try again.", "error")

        finally:
            cursor.close()

    return render_template('login.html')


# ===============================
# SIGNUP
# ===============================
@app.route('/signup', methods=['GET', 'POST'])
@guest_only
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            flash("Passwords do not match. Please try again.", "error")
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)

        try:
            cursor = db.cursor()
            cursor.execute("SELECT email FROM accounts WHERE email = %s", (email,))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("Email already registered. Please log in instead.", "warning")
                return redirect(url_for('login'))

            insert_query = """
                INSERT INTO accounts (first_name, last_name, email, account_password)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_query, (first_name, last_name, email, hashed_password))
            db.commit()

            flash(f"Account created successfully! Welcome, {first_name}!", "success")
            return redirect(url_for('login'))

        except mysql.connector.Error as err:
            print("Database error:", err)
            flash("An error occurred while creating your account. Please try again.", "error")

        finally:
            cursor.close()

    return render_template('signup.html')


# ===============================
# CART SYSTEM
# ===============================
products = {
    1: {"name": "All Purpose Flour", "price": 19.99, "stock": 10, "image": "product1.jpg"},
    2: {"name": "Product 2", "price": 29.99, "stock": 8, "image": "product2.jpg"},
    3: {"name": "Product 3", "price": 39.99, "stock": 5, "image": "product3.jpg"},
    5: {"name": "Product 5", "price": 24.99, "stock": 15, "image": "product5.jpg"},
    6: {"name": "Product 6", "price": 34.99, "stock": 20, "image": "product6.jpg"},
    7: {"name": "Product 7", "price": 44.99, "stock": 12, "image": "product7.jpg"},
    8: {"name": "Product 8", "price": 54.99, "stock": 7, "image": "product8.jpg"},
}


@app.route("/add_to_cart", methods=["POST"])
@login_required
def add_to_cart():
    product_id = int(request.form["product_id"])
    quantity = int(request.form["quantity"])

    if "cart" not in session:
        session["cart"] = {}

    cart = session["cart"]

    if str(product_id) in cart:
        cart[str(product_id)]["quantity"] += quantity
    else:
        product = products[product_id]
        cart[str(product_id)] = {
            "id": product_id,
            "name": product["name"],
            "price": product["price"],
            "quantity": quantity,
            "image": product["image"],
        }

    session["cart"] = cart
    session.modified = True

    return redirect(request.referrer or url_for("homepage"))


@app.route("/cart")
@login_required
def cart():
    cart = session.get("cart", {})
    total = sum(item["price"] * item["quantity"] for item in cart.values())
    return render_template("cart.html", cart=cart, total=total)


@app.context_processor
def cart_count():
    cart_quantity = 0
    if "cart" in session:
        cart_quantity = sum(item["quantity"] for item in session["cart"].values())
    return dict(cart_quantity=cart_quantity)


@app.route("/remove/<int:product_id>", methods=["POST"])
@login_required
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    cart.pop(str(product_id), None)
    session["cart"] = cart
    return redirect(url_for("cart"))


# ===============================
# LOGOUT
# ===============================
@app.route('/logout')
@login_required
def logout():
    session.clear()
    flash("You’ve been logged out successfully.", "info")
    return redirect(url_for('login'))

@app.route('/buyer')
def buyer_dashboard():
    return render_template('buyerdashboard.html')



# ===============================
# RUN APP
# ===============================
if __name__ == '__main__':
    app.run(debug=True)
