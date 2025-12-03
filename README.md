# Stroke Prediction Management System

A secure Flask web application for managing patient stroke prediction data, built for Leeds Trinity University COM7033 module assessment.

## 📋 Project Overview

This application provides a secure platform for healthcare professionals to manage patient data related to stroke prediction. It implements comprehensive CRUD operations, robust security measures, and dual database architecture.

## ✨ Features

- **Secure User Authentication**
  - Password hashing using Werkzeug's security functions
  - Session management with Flask-Login
  - Protection against unauthorized access

- **Complete CRUD Operations**
  - Create: Add new patient records
  - Read: View patient lists and individual details
  - Update: Edit existing patient information
  - Delete: Remove patient records

- **Dual Database Architecture**
  - SQLite: User authentication and account management
  - MongoDB: Patient data storage and retrieval

- **Security Implementations**
  - Password hashing (bcrypt-based)
  - CSRF protection using Flask-WTF
  - Input validation and sanitization
  - SQL injection prevention through ORM
  - XSS protection through template escaping
  - Secure session handling
  - Authentication required for protected routes
  - Error logging for security monitoring

- **Search Functionality**
  - Search patients by ID, gender, work type, or smoking status
  - Quick filtering for efficient data access

- **Statistics Dashboard**
  - Overview of total patients
  - Stroke vs non-stroke patient counts
  - Percentage calculations

## 🗄️ Database Schema

### SQLite - Users Table
```sql
users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME
)
```

### MongoDB - Patients Collection
```json
{
    "id": Integer,
    "gender": String,
    "age": Float,
    "hypertension": Integer (0 or 1),
    "heart_disease": Integer (0 or 1),
    "ever_married": String,
    "work_type": String,
    "Residence_type": String,
    "avg_glucose_level": Float,
    "bmi": String,
    "smoking_status": String,
    "stroke": Integer (0 or 1),
    "created_at": DateTime
}
```

## 🔒 Security Features

### 1. Password Security
- Passwords are hashed using Werkzeug's `generate_password_hash`
- Uses bcrypt algorithm with salt
- Plain text passwords are never stored

### 2. Input Validation
- All forms use WTForms validators
- Age: 0-120 years
- Glucose level: 0-500 mg/dL
- BMI: 0-100
- Username: Alphanumeric and underscores only
- Email: Valid email format required

### 3. CSRF Protection
- Flask-WTF provides CSRF tokens for all forms
- Prevents cross-site request forgery attacks

### 4. SQL Injection Prevention
- Uses SQLAlchemy ORM for all database queries
- Parameterized queries prevent SQL injection

### 5. XSS Protection
- Jinja2 template engine automatically escapes output
- User input is sanitized before display

### 6. Authentication & Authorization
- Flask-Login manages user sessions
- `@login_required` decorator protects routes
- Session cleared on logout

### 7. Error Handling
- Custom error pages (404, 500)
- Errors logged to file for security monitoring
- Sensitive information not exposed in error messages

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- MongoDB installed and running
- pip package manager

### Step 1: Clone the Repository
```bash
git clone https://github.com/MuhammadFaizButt/com7033-assignment

cd stroke_prediction_app
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Start MongoDB
```bash
# On Windows
net start MongoDB

# On macOS
brew services start mongodb-community

# On Linux
sudo systemctl start mongod
```

### Step 5: Add Dataset
Place the `healthcare-dataset-stroke-data.csv` file in the `data/` directory.

### Step 6: Run the Application
```bash
python run.py
```

The application will be available at: `http://localhost:5000`

## 📖 Usage Guide

### First Time Setup

1. **Register an Account**
   - Navigate to the home page
   - Click "Register"
   - Fill in username, email, and password
   - Submit the form

2. **Login**
   - Use your credentials to login
   - You'll be redirected to the dashboard

3. **Load Dataset**
   - On the dashboard, click "Load Dataset from CSV"
   - This will import all patient data from the CSV file into MongoDB

### Managing Patients

#### View Patients
- Click "Patients" in the navigation
- Browse through paginated patient list
- View 20 patients per page

#### Add New Patient
- Click "Add Patient" in navigation
- Fill in all required fields
- Submit the form
- Patient will be added to MongoDB

#### Edit Patient
- Go to patient list or detail page
- Click "Edit" button
- Modify fields as needed
- Submit to save changes

#### Delete Patient
- From patient list or detail page
- Click "Delete" button
- Confirm deletion
- Patient will be removed from database

#### Search Patients
- Click "Search" in navigation
- Enter search term (ID, gender, work type, smoking status)
- View filtered results

## 🧪 Testing

### Run All Tests
```bash
# From project root directory
python -m pytest tests/ -v
```

### Run Specific Test Files
```bash
# Authentication tests
python -m pytest tests/test_auth.py -v

# CRUD operation tests
python -m pytest tests/test_crud.py -v

# Security tests
python -m pytest tests/test_security.py -v
```

### Test Coverage
- **Authentication**: 6 tests
- **CRUD Operations**: 6 tests
- **Security Features**: 8 tests
- **Total**: 20 unit tests

## 📁 Project Structure

```
stroke_prediction_app/
├── app/
│   ├── __init__.py           # Flask application factory
│   ├── models.py             # SQLAlchemy User model
│   ├── database.py           # MongoDB connection and operations
│   ├── forms.py              # WTForms with validation
│   ├── static/
│   │   └── css/
│   │       └── style.css     # Application styling
│   └── templates/            # Jinja2 HTML templates
│       ├── base.html
│       ├── index.html
│       ├── login.html
│       ├── register.html
│       ├── dashboard.html
│       ├── patients.html
│       ├── patient_detail.html
│       ├── patient_form.html
│       ├── search.html
│       ├── 404.html
│       └── 500.html
├── tests/                    # Unit tests
│   ├── test_auth.py
│   ├── test_crud.py
│   └── test_security.py
├── data/                     # Dataset folder
│   └── healthcare-dataset-stroke-data.csv
├── config.py                 # Application configuration
├── requirements.txt          # Python dependencies
├── run.py                    # Application entry point
├── .gitignore               # Git ignore file
└── README.md                # This file
```

This application handles sensitive healthcare data and implements:
- **Data Privacy**: Secure storage and access controls
- **GDPR Awareness**: User authentication and authorization
- **Audit Trail**: Logging of data access and modifications
- **Secure Handling**: Encryption of passwords and secure sessions
- **Ethical Use**: Healthcare data used for legitimate medical purposes only

## 🐛 Known Issues & Limitations

- Dataset must be loaded manually via dashboard button
- No email verification for registration
- No password reset functionality
- MongoDB must be running locally
- No data backup mechanism implemented

## 📚 References

- Flask Documentation: https://flask.palletsprojects.com/
- Flask-Login: https://flask-login.readthedocs.io/
- Flask-WTF: https://flask-wtf.readthedocs.io/
- PyMongo Documentation: https://pymongo.readthedocs.io/
- SQLAlchemy: https://www.sqlalchemy.org/
- Stroke Prediction Dataset: https://www.kaggle.com/datasets/fedesoriano/stroke-prediction-dataset

