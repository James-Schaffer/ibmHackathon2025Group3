from flask import Flask,render_template,request
from werkzeug.utils import secure_filename
import os
app = Flask(__name__)

@app.route("/",methods=["GET","POST"])
def Camera():
    if request.method == 'POST': 
        image = request.files['image']
        # print(image.filename)
        image.save(os.path.join("media/", secure_filename(image.filename)))

    return render_template("index.html")

app.run(host="0.0.0.0",port=80,debug=True)
