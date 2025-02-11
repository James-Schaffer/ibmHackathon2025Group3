from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
import google.generativeai as genai
from PIL import Image
import json
import re
import datetime



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

# spending_categories = [
#     "Food & Drinks",
#     "Transportation",
#     "School Supplies",
#     "Rent & Utilities",
#     "Phone Bill",
#     "Entertainment",
#     "Clothing & Accessories",
#     "Personal Care",
#     "Fitness",
#     "Socializing",
#     "Tuition & Fees",
#     "Online Subscriptions",
#     "Emergency Fund & Savings",
#     "other"
# ]

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    budget=db.Column(db.Integer, nullable=True)
    # One-to-Many relationship
    purchases = db.relationship('Purchase', back_populates='user', lazy=True)

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
class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Numeric(10, 2),nullable=False)
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
            return redirect(f"/home")
        
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

@app.route("/update_budget",methods=["POST","GET"])
# @login_required
def update_budget():
   
    return redirect(url_for("login"))
    


@app.route("/profile")
@login_required
def profile():
    # this is cool
    purchases = Purchase.query.filter(Purchase.user_id == current_user.id).order_by(Purchase.id.desc()).limit(5).all()
    return render_template("profile.html", user=current_user, purchases=purchases)

@app.route("/expenses" ,methods=["GET", "POST"])
@login_required
def expenses():
    if request.method == "POST":
        label = request.form.get("label")
        price = request.form.get("price")
        response = model.generate_content(f"Classify the following purchase =>({label}) into one of the predefined spending categories: [Food & Drinks, Transportation, School Supplies, Rent & Utilities, Phone Bill, Entertainment, Clothing & Accessories, Personal Care, Fitness, Socializing, Tuition & Fees, Online Subscriptions, Emergency Fund & Savings,others]. Only return the category name. Do not include any extra text. ")
        print(response.text)
        print(label,price)
        purchase= Purchase(label=label, price=price,category=response.text.replace("\n",""),user_id=current_user.id,date = datetime.datetime.now().date())
        db.session.add(purchase)
        db.session.commit()

    # purchases = Purchase.query.filter(Purchase.user_id == current_user.id).all()
    purchases = Purchase.query.filter(Purchase.user_id == current_user.id).order_by(Purchase.id.desc()).all()
    # print(item)

    return render_template("expenses.html",purchases=purchases)

# @app.route("/leaderboard")
# @login_required
# def leaderboard():

#     return render_template("leaderboard.html")

@app.route('/leaderboard')
def leaderboard():
    users = User.query.all()
    leaderboard_data = []
    
    for user in users:
        total_spent = sum(p.price for p in user.purchases)
        savings = user.budget - total_spent if user.budget else 0
        savings_percentage = (savings / user.budget * 100) if user.budget else 0
        
        # Round the savings percentage to 2 decimal places
        savings_percentage = round(savings_percentage, 2)
        
        leaderboard_data.append({
            'username': user.username,
            'savings_percentage': savings_percentage
        })
    
    leaderboard_data = sorted(leaderboard_data, key=lambda x: x['savings_percentage'], reverse=True)
    
    return render_template('leaderboard.html', leaderboard_data=leaderboard_data)

@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    global budget
    if request.method == "POST":  # Method should be in uppercase "POST"
        budget = request.get_json()

        if 'budget' not in budget or not isinstance(budget['budget'], int):
            return jsonify({'error': 'Invalid budget value'}), 400
        
        current_user.budget = budget['budget']
        db.session.commit()

        print(budget["budget"])
        return jsonify({'message': 'Budget updated successfully', 'budget': budget['budget']}), 200

    expenses=0
    # purchases = Purchase.query.filter(Purchase.user_id == current_user.id).all()
    purchases = Purchase.query.filter(Purchase.user_id == current_user.id).order_by(Purchase.id.desc()).all()
    if purchases:
        expenses += sum(purchase.price for purchase in purchases)
    else:
        expenses=0
    if current_user.budget!=None:
        savings = current_user.budget-expenses
    else:
        savings=0

    return render_template("home.html", purchases=purchases,budget=current_user.budget,user=current_user.username,expenses=expenses,savings=savings)

@app.route("/savings")
@login_required
def savings():
    purchases_by_category = {}

    categories = db.session.query(Purchase.category).distinct()
    
    for category in categories:
        category_name = category[0]  # Extract category name from query result
        # purchases = Purchase.query.filter_by(category=category_name).order_by(Purchase.price.asc()).all()
        purchases = Purchase.query.filter_by(user_id=current_user.id, category=category_name).order_by(Purchase.price.asc()).all()

        purchases_by_category[category_name] = purchases

    # print(purchases_by_category)/
    return render_template("savings.html",purchases_by_category=purchases_by_category)

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
        response = model.generate_content(["Classify the following purchase =>({label}) into one of the predefined spending categories: [Food & Drinks, Transportation, School Supplies, Rent & Utilities, Phone Bill, Entertainment, Clothing & Accessories, Personal Care, Fitness, Socializing, Tuition & Fees, Online Subscriptions, Emergency Fund & Savings,others]. Only return the category name.Output the purchase data in the format: name,price,category,name,price,category. Only include the purchase name and its corresponding price, no additional information.also remove all the currency symbol from it", image])
        # print(response.text)
        data = str(response.text).split(',')
        # print(data)
        two_d_list = []

# Loop through the data in steps of 3 (product, price, category)
        for i in range(0, len(data), 3):
            product = data[i]  # Product name
            price = float(data[i + 1].replace('£', '').strip())  # Convert price to float after removing '£'
            category = data[i + 2]
            category = re.sub("\n","",category)  # Category
            category = re.sub(" ","",category)  # Category
    
            # Create a new Purchase object
            purchase = Purchase(label=product, price=price, category=category, user_id=current_user.id,date = datetime.datetime.now().date())
            
            # Add the purchase to the session and commit
            db.session.add(purchase)
            db.session.commit()
            

        return jsonify({"message": "Image uploaded successfully", "image_url": f"/uploads/{image.filename}"})
        
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500  



@app.route("/budget")
@login_required
def budget():
    return render_template("budget.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=8080, debug=True)
