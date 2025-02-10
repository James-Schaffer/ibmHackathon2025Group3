from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = "3$Yh9K|@w2Z*bN-gfdtrstrdrcea666b53c"
DB_NAME = "database.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"

# Database initialization
db = SQLAlchemy()
db.init_app(app)

# User model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    tags = db.relationship('Tag', backref='user', lazy=True)
    purchases = db.relationship('Purchases', backref='user', lazy=True)

# Group model
class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    code = db.Column(db.String(150), unique=True, nullable=False)
    users = db.relationship('User', backref='group', lazy=True)

# Tag model
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    purchases_tags = db.relationship('PurchasesTags', backref='tag', lazy=True)

# Purchases model
class Purchases(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(150), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    purchases_tags = db.relationship('PurchasesTags', backref='purchase', lazy=True)

# PurchasesTags model
class PurchasesTags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'),nullable=False)

# Create database tables
with app.app_context():
    db.create_all()

# Login manager setup
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        print("test")
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for("login"))

            # redirect to show their budget
            return redirect(url_for(f"homepage"))
        else:
            return "Invalid username or password"
            # flash("Invalid username or password", "error")

            return render_template("login.html")
    
    return render_template("login.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Debugging: Print form data
        print(f"Received username: {username}, password: {password}")

        if not username or not password:
            flash("Username and password are required!", "error")
            return redirect(url_for("signup"))
        elif User.query.filter_by(username=username).first():
            # Flash a message if an account with the email already exists
            # flash("Sorry, an account with that username already exists. Please log in or use a different username to register.")
            # return redirect(url_for("signup"))
            return "Sorry, an account with that username already exists. Please log in or use a different username to register."
        else:
            hashed_password = generate_password_hash(password, method="pbkdf2:sha256")
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            # flash("Account created successfully! Please login.", "success")
            return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/homepage", methods=["GET", "POST"])
def homepage():
    return render_template("homepage.html")

@app.route("/loginredir", methods=["GET", "POST"])
def loginRedir():
    return render_template("loginRedir.html")

@app.route("/capture", methods=["GET", "POST"])
def capture():

    return render_template("capture.html")

@app.route("/dashboard")
# @login_required
def dashboard():
    return render_template("budget.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(port=8080, debug=True)
