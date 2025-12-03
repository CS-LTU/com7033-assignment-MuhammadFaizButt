from pymongo import MongoClient, ASCENDING
from bson.objectid import ObjectId
import csv
from datetime import datetime

class MongoDB:
    """MongoDB handler for patient data"""
    
    def __init__(self, app=None):
        self.client = None
        self.db = None
        self.patients = None
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize MongoDB connection"""
        mongo_uri = app.config['MONGO_URI']
        db_name = app.config['MONGO_DBNAME']
        
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.patients = self.db.patients
        
        # Create index on id field for faster queries
        self.patients.create_index([('id', ASCENDING)], unique=True)
    
    def load_dataset(self, csv_path):
        """Load patient data from CSV into MongoDB"""
        try:
            with open(csv_path, 'r') as file:
                csv_reader = csv.DictReader(file)
                patients_data = []
                
                for row in csv_reader:
                    # Convert numeric fields
                    patient = {
                        'id': int(row['id']),
                        'gender': row['gender'],
                        'age': float(row['age']),
                        'hypertension': int(row['hypertension']),
                        'heart_disease': int(row['heart_disease']),
                        'ever_married': row['ever_married'],
                        'work_type': row['work_type'],
                        'Residence_type': row['Residence_type'],
                        'avg_glucose_level': float(row['avg_glucose_level']),
                        'bmi': row['bmi'] if row['bmi'] != 'N/A' else None,
                        'smoking_status': row['smoking_status'],
                        'stroke': int(row['stroke']),
                        'created_at': datetime.utcnow()
                    }
                    patients_data.append(patient)
                
                # Clear existing data and insert new
                self.patients.delete_many({})
                if patients_data:
                    self.patients.insert_many(patients_data)
                
                return len(patients_data)
        except Exception as e:
            raise Exception(f"Error loading dataset: {str(e)}")
    
    def get_all_patients(self, skip=0, limit=50):
        """Get all patients with pagination"""
        return list(self.patients.find().skip(skip).limit(limit))
    
    def get_patient_by_id(self, patient_id):
        """Get a single patient by ID"""
        return self.patients.find_one({'id': int(patient_id)})
    
    def search_patients(self, query):
        """Search patients by various fields"""
        search_filter = {
            '$or': [
                {'id': {'$regex': str(query), '$options': 'i'}},
                {'gender': {'$regex': query, '$options': 'i'}},
                {'work_type': {'$regex': query, '$options': 'i'}},
                {'smoking_status': {'$regex': query, '$options': 'i'}}
            ]
        }
        return list(self.patients.find(search_filter).limit(50))
    
    def add_patient(self, patient_data):
        """Add a new patient"""
        # Get the next available ID
        last_patient = self.patients.find_one(sort=[('id', -1)])
        next_id = (last_patient['id'] + 1) if last_patient else 1
        
        patient_data['id'] = next_id
        patient_data['created_at'] = datetime.utcnow()
        
        result = self.patients.insert_one(patient_data)
        return result.inserted_id
    
    def update_patient(self, patient_id, patient_data):
        """Update an existing patient"""
        patient_data['updated_at'] = datetime.utcnow()
        result = self.patients.update_one(
            {'id': int(patient_id)},
            {'$set': patient_data}
        )
        return result.modified_count > 0
    
    def delete_patient(self, patient_id):
        """Delete a patient"""
        result = self.patients.delete_one({'id': int(patient_id)})
        return result.deleted_count > 0
    
    def get_statistics(self):
        """Get basic statistics about patients"""
        total = self.patients.count_documents({})
        stroke_count = self.patients.count_documents({'stroke': 1})
        
        return {
            'total_patients': total,
            'stroke_patients': stroke_count,
            'non_stroke_patients': total - stroke_count,
            'stroke_percentage': round((stroke_count / total * 100), 2) if total > 0 else 0
        }

# Global MongoDB instance
mongo = MongoDB()
