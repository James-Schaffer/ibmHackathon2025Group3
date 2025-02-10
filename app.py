from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
import google.generativeai as genai
from PIL import Image

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = "3$Yh9K|@w2Z*bN-gfdtrstrdrcea666b53c"
DB_NAME = "database.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
app.config["REMEMBER_COOKIE_DURATION"] = 86400  # Keep session for 1 day
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
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    tags = db.relationship('Tag', backref='user', lazy=True)
    purchases = db.relationship('Purchases', backref='user', lazy=True)

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

# Purchases model
class Purchases(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(150), unique=False, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(150), unique=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    purchases_tags = db.relationship('PurchasesTags', backref='purchase', lazy=True)

# # PurchasesTags model
# class PurchasesTags(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)
#     purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'), nullable=False)

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

# Routes
@app.route("/", methods=["GET", "POST"])
def welcome():
    return render_template("welcome.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # print(username,password)
        # if not username or not password:
        #     flash("Username and password are required!", "error")
        #     return redirect(url_for("login"))

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            # flash("Login successful!", "success")
            return redirect("/home")
        
            # flash("Invalid username or password", "error")
        return "Invalid username or password : From Server"
            # return redirect(url_for("login"))

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
            # flash("Username already exists. Please log in or choose a different username.", "error")
            # return redirect(url_for("signup"))

        hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully! Please login.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

@app.route("/home")
@login_required
def home():
    return render_template("home.html")

@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html")

@app.route("/expenses" ,methods=["GET", "POST"])
@login_required
def expenses():
    if request.method == "POST":
        label = request.form.get("label")
        price = request.form.get("price")
        response = model.generate_content(f"Classify the following purchase =>({label}) into one of the predefined spending categories: [Food & Drinks, Transportation, School Supplies, Rent & Utilities, Phone Bill, Entertainment, Clothing & Accessories, Personal Care, Fitness, Socializing, Tuition & Fees, Online Subscriptions, Emergency Fund & Savings]. Only return the category name. Do not include any extra text.")
        print(response.text)
        print(label,price)
        purchase= Purchases(label=label, price=price,category=response.text)
        db.session.add(purchase)
        db.session.commit()

        pass
    return render_template("expenses.html")

@app.route("/friends")
@login_required
def leaderboard():
    return render_template("friends.html")

@app.route("/savings")
@login_required
def savings():
    return render_template("savings.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/capture", methods=["GET", "POST"])
def capture():
    if request.method == "GET":
        return render_template("capture.html")

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400  
    
    image = request.files["image"]
    
    if image.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    if not image.filename.lower().endswith(("png", "jpg", "jpeg")):
        return jsonify({"error": "Invalid file type"}), 400
    
    try:
        image_path = os.path.join("media", image.filename)
        image.save(image_path)
        image = Image.open(image_path)
        response = model.generate_content(["From this image, analyse the names of the products listed and the price of each product and output in this format json format, no other response ", image])
        print(response.text)
        return jsonify({"message": "Image uploaded successfully", "image_url": f"/uploads/{image.filename}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500  

# @app.route("/uploads/<filename>")
# def uploaded_file(filename):
#     return send_from_directory("uploads", filename)

@app.route("/budget")
@login_required
def budget():
    return render_template("budget.html")

if __name__ == "__main__":
    app.run(port=8080, debug=True)
