# 📝 GCBoard - Community Bulletin Board Backend

This project is a backend application for a community bulletin board built with Flask. It provides features such as user registration, login, email verification, and post creation.

## 📁 Project Structure
gcboard/

├── backend/

│ ├── app.py

│ ├── config.py

│ ├── models/

│ ├── routes/

│ └── ...

└── frontend/


## 🚀 Getting Started

1. Set up a virtual environment and install dependencies:
```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
```
2. Create the .env file:
To run this project, you must create a .env file inside the gcboard/backend/ directory. The .env file should follow the format below:
```
# ✅ Basic Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_ENV=development
FLASK_DEBUG=True

# ✅ Database Configuration (default: SQLite)
DATABASE_URL=sqlite:///community.db
# For other DBMS (example):
# DATABASE_URL=postgresql://username:password@localhost/dbname

# ✅ Email Server Settings (Gmail example)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USE_SSL=False
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_DEFAULT_SENDER=your_email@gmail.com

# ✅ JWT Token Authentication
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ACCESS_TOKEN_EXPIRES=7200

# ✅ Admin Email List (comma-separated)
ADMIN_EMAILS=admin@example.com

# ✅ "Remember Me" Cookie Duration (7 days)
REMEMBER_COOKIE_DURATION=604800

# ✅ CORS Configuration (allowed origins for API access)
CORS_ORIGINS=*

# ✅ Email Verification URL Template
EMAIL_VERIFICATION_URL=http://127.0.0.1:5000/verify-email/{}

# ✅ System Notification Sender Email
NOTIFICATION_EMAIL=no-reply@yourdomain.com

# ✅ Default Pagination Size
DEFAULT_PAGE_SIZE=20
```
3. start server
```
flask run
```
