from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin
import os
import time

# Initialize Flask app
app = Flask(__name__)
app.config["SECRET_KEY"] = "3$Yh9K|@w2Z*bN-gfdtrstrdrcea666b53c"
DB_NAME = "database.db"
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"

# Database initialization
db = SQLAlchemy()
db.init_app(app)

# Uploads folder setup
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
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
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchases.id'), nullable=False)

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

# Utility function for allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/capture", methods=["GET", "POST"])
def capture():
    if request.method == "GET":
        return render_template("capture.html")  # Ensure you have a "capture.html" template

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400  
    
    image = request.files["image"]
    
    if image.filename == "":
        return jsonify({"error": "No selected file"}), 400
    
    if not allowed_file(image.filename):
        return jsonify({"error": "Invalid file type"}), 400
    
    try:
        ext = image.filename.rsplit(".", 1)[1].lower()
        filename = f"captured_{int(time.time())}.{ext}"

        # Remove old images
        for file in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Save the new image
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(image_path)

        return jsonify({"message": "Image uploaded successfully", "image_url": f"/uploads/{filename}"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500  
  

@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80, debug=True)
