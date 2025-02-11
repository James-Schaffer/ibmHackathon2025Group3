
# # Group model
# class Group(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(150), unique=True, nullable=False)
#     code = db.Column(db.String(150), unique=True, nullable=False)
#     users = db.relationship('User', backref='group', lazy=True)

# # Tag model
# class Tag(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(150), unique=True, nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     purchases_tags = db.relationship('PurchasesTags', backref='tag', lazy=True)

# Create database tables
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
import google.generativeai as genai
from PIL import Image
import json
import re
from sqlalchemy.types import Numeric  # Supports decimal values
from datetime import date  # For stamping purchase date

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = "3$Yh9K|@w2Z*bN-gfdtrstrdrcea666b53c"
DB_NAME = "database.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
app.config["REMEMBER_COOKIE_DURATION"] = 86400  # 1 day session
app.config["SESSION_PERMANENT"] = True

# Database initialization
db = SQLAlchemy()
db.init_app(app)

spending_categories = [
    "Food & Drinks",
    "Transportation",
    "School Supplies",
    "Rent & Utilities",
    "Phone Bill",
    "Entertainment",
    "Clothing & Accessories",
    "Personal Care",
    "Fitness",
    "Socializing",
    "Tuition & Fees",
    "Online Subscriptions",
    "Emergency Fund & Savings",
    "other"
]

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    budget = db.Column(db.Integer, nullable=True)
    # One-to-Many relationship
    purchases = db.relationship('Purchase', back_populates='user', lazy=True)

# Purchases model
class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(150), nullable=False)
    price = db.Column(Numeric(10, 2), nullable=False)  # Supports decimals
    category = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date)
    # Relationship back to User
    user = db.relationship('User', back_populates='purchases')

# Create database tables
with app.app_context():
    db.create_all()

# Configure generative AI model
genai.configure(api_key="AIzaSyAMnCFsSFcXpOAfQzv05gLk4NuGjymRaLM")
model = genai.GenerativeModel("gemini-1.5-flash")

# Login manager setup
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ---------------- Routes ----------------

@app.route("/", methods=["GET", "POST"])
def welcome():
    return render_template("welcome.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect("/home")
        return "Invalid username or password : From Server"
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if not username or not password:
            flash("Username and password are required!", "error")
            return redirect(url_for("signup"))
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists. Please log in or choose a different username."
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully! Please login.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/update_budget", methods=["POST", "GET"])
def update_budget():
    return redirect(url_for("login"))

@app.route("/profile")
@login_required
def profile():
    purchases = Purchase.query.filter_by(user_id=current_user.id).order_by(Purchase.date.desc()).limit(5).all()
    return render_template("profile.html", user=current_user, purchases=purchases)

@app.route("/expenses", methods=["GET", "POST"])
@login_required
def expenses():
    if request.method == "POST":
        label = request.form.get("label")
        price = request.form.get("price")
        response = model.generate_content(
            f"Classify the following purchase =>({label}) into one of the predefined spending categories: "
            "[Food & Drinks, Transportation, School Supplies, Rent & Utilities, Phone Bill, Entertainment, "
            "Clothing & Accessories, Personal Care, Fitness, Socializing, Tuition & Fees, Online Subscriptions, "
            "Emergency Fund & Savings,others]. Only return the category name. Do not include any extra text."
        )
        print(response.text)
        purchase = Purchase(label=label, price=price, category=response.text, user_id=current_user.id)
        db.session.add(purchase)
        db.session.commit()
    purchases = Purchase.query.filter(Purchase.user_id == current_user.id).order_by(Purchase.id.desc()).all()
    return render_template("expenses.html", purchases=purchases)

@app.route("/leaderboard")
@login_required
def leaderboard():
    return render_template("leaderboard.html")

@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "POST":
        budget = request.get_json()
        if 'budget' not in budget or not isinstance(budget['budget'], int):
            return jsonify({'error': 'Invalid budget value'}), 400
        current_user.budget = budget['budget']
        db.session.commit()
        return jsonify({'message': 'Budget updated successfully', 'budget': budget['budget']}), 200
    purchases = Purchase.query.filter(Purchase.user_id == current_user.id).order_by(Purchase.id.desc()).all()
    return render_template("home.html", purchases=purchases, budget=current_user.budget, user=current_user.username)

@app.route("/savings")
@login_required
def savings():
    purchases_by_category = {}
    for category in spending_categories:
        purchases = Purchase.query.filter_by(category=category).all()
        purchases_by_category[category] = purchases
    return render_template("savings.html", purchases_by_category=purchases_by_category)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# --------------- Image Capture & Extraction ----------------

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/capture', methods=['GET'])
def capture():
    """Serve the capture.html page."""
    return render_template('capture.html')

@app.route('/capture', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file uploaded'}), 400
    image_file = request.files['image']
    if image_file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_file.filename)
    image_file.save(image_path)
    extracted_data = extract_purchase_data(image_path)
    # Ensure data is a list
    if not isinstance(extracted_data, list):
        return jsonify({'error': 'Failed to extract purchases', 'data': []})
    print(f"✅ Sending Response: {json.dumps(extracted_data, indent=2)}")
    return jsonify({'message': 'Image processed', 'data': extracted_data})

@app.route('/confirm_purchase', methods=['POST'])
@login_required
def confirm_purchase():
    """Receive confirmed purchases and log them into the database."""
    data = request.json
    purchases = data.get("purchases", [])
    for p in purchases:
        try:
            # Insert into Purchase table using a default category ("Unknown")
            new_purchase = Purchase(
                label=p["product"],
                price=float(p["price"].replace("£", "").strip()) if isinstance(p["price"], str) else float(p["price"]),
                category="Unknown",
                user_id=current_user.id,
                date=date.today()
            )
            db.session.add(new_purchase)
        except Exception as e:
            print(f"Error processing purchase: {p}, error: {e}")
    db.session.commit()
    return jsonify({'message': 'Purchases saved successfully'})

def extract_purchase_data(image_path):
    """Send image to Gemini and extract only product names and prices."""
    try:
        with open(image_path, "rb") as img_file:
            image_bytes = img_file.read()

        # Use a strict prompt to get only product and price info in JSON format
        prompt = (
            "Extract only the product names and their prices from the provided receipt image. "
            "Ignore all other details. Return a valid JSON array of objects in the following format: "
            '[{"product": "M&M\'s Choc Share", "price": "£2.85"}, {"product": "Buxton Water", "price": "£0.75"}]'
        )

        response = model.generate_content([
            prompt,
            {"mime_type": "image/png", "data": image_bytes}
        ])
        print(f"✅ Raw Gemini Response: {response.text}")
        if not response.text:
            return []
        start = response.text.find("[")
        end = response.text.rfind("]") + 1
        if start == -1 or end == -1:
            raise ValueError("Could not find valid JSON in the response.")
        json_text = response.text[start:end]
        extracted_data = json.loads(json_text)
        print(f"✅ Parsed Purchases: {extracted_data}")
        return extracted_data
    except Exception as e:
        print(f"❌ Error extracting data: {e}")
        return {"error": str(e)}

@app.route("/purchase", methods=["GET", "POST"])
@login_required
def purchase():
    if request.method == "POST":
        label = request.form.get("label")
        price = request.form.get("price")
        category = request.form.get("category")
        if not label or not price:
            return "Purchase name and price are required!"
        new_purchase = Purchase(label=label, price=float(price), category=category, user_id=current_user.id)
        db.session.add(new_purchase)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("purchase.html")

def process_image(image_path):
    """(Alternate function) Extract purchase details using Gemini."""
    image = Image.open(image_path)
    print(f"✅ Processing image with Gemini: {image_path}")
    gemini_prompt = (
        "Extract only the product names and their prices from the provided receipt image. "
        "Ignore all other details. Return a valid JSON array of objects in the following format: "
        '[{"product": "M&M\'s Choc Share", "price": "£2.85"}, {"product": "Buxton Water", "price": "£0.75"}]'
    )
    response = model.generate_content([gemini_prompt, image])
    print(f"✅ Gemini Response: {response.text}")
    if not response.text:
        return []
    start = response.text.find("[")
    end = response.text.rfind("]") + 1
    if start == -1 or end == -1:
        return []
    json_text = response.text[start:end]
    extracted_data = json.loads(json_text)
    print(f"✅ Final Extracted Purchases: {extracted_data}")
    return extracted_data

if __name__ == "__main__":
    app.run(port=80, debug=True)
