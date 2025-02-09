from flask import Flask,render_template,request,jsonify
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()
DB_NAME = "database.db" 

app = Flask(__name__)
app.config["SECRET_KEY"] = "3$Yh9K|@w2Z*bN-gfdtrstrdrcea666b53c"
app.config["SQLALCHEMY_DATABASE_URI"]= f"sqlite:///{DB_NAME}"
db.init_app(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    # Many-to-One: Users -> Group
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    # One-to-Many: Users -> Tags
    tags = db.relationship('Tag', backref='user', lazy=True)
    # One-to-Many: Users -> Purchases
    purchases = db.relationship('Purchases', backref='user', lazy=True)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    code = db.Column(db.String(150), unique=True, nullable=False)
    # One-to-Many: Group -> Users
    users = db.relationship('User', backref='group', lazy=True)

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    # Many-to-One: Tags -> Users
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # One-to-Many: Tags -> PurchasesTags
    purchases_tags = db.relationship('PurchasesTags', backref='tag', lazy=True)

class Purchases(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(150), unique=True, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    # Many-to-One: Purchases -> Users
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # One-to-Many: Purchases -> PurchasesTags
    purchases_tags = db.relationship('PurchasesTags', backref='purchase', lazy=True)

class PurchasesTags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # Many-to-One: PurchasesTags -> Tags
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), nullable=False)
    # Many-to-One: PurchasesTags -> Purchases
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'), nullable=False)

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.query.get((int(id)))

@app.route("/",methods=["GET","POST"])
def index():
    return render_template("index.html")

@app.route("/capture",methods=["GET","POST"])
def Camera():
    if request.method == 'POST': 
        image = request.files['image']
        image.save(os.path.join("media/", secure_filename(image.filename)))

    return render_template("capture.html")

@app.route("/login",methods=["GET","POST"])
def login():
    if request.method == 'POST': 
        username=request.form.get("username")
        password= request.form.get("password")
        print(username,password)
    return render_template("login.html")

@app.route("/signup",methods=["GET","POST"])
def signup():
    if request.method == 'POST': 
        username=request.form.get("username")
        password= request.form.get("password")
        print(username,password)
    return render_template("signup.html")

app.run(host="0.0.0.0",port=8080,debug=True)
