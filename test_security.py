import unittest
from app import create_app
from app.models import db, User
from config import Config

class TestConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    MONGO_DBNAME = 'test_stroke_prediction_db'

class SecurityTestCase(unittest.TestCase):
    """Test cases for security features"""
    
    def setUp(self):
        """Set up test client and database"""
        self.app = create_app()
        self.app.config.from_object(TestConfig)
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Clean up after tests"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_password_hashing_security(self):
        """Test that passwords are securely hashed"""
        with self.app.app_context():
            user = User(username='testuser', email='test@example.com')
            password = 'SecurePassword123!'
            user.set_password(password)
            
            # Password should not be stored in plain text
            self.assertNotEqual(user.password_hash, password)
            
            # Hash should be long enough (bcrypt produces 60 character hashes)
            self.assertGreater(len(user.password_hash), 50)
            
            # Should verify correct password
            self.assertTrue(user.check_password(password))
            
            # Should reject incorrect password
            self.assertFalse(user.check_password('WrongPassword'))
    
    def test_authentication_required(self):
        """Test that authentication is required for protected routes"""
        protected_routes = [
            '/dashboard',
            '/patients',
            '/patient/add',
            '/search'
        ]
        
        for route in protected_routes:
            response = self.client.get(route)
            # Should redirect to login
            self.assertEqual(response.status_code, 302)
            self.assertIn(b'/login', response.data)
    
    def test_sql_injection_prevention(self):
        """Test SQL injection prevention in login"""
        # Attempt SQL injection in username field
        response = self.client.post('/login', data={
            'username': "admin' OR '1'='1",
            'password': 'anything'
        })
        
        # Should not bypass authentication
        self.assertNotIn(b'Dashboard', response.data)
        self.assertIn(b'Invalid username or password', response.data)
    
    def test_input_validation_age(self):
        """Test input validation for age field"""
        # Create and login user
        with self.app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
        
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Try to add patient with invalid age
        response = self.client.post('/patient/add', data={
            'gender': 'Male',
            'age': 150,  # Invalid: too old
            'hypertension': '0',
            'heart_disease': '0',
            'ever_married': 'Yes',
            'work_type': 'Private',
            'Residence_type': 'Urban',
            'avg_glucose_level': 100,
            'bmi': '25',
            'smoking_status': 'never smoked',
            'stroke': '0'
        })
        
        self.assertIn(b'Age must be between 0 and 120', response.data)
    
    def test_input_validation_glucose(self):
        """Test input validation for glucose level"""
        # Create and login user
        with self.app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
        
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Try to add patient with invalid glucose level
        response = self.client.post('/patient/add', data={
            'gender': 'Female',
            'age': 50,
            'hypertension': '0',
            'heart_disease': '0',
            'ever_married': 'Yes',
            'work_type': 'Private',
            'Residence_type': 'Urban',
            'avg_glucose_level': 600,  # Invalid: too high
            'bmi': '25',
            'smoking_status': 'never smoked',
            'stroke': '0'
        })
        
        self.assertIn(b'Glucose level must be between 0 and 500', response.data)
    
    def test_username_validation(self):
        """Test username validation (alphanumeric only)"""
        # Try to register with special characters in username
        response = self.client.post('/register', data={
            'username': 'test<script>alert("xss")</script>',
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        })
        
        self.assertIn(b'Username can only contain letters, numbers, and underscores', response.data)
    
    def test_email_validation(self):
        """Test email validation"""
        # Try to register with invalid email
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'not-an-email',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        })
        
        self.assertIn(b'Invalid email address', response.data)
    
    def test_session_security(self):
        """Test session is cleared on logout"""
        # Create and login user
        with self.app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
        
        # Login
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Verify can access protected page
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        
        # Logout
        self.client.get('/logout')
        
        # Verify cannot access protected page after logout
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 302)  # Redirected to login

if __name__ == '__main__':
    unittest.main()
