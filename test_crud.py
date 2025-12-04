import unittest
from app import create_app
from app.models import db, User
from app.database import mongo
from config import Config

class TestConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    MONGO_DBNAME = 'test_stroke_prediction_db'

class CRUDTestCase(unittest.TestCase):
    """Test cases for CRUD operations"""
    
    def setUp(self):
        """Set up test client and database"""
        self.app = create_app()
        self.app.config.from_object(TestConfig)
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Create test user
            user = User(username='testuser', email='test@example.com')
            user.set_password('testpass123')
            db.session.add(user)
            db.session.commit()
            
            # Clear MongoDB test database
            mongo.patients.delete_many({})
        
        # Login the test user
        self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
    
    def tearDown(self):
        """Clean up after tests"""
        with self.app.app_context():
            mongo.patients.delete_many({})
            db.session.remove()
            db.drop_all()
    
    def test_add_patient(self):
        """Test adding a new patient"""
        response = self.client.post('/patient/add', data={
            'gender': 'Male',
            'age': 67,
            'hypertension': '1',
            'heart_disease': '0',
            'ever_married': 'Yes',
            'work_type': 'Private',
            'Residence_type': 'Urban',
            'avg_glucose_level': 228.69,
            'bmi': '36.6',
            'smoking_status': 'formerly smoked',
            'stroke': '1'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Patient added successfully', response.data)
        
        # Verify patient was added to MongoDB
        with self.app.app_context():
            patients = list(mongo.patients.find())
            self.assertEqual(len(patients), 1)
            self.assertEqual(patients[0]['gender'], 'Male')
    
    def test_view_patients(self):
        """Test viewing patients list"""
        # Add a test patient
        with self.app.app_context():
            mongo.add_patient({
                'gender': 'Female',
                'age': 45,
                'hypertension': 0,
                'heart_disease': 0,
                'ever_married': 'Yes',
                'work_type': 'Private',
                'Residence_type': 'Rural',
                'avg_glucose_level': 120.5,
                'bmi': '28.0',
                'smoking_status': 'never smoked',
                'stroke': 0
            })
        
        response = self.client.get('/patients')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Patients List', response.data)
    
    def test_view_patient_detail(self):
        """Test viewing individual patient details"""
        # Add a test patient
        with self.app.app_context():
            mongo.add_patient({
                'gender': 'Male',
                'age': 50,
                'hypertension': 1,
                'heart_disease': 0,
                'ever_married': 'Yes',
                'work_type': 'Govt_job',
                'Residence_type': 'Urban',
                'avg_glucose_level': 150.0,
                'bmi': '30.0',
                'smoking_status': 'smokes',
                'stroke': 0
            })
            patient = mongo.patients.find_one()
        
        response = self.client.get(f'/patient/{patient["id"]}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Patient Details', response.data)
    
    def test_update_patient(self):
        """Test updating patient information"""
        # Add a test patient
        with self.app.app_context():
            mongo.add_patient({
                'gender': 'Female',
                'age': 30,
                'hypertension': 0,
                'heart_disease': 0,
                'ever_married': 'No',
                'work_type': 'Private',
                'Residence_type': 'Urban',
                'avg_glucose_level': 90.0,
                'bmi': '25.0',
                'smoking_status': 'never smoked',
                'stroke': 0
            })
            patient = mongo.patients.find_one()
            patient_id = patient['id']
        
        # Update patient
        response = self.client.post(f'/patient/edit/{patient_id}', data={
            'gender': 'Female',
            'age': 31,  # Changed age
            'hypertension': '0',
            'heart_disease': '0',
            'ever_married': 'Yes',  # Changed marital status
            'work_type': 'Private',
            'Residence_type': 'Urban',
            'avg_glucose_level': 95.0,  # Changed glucose
            'bmi': '25.0',
            'smoking_status': 'never smoked',
            'stroke': '0'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Patient updated successfully', response.data)
        
        # Verify changes
        with self.app.app_context():
            updated_patient = mongo.get_patient_by_id(patient_id)
            self.assertEqual(updated_patient['age'], 31)
            self.assertEqual(updated_patient['ever_married'], 'Yes')
    
    def test_delete_patient(self):
        """Test deleting a patient"""
        # Add a test patient
        with self.app.app_context():
            mongo.add_patient({
                'gender': 'Male',
                'age': 60,
                'hypertension': 1,
                'heart_disease': 1,
                'ever_married': 'Yes',
                'work_type': 'Self-employed',
                'Residence_type': 'Rural',
                'avg_glucose_level': 200.0,
                'bmi': '35.0',
                'smoking_status': 'formerly smoked',
                'stroke': 1
            })
            patient = mongo.patients.find_one()
            patient_id = patient['id']
        
        # Delete patient
        response = self.client.post(f'/patient/delete/{patient_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Patient deleted successfully', response.data)
        
        # Verify deletion
        with self.app.app_context():
            deleted_patient = mongo.get_patient_by_id(patient_id)
            self.assertIsNone(deleted_patient)
    
    def test_search_patients(self):
        """Test patient search functionality"""
        # Add test patients
        with self.app.app_context():
            mongo.add_patient({
                'gender': 'Male',
                'age': 55,
                'hypertension': 0,
                'heart_disease': 0,
                'ever_married': 'Yes',
                'work_type': 'Govt_job',
                'Residence_type': 'Urban',
                'avg_glucose_level': 110.0,
                'bmi': '28.0',
                'smoking_status': 'never smoked',
                'stroke': 0
            })
        
        response = self.client.post('/search', data={
            'query': 'Govt_job'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Govt_job', response.data)

if __name__ == '__main__':
    unittest.main()
