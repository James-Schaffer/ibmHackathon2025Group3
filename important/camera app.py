import os
import time
from flask import Flask, request, render_template, jsonify, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET", "POST"])
def Camera():
    if request.method == "POST":
        if "image" not in request.files:
            return jsonify({"error": "No image uploaded"}), 400
        
        image = request.files["image"]

        if image.filename == "":
            return jsonify({"error": "No selected file"}), 400
        
        if not allowed_file(image.filename):
            return jsonify({"error": "Invalid file type"}), 400

        # Generate unique filename (prevents caching issues)
        ext = image.filename.rsplit(".", 1)[1].lower()
        filename = f"captured_{int(time.time())}.{ext}"  # Example: captured_1700000000.png

        # Remove old images before saving new one
        for file in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

        # Save the new image
        image_path = os.path.join(UPLOAD_FOLDER, filename)
        image.save(image_path)

        return jsonify({"message": "Image uploaded successfully", "image_url": f"/uploads/{filename}"})

    return render_template("index.html")

# Route to serve uploaded images
@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == "__main__":
    app.run(debug=True, port=80)
