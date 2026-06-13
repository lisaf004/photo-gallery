from flask import Flask, render_template, request 
from flask import session, redirect, url_for
from flask import Flask, request, redirect, flash
import os
import sqlite3

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}
app = Flask(__name__)
app.secret_key = "secretkey123"  # Required for secure session handling

DATABASE = "database.db"
UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  # Allows accessing columns by name like a dictionary
    return conn

def init_db():
    """Creates tables if they do not exist and seeds initial test users."""
    conn = get_db_connection()
    
    # 1. Create Users Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    
    # 2. Create Photos Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS photos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            filename TEXT,
            description TEXT,
            keywords TEXT
        )
    """)
    
    # 3. Create Messages Table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER,
            receiver_id INTEGER,
            content TEXT
        )
    """)
    
    # 🌱 SEEDING: Insert default users if they don't exist yet (Showcases FR2 & FR3 instantly!)
    conn.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'Test1', '123')")
    conn.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (2, 'Test2', '123')")
    
    conn.commit()
    conn.close()

# --- FUNCTIONALITY 2 & 3: HOME FEED & USER LIST ---
@app.route("/")
def home():
    conn = get_db_connection()
    
    # FR2 & FR3: Everyone (including guests) can see the registered members list
    users_list = conn.execute("SELECT id, username FROM users").fetchall()
    
    logged_in = "user" in session
    db_photos = []

    if logged_in:
        # FR2: Signed-in users see all photos from all users
        db_photos = conn.execute("""
            SELECT photos.*, users.username 
            FROM photos 
            JOIN users ON photos.user_id = users.id
            ORDER BY photos.id DESC
        """).fetchall()
        
    conn.close()
    return render_template("home.html", logged_in=logged_in, users_list=users_list, db_photos=db_photos)


# --- FUNCTIONALITY 1: SIGN IN ---
@app.route("/signin", methods=["GET", "POST"])
def signin():
    error = None  # Level 1 Indentation (4 spaces)
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password") or ""

        conn = get_db_connection()
        user_row = conn.execute(
            "SELECT * FROM users WHERE username = ? AND password = ?", 
            (username, password)
        ).fetchone()
        conn.close()

        if user_row:
            session["user"] = user_row["username"]
            session["user_id"] = user_row["id"]
            return redirect(url_for("home"))
        else:
            error = "Invalid username or password!"

    return render_template("signin.html", error=error)

# --- FUNCTIONALITY 1: SIGN UP ---
@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None 
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password") or ""

        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)", 
                (username, password)
            )
            conn.commit()
            
            user_row = conn.execute("SELECT id FROM users WHERE username = ?", (username,)).fetchone()
            session["user"] = username
            session["user_id"] = user_row["id"]
            conn.close()
            return redirect(url_for("home"))
        except sqlite3.IntegrityError:
            conn.close()
            error = "Username already exists!"

    return render_template("signup.html", error=error)

# --- FUNCTIONALITY 1: SIGN OUT ---
@app.route("/logout")
def logout():
    session.clear()  # Clear all session tokens
    return redirect(url_for("home"))


# --- FUNCTIONALITY 4: UPLOAD PHOTO ---
@app.route("/upload", methods=["GET", "POST"])
def upload():
    if "user" not in session:
        return redirect("/signin")

    if request.method == "POST":
        file = request.files.get("image")
        description = request.form.get("description")
        keywords = request.form.get("keywords")

        # 🔥 NEU: Datei prüfen
        if not file or file.filename == "":
            flash("No file selected")
            return redirect("/upload")

        if not allowed_file(file.filename):
            flash("Invalid file type!")
            return redirect("/upload")

        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)

        # Store the photo metadata inside the database
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO photos (user_id, filename, description, keywords) 
            VALUES (?, ?, ?, ?)
        """, (session["user_id"], file.filename, description, keywords))
        conn.commit()
        conn.close()

        return redirect(url_for("home"))

    return render_template("upload.html")


# --- FUNCTIONALITY 6: INBOX (DIRECT MESSAGES) ---
@app.route("/inbox", methods=["GET", "POST"])
def inbox():
    if "user" not in session:
        return redirect("/signin")

    conn = get_db_connection()
    receiver_name = request.args.get("receiver", "")

    if request.method == "POST":
        content = request.form.get("message")
        target_receiver = request.form.get("receiver")

        # Find the user ID that belongs to the typed recipient name
        receiver = conn.execute("SELECT id FROM users WHERE username = ?", (target_receiver,)).fetchone()
        
        if receiver and content:
            conn.execute("""
                INSERT INTO messages (sender_id, receiver_id, content) 
                VALUES (?, ?, ?)
            """, (session["user_id"], receiver["id"], content))
            conn.commit()
            return redirect(url_for("inbox"))
        else:
            conn.close()
            return "Recipient does not exist or message content is empty!"

    # Fetch only messages addressed to the currently authenticated user
    my_messages = conn.execute("""
        SELECT messages.*, users.username AS sender_name 
        FROM messages 
        JOIN users ON messages.sender_id = users.id 
        WHERE messages.receiver_id = ?
        ORDER BY messages.id DESC
    """, (session["user_id"],)).fetchall()
    
    conn.close()
    return render_template("inbox.html", messages=my_messages, receiver_name=receiver_name)


# --- FUNCTIONALITY 5: KEYWORD SEARCH ---
@app.route("/search")
def search():
    keyword = request.args.get("q", "").strip()  # Fetch input token from navbar search bar
    conn = get_db_connection()
    
    # Query matching keywords via SQL LIKE operation (FR5.A)
    results = conn.execute("""
        SELECT photos.*, users.username 
        FROM photos 
        JOIN users ON photos.user_id = users.id
        WHERE photos.keywords LIKE ?
        ORDER BY photos.id DESC
    """, (f"%{keyword}%",)).fetchall()
    
    conn.close()
    return render_template("search_results.html", results=results, keyword=keyword)


# --- FUNCTIONALITY 4.B: MODIFY OWN POST INFORMATION ---
@app.route("/edit/<int:photo_id>", methods=["GET", "POST"])
def edit_photo(photo_id):
    if "user" not in session:
        return redirect("/signin")
    
    conn = get_db_connection()
    photo = conn.execute("SELECT * FROM photos WHERE id = ?", (photo_id,)).fetchone()
    
    if not photo:
        conn.close()
        return "Photo not found!", 404
        
    # Security checkpoint: Does this post belong to the currently logged-in user?
    if photo["user_id"] != session["user_id"]:
        conn.close()
        return "Access denied! You cannot modify other users' posts.", 403

    if request.method == "POST":
        description = request.form.get("description")
        keywords = request.form.get("keywords")
        
        conn.execute("""
            UPDATE photos 
            SET description = ?, keywords = ? 
            WHERE id = ?
        """, (description, keywords, photo_id))
        conn.commit()
        conn.close()
        return redirect(url_for("home"))
        
    conn.close()
    return render_template("edit.html", photo=photo)


# --- FUNCTIONALITY 6.E: DELETE DIRECT MESSAGE ---
@app.route("/delete-message/<int:message_id>", methods=["POST"])
def delete_message(message_id):
    if "user" not in session:
        return redirect("/signin")
        
    conn = get_db_connection()
    # Confirm that only the designated recipient can drop the message
    msg = conn.execute("SELECT receiver_id FROM messages WHERE id = ?", (message_id,)).fetchone()
    
    if msg and msg["receiver_id"] == session["user_id"]:
        conn.execute("DELETE FROM messages WHERE id = ?", (message_id,))
        conn.commit()
        
    conn.close()
    return redirect(url_for("inbox"))

if __name__ == "__main__":
    init_db()  # <-- Das sorgt dafür, dass die Test-User sofort generiert werden!
    app.run(debug=True)