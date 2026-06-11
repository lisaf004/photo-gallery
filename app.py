from flask import Flask, render_template
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


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/upload")
def upload():
    return render_template("upload.html")


@app.route("/inbox")
def inbox():
    return render_template("inbox.html")


if __name__ == "__main__":
    app.run(debug=True)