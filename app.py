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
from google.api_core.exceptions import ResourceExhausted


app = Flask(__name__)
app.config["SECRET_KEY"] = "3$Yh9K|@w2Z*bN-gfdtrstrdrcea666b53c"
DB_NAME = "database.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
app.config["REMEMBER_COOKIE_DURATION"] = 86400  # Keep session for 1 day
app.config["SESSION_PERMANENT"] = True

db = SQLAlchemy()
db.init_app(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    budget=db.Column(db.Integer, nullable=True)
    purchases = db.relationship('Purchase', back_populates='user', lazy=True)

class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Numeric(10, 2),nullable=False)
    category = db.Column(db.String(150), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date)
    user = db.relationship('User', back_populates='purchases')

with app.app_context():
    db.create_all()


genai.configure(api_key="AIzaSyAMnCFsSFcXpOAfQzv05gLk4NuGjymRaLM")
model = genai.GenerativeModel("gemini-1.5-flash")

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
    

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(f"/home")
        
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

@app.route("/profile")
@login_required
def profile():
    purchases = Purchase.query.filter(Purchase.user_id == current_user.id).order_by(Purchase.id.desc()).limit(5).all()
    return render_template("profile.html", user=current_user, purchases=purchases)

@app.route("/expenses", methods=["GET", "POST"])
@login_required
def expenses():
    if request.method == "POST":
        if request.is_json:
            data = request.get_json()
            purchase_text = data.get("purchase", "")
            price = data.get("price")
            category = data.get("category", "")
        else:
            purchase_text = request.form.get("purchase", "")
            price = request.form.get("price")
            category = request.form.get("category", "")

        if not purchase_text or purchase_text.strip() == "":
            purchase_text = "Unknown"
        else:
            purchase_text = purchase_text.strip()

        try:
            price = float(price)
        except (TypeError, ValueError):
            flash("Invalid price", "error")
            return redirect(url_for("expenses"))

        if not category or category.strip() == "":
            response = model.generate_content(
                f"Classify the following purchase =>({purchase_text}) into one of the predefined spending categories: [Food & Drinks, Transportation, School Supplies, Rent & Utilities, Phone Bill, Entertainment, Clothing & Accessories, Personal Care, Fitness, Socializing, Tuition & Fees, Online Subscriptions, Emergency Fund & Savings,others]. Only return the category name. Do not include any extra text and no spaces between words"
            )
            category = response.text.replace("\n", "").strip()
        else:
            category = category.strip()

        purchase_date = datetime.date.today()

        new_purchase = Purchase(
            label=purchase_text,
            price=price,
            category=category,
            user_id=current_user.id,
            date=purchase_date
        )
        db.session.add(new_purchase)
        db.session.commit()

        if request.is_json:
            return jsonify({"message": "Purchase added successfully"}), 200
        else:
            return redirect(url_for("expenses"))

    purchases = Purchase.query.filter(Purchase.user_id == current_user.id).order_by(Purchase.id.desc()).all()
    return render_template("expenses.html", purchases=purchases)

@app.route('/leaderboard')
@login_required

def leaderboard():
    users = User.query.all()
    leaderboard_data = []
    
    for user in users:
        total_spent = sum(p.price for p in user.purchases)
        savings = user.budget - total_spent if user.budget else 0
        savings_percentage = (savings / user.budget * 100) if user.budget else 0
        
        savings_percentage = round(savings_percentage, 2)
        
        leaderboard_data.append({
            'username': user.username,
            'savings_percentage': savings_percentage
        })
    
    leaderboard_data = sorted(leaderboard_data, key=lambda x: x['savings_percentage'], reverse=True)

    rank = 1
    for i, user in enumerate(leaderboard_data):
        if i > 0 and user['savings_percentage'] == leaderboard_data[i - 1]['savings_percentage']:
            user['rank'] = leaderboard_data[i - 1]['rank']  
        else:
            user['rank'] = rank  
        rank += 1

    return render_template('leaderboard.html', leaderboard_data=leaderboard_data)


@app.route("/home", methods=["GET", "POST"])
@login_required
def home():
    global budget
    if request.method == "POST": 
        budget = request.get_json()

        if 'budget' not in budget or not isinstance(budget['budget'], int):
            return jsonify({'error': 'Invalid budget value'}), 400
        
        current_user.budget = budget['budget']
        db.session.commit()

        print(budget["budget"])
        return jsonify({'message': 'Budget updated successfully', 'budget': budget['budget']}), 200

    expenses=0
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
        category_name = category[0]  
        purchases = Purchase.query.filter_by(user_id=current_user.id, category=category_name).order_by(Purchase.price.asc()).all()

        purchases_by_category[category_name] = purchases

    return render_template("savings.html",purchases_by_category=purchases_by_category)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/capture", methods=["GET", "POST"])
@login_required
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
        response = model.generate_content([
            "Classify the following purchase =>({label}) into one of the predefined spending categories: [Food & Drinks, Transportation, School Supplies, Rent & Utilities, Phone Bill, Entertainment, Clothing & Accessories, Personal Care, Fitness, Socializing, Tuition & Fees, Online Subscriptions, Emergency Fund & Savings,others]. Only return the category name.Output the purchase data in the format: name,price,category,name,price,category. Only include the purchase name and its corresponding price, no additional information.also remove all the currency symbol from it",
            image
        ])
        data = str(response.text).split(',')
        two_d_list = []

        for i in range(0, len(data), 3):
            
            product = data[i].strip() if data[i] else ""
            if not product:
                product = "Unknown"  

            price = float(data[i + 1].replace('£', '').strip())
            
            category = data[i + 2]
            category = re.sub("\n", "", category)
            category = re.sub(" ", "", category)
            
            purchase = Purchase(
                label=product,
                price=price,
                category=category,
                user_id=current_user.id,
                date=datetime.datetime.now().date()  
            )
            
            db.session.add(purchase)
            db.session.commit()


        return jsonify({"message": "Image uploaded successfully", "image_url": f"/uploads/{image.filename}"})
        
    except ResourceExhausted as e:
        print("ResourceExhausted error:", e)
        return redirect(request.url) 
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

 



@app.route("/budget")
@login_required
def budget():
    return render_template("budget.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=80, debug=True)
