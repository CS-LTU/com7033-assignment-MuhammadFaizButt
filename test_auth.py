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

class AuthenticationTestCase(unittest.TestCase):
    """Test cases for user authentication"""
    
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
    
    def test_registration_success(self):
        """Test successful user registration"""
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Check if user was created
        with self.app.app_context():
            user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, 'test@example.com')
    
    def test_registration_duplicate_username(self):
        """Test registration with duplicate username"""
        # Create first user
        with self.app.app_context():
            user = User(username='testuser', email='test1@example.com')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        # Try to register with same username
        response = self.client.post('/register', data={
            'username': 'testuser',
            'email': 'test2@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        })
        
        self.assertIn(b'Username already exists', response.data)
    
    def test_login_success(self):
        """Test successful login"""
        # Create user
        with self.app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
        
        # Login
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post('/login', data={
            'username': 'nonexistent',
            'password': 'wrongpass'
        })
        
        self.assertIn(b'Invalid username or password', response.data)
    
    def test_password_hashing(self):
        """Test that passwords are properly hashed"""
        with self.app.app_context():
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpass123')
            
            # Password should be hashed, not plain text
            self.assertNotEqual(user.password_hash, 'testpass123')
            self.assertTrue(user.check_password('testpass123'))
            self.assertFalse(user.check_password('wrongpass'))
    
    def test_logout(self):
        """Test logout functionality"""
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
        
        # Logout
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'logged out', response.data)

if __name__ == '__main__':
    unittest.main()
