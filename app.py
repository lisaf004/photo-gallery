from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "secret"

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ---------------- DATABASE ----------------
def get_db():
    return sqlite3.connect("database.db")

def init_db():
    db = get_db()
    c = db.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS photos(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        filename TEXT,
        description TEXT,
        keywords TEXT
    )""")

    c.execute("""CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_id INTEGER,
        receiver_id INTEGER,
        content TEXT
    )""")

    db.commit()
    db.close()

init_db()

# ---------------- AUTH ----------------
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if not username or not password:
            return "Error"

        db = get_db()
        try:
            db.execute("INSERT INTO users(username,password) VALUES (?,?)",
                       (username, password))
            db.commit()
        except:
            return "Error"
        return redirect("/login")

    return render_template("signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=? AND password=?",
                          (username, password)).fetchone()

        if user:
            session["user_id"] = user[0]
            return redirect("/")
        return "Invalid"

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- HOME ----------------
@app.route("/")
def home():
    db = get_db()

    users = db.execute("SELECT id, username FROM users").fetchall()

    photos = []
    if "user_id" in session:
        photos = db.execute("""
            SELECT photos.*, users.username 
            FROM photos JOIN users ON photos.user_id = users.id
        """).fetchall()

    return render_template("home.html", users=users, photos=photos)


# ---------------- UPLOAD ----------------
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user_id" not in session:
        return "Login required"

    if request.method == "POST":
        file = request.files["file"]
        description = request.form["description"]
        keywords = request.form["keywords"]

        if not file:
            return "Error"

        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        db = get_db()
        db.execute("""
            INSERT INTO photos(user_id, filename, description, keywords)
            VALUES (?, ?, ?, ?)
        """, (session["user_id"], file.filename, description, keywords))
        db.commit()

        return redirect("/")

    return render_template("upload.html")


# ---------------- EDIT OWN POST ----------------
@app.route("/edit/<int:id>", methods=["POST"])
def edit(id):
    if "user_id" not in session:
        return "Error"

    description = request.form["description"]
    keywords = request.form["keywords"]

    db = get_db()

    photo = db.execute("SELECT user_id FROM photos WHERE id=?", (id,)).fetchone()

    if photo[0] != session["user_id"]:
        return "Error"

    db.execute("""
        UPDATE photos SET description=?, keywords=? WHERE id=?
    """, (description, keywords, id))
    db.commit()

    return redirect("/")


# ---------------- SEARCH ----------------
@app.route("/search")
def search():
    keyword = request.args.get("keyword")

    if not keyword:
        return "Error"

    db = get_db()
    photos = db.execute("""
        SELECT photos.*, users.username
        FROM photos JOIN users ON photos.user_id = users.id
        WHERE keywords LIKE ?
    """, ("%" + keyword + "%",)).fetchall()

    users = db.execute("SELECT id, username FROM users").fetchall()

    return render_template("home.html", users=users, photos=photos)


# ---------------- DIRECT MESSAGE ----------------
@app.route("/send/<int:receiver_id>", methods=["POST"])
def send(receiver_id):
    if "user_id" not in session:
        return "Error"

    content = request.form["content"]

    db = get_db()
    db.execute("""
        INSERT INTO messages(sender_id, receiver_id, content)
        VALUES (?, ?, ?)
    """, (session["user_id"], receiver_id, content))
    db.commit()

    return redirect("/")


# ---------------- INBOX ----------------
@app.route("/inbox")
def inbox():
    if "user_id" not in session:
        return "Error"

    db = get_db()
    messages = db.execute("""
        SELECT messages.*, users.username 
        FROM messages JOIN users ON messages.sender_id = users.id
        WHERE receiver_id=?
    """, (session["user_id"],)).fetchall()

    return render_template("inbox.html", messages=messages)


# ---------------- REPLY ----------------
@app.route("/reply/<int:id>", methods=["POST"])
def reply(id):
    if "user_id" not in session:
        return "Error"

    db = get_db()
    msg = db.execute("SELECT sender_id FROM messages WHERE id=?", (id,)).fetchone()

    content = request.form["content"]

    db.execute("""
        INSERT INTO messages(sender_id, receiver_id, content)
        VALUES (?, ?, ?)
    """, (session["user_id"], msg[0], content))
    db.commit()

    return redirect("/inbox")


# ---------------- DELETE ----------------
@app.route("/delete/<int:id>")
def delete(id):
    if "user_id" not in session:
        return "Error"

    db = get_db()
    db.execute("DELETE FROM messages WHERE id=?", (id,))
    db.commit()

    return redirect("/inbox")


if __name__ == "__main__":
    app.run(debug=True)