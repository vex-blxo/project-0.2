from flask import Flask, render_template, request, redirect, url_for, flash, session

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/reload')
def reload():
    return render_template("index.html")


# !!!!!!!!!!! Login at Signup !!!!!!!!!!!

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        print(f"Login Attempt: {email}, {password}")
        flash(f"Welcome back, {email}!")
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        print(f"New User: {name}, {email}, {password}")
        flash(f"Thanks for signing up, {name}!")
        return redirect(url_for('home'))
    return render_template('signup.html')


# Renz eto yung sa Cart Icon wla pang naka lagay so ako na bahala dine thx
# Nisabi ko lng kasi baka magalaw mo 
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
def add_to_cart():
    product_id = int(request.form["product_id"])
    quantity = int(request.form["quantity"])

    if "cart" not in session:
        session["cart"] = {}

    cart = session["cart"]

    # If product already in cart, increment quantity
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
    session.modified = True  # ensure session updates are saved

    # 👇 stay on same page instead of jumping to cart
    return redirect(request.referrer or url_for("index"))



@app.route("/cart")
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
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    cart.pop(str(product_id), None)  # safely remove if exists
    session["cart"] = cart
    return redirect(url_for("cart"))


if __name__ == '__main__':
    app.run(debug=True)
