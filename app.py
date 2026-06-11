from flask import Flask, render_template, request 
from flask import session, redirect, url_for
import os

app = Flask(__name__)

IMAGE_FOLDER = "static/images"

CATEGORIES = [
    "Mountains", "Beach", "Forest", "City",
    "Food", "Animals", "People", "Night"
]

@app.route("/")
def home():
    images = {}

    for category in CATEGORIES:
        path = os.path.join(IMAGE_FOLDER, category)
        if os.path.exists(path):
            images[category] = os.listdir(path)
        else:
            images[category] = []

    return render_template("home.html", images=images, categories=CATEGORIES)




# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        session["user"] = username
        return redirect(url_for("home"))
    
    return render_template("login.html")


# SIGN UP
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        session["user"] = username
        return redirect(url_for("home"))
    
    return render_template("signup.html")


UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

images = []  # einfache Speicherung (für Projekt ausreichend)

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        file = request.files["image"]
        description = request.form.get("description")
        keywords = request.form.get("keywords")

        if file:
            filepath = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(filepath)

            images.append({
                "url": "/" + filepath,
                "description": description,
                "keywords": keywords
            })

        return redirect("/")

    return render_template("upload.html")


messages = []

@app.route("/inbox", methods=["GET", "POST"])
def inbox():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        msg = request.form.get("message")
        if msg:
            messages.append(msg)

    return render_template("inbox.html", messages=messages)


if __name__ == "__main__":
    app.run(debug=True)

app.secret_key = "secretkey123"  # wichtig für Sessions

@app.route("/login")
def login():
    session["user"] = "testuser"
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

@app.route("/")
def home():
    if "user" not in session:
        return render_template("home.html", logged_in=False)
    else:
        return render_template("home.html", logged_in=True)
    
if __name__ == "__main__":
    app.run(debug=True)