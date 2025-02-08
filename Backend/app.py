from flask import Flask,render_template,request

app = Flask(__name__)

@app.route("/")
def Camera():
    if request.method == 'POST': 
        print(1)

    return render_template("index.html")

app.run(host="0.0.0.0",port=8080,debug=True)
