# Personal Photo Gallery — Term Project

**Course:** Software Engineering and Design (Spring 2026)  
**Team 6:** Lisa Freudewald & Luca Tim Witzig

---

## 📋 Project Overview

This project is a web-based **Personal Photo Gallery** built using Python and Flask. It uses a local SQLite database to save user accounts, photos, and messages. Users can sign up, log in, upload images with descriptions and keywords, search for photos, and chat with other users through a built-in messaging system.

---

## 🚀 How to Run the Project

Follow these steps to set up and run the application on your computer after extracting the project ZIP file.

### Prerequisites

Make sure you have **Python 3.x** installed on your computer.

### Step 1: Open Terminal in Project Directory

Extract the ZIP archive and open your terminal or command prompt inside the project root folder (`photo-gallery/`):

### Step 2: Install Dependencies

This project runs on a clean Flask setup without any heavy external frameworks. You only need to install core Flask:

```bash
pip install flask
```

### Step 3: Launch the Application

Start the backend application by running the main script:

```bash
python app.py
```

### Step 4: Access via Web Browser

Once the server is running, open your web browser and go to:
**[http://127.0.0.1:5000/](http://127.0.0.1:5000/)**

---

## 🌱 Automated Database Seeding & Testing Accounts

When you start the application for the first time, it automatically creates the database file (`database.db`) and inserts two test users.

You can log in right away using either of these pre-configured profiles:

- **Account 1:** Username: `Test1` | Password: `123`
- **Account 2:** Username: `Test2` | Password: `123`

---

## 🛠️ Main Features

- **User Accounts:** Visitors can browse the site as guests, but you must log in to see or upload photos. New users can register easily. If someone types a wrong password or tries to pick a username that is already taken, a warning message appears directly on the screen.
- **Photo Feed & Uploads:** Logged-in users can view a shared feed of all uploaded pictures. You can post your own photos along with a text description and tags/keywords. You can also change the description and keywords of your own posts later if you want to edit them.
- **Member Directory:** A sidebar panel on the homepage always shows a list of all registered users on the platform. This list is visible to both logged-in members and public guests.
- **Keyword Search:** Users can search for images using specific tags or keywords. The search bar automatically filters the feed and displays all matching photos on a results page.
- **Direct Messaging:** Every post uploaded by another user has a "Send DM" button. Clicking it lets you send a private message to that user. Users also have a personal inbox where they can read incoming messages, reply to them directly, or permanently delete them.
