"""
Setup script for initializing the application databases
Run this script before first use to set up the SQLite database
"""

from app import create_app
from app.models import db

def setup_database():
    """Initialize the SQLite database"""
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ SQLite database tables created successfully!")
        print("✅ Ready to start the application!")
        print("\nNext steps:")
        print("1. Make sure MongoDB is running")
        print("2. Run 'python run.py' to start the application")
        print("3. Navigate to http://localhost:5000")
        print("4. Register a new account")
        print("5. Load the dataset from the dashboard")

if __name__ == '__main__':
    setup_database()
