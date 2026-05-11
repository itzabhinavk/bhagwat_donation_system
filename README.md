# 🙏 Bhagwat Donation Management System

A full-stack web application to publicly track and manage donations during a Bhagwat event.  
Built with **Python Flask** + **MySQL** + **Vanilla JS** — no frameworks needed!

---

## ✨ Features

**Public (No Login)**
- View all donations in a sortable, searchable table
- See total donation amount in real-time
- Paginated results for fast loading on mobile
- View notices/announcements

**Admin Panel**
- Secure login with single-session enforcement
- Add, Edit, Delete donations
- Add, Edit, Delete notices
- Dashboard with stats

---

## 🚀 Quick Setup (Local)

### 1. Clone / Download the project

```bash
cd bhagwat_app
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows:
venv\Scripts\activate

# Mac/Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up the database

Make sure MySQL is running. Then:

```bash
mysql -u root -p < database/schema.sql
```

### 5. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your MySQL credentials:

```
SECRET_KEY=change-this-to-something-long-and-random
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=bhagwat_db
DB_PORT=3306
```

### 6. Create the admin account

```bash
python seed_admin.py
```

Follow the prompts to set username and password.

### 7. Run the app!

```bash
python app.py
```

Visit: `http://localhost:5000`  
Admin panel: `http://localhost:5000/admin/login`

---

## ☁️ Deploy to Render + Railway MySQL

### Step 1: Set up Railway MySQL

1. Go to [railway.app](https://railway.app)
2. New Project → Add MySQL
3. Copy the connection details (Host, User, Password, Database, Port)
4. Run `schema.sql` on Railway using their MySQL console or a tool like TablePlus

### Step 2: Deploy to Render

1. Push this project to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Add Environment Variables from your `.env` file
6. Deploy!

### Step 3: Run seed_admin on production

Use Render's shell to run:
```bash
python seed_admin.py
```

---

## 📁 Project Structure

```
bhagwat_app/
│
├── app.py              # Main Flask app entry point
├── config.py           # Configuration (loads from .env)
├── requirements.txt    # Python dependencies
├── Procfile            # For Render deployment
├── seed_admin.py       # Script to create admin account
├── .env.example        # Environment variable template
│
├── database/
│   ├── db.py           # MySQL connection utility
│   └── schema.sql      # Database table definitions
│
├── routes/
│   ├── public.py       # Public page routes
│   └── admin.py        # Admin panel routes
│
├── utils/
│   └── helpers.py      # Auth decorator, session utils
│
├── static/
│   ├── css/style.css   # Main stylesheet
│   ├── js/main.js      # Public page JavaScript
│   └── js/admin.js     # Admin panel JavaScript
│
└── templates/
    ├── base.html        # Base template (public pages)
    ├── index.html       # Homepage with donation table
    ├── notices.html     # All notices page
    ├── error.html       # Error page
    └── admin/
        ├── login.html   # Admin login page
        └── dashboard.html # Admin dashboard
```

---

## 🔒 Security Features

- Passwords hashed with **Werkzeug** (bcrypt-style)
- **Single session enforcement**: logging in from a new device invalidates the previous session
- Session stored server-side
- SQL queries use **parameterized statements** (no SQL injection)
- Admin routes protected by `@login_required` decorator

---

## 📱 Mobile Friendly

The entire UI is responsive — village volunteers can open it on any phone browser without installing anything.

---

## 🛠️ Troubleshooting

**MySQL Connection Error**: Check your `.env` values, make sure MySQL is running.

**"Table doesn't exist"**: Run `schema.sql` first.

**Can't login**: Run `seed_admin.py` to create/reset admin password.

**Render deployment fails**: Make sure all env variables are set in Render dashboard.
