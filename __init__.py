from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from app.models import db, User
from app.database import mongo
from app.forms import RegistrationForm, LoginForm, PatientForm, SearchForm
from config import Config
import logging
from datetime import datetime

def create_app():
    """Application factory"""
    
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    mongo.init_app(app)
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Setup logging for security and debugging
    logging.basicConfig(
        filename='app.log',
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # ==================== ROUTES ====================
    
    @app.route('/')
    def index():
        """Home page"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return render_template('index.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """User registration with secure password hashing"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = RegistrationForm()
        
        if form.validate_on_submit():
            try:
                # Create new user with hashed password
                user = User(
                    username=form.username.data.strip(),
                    email=form.email.data.strip().lower()
                )
                user.set_password(form.password.data)
                
                db.session.add(user)
                db.session.commit()
                
                app.logger.info(f'New user registered: {user.username}')
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
                
            except Exception as e:
                db.session.rollback()
                app.logger.error(f'Registration error: {str(e)}')
                flash('An error occurred during registration. Please try again.', 'danger')
        
        return render_template('register.html', form=form)
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login with secure session handling"""
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = LoginForm()
        
        if form.validate_on_submit():
            # Prevent SQL injection by using ORM
            user = User.query.filter_by(username=form.username.data.strip()).first()
            
            if user and user.check_password(form.password.data):
                login_user(user)
                session.permanent = True
                app.logger.info(f'User logged in: {user.username}')
                
                # Redirect to next page or dashboard
                next_page = request.args.get('next')
                if next_page:
                    return redirect(next_page)
                return redirect(url_for('dashboard'))
            else:
                app.logger.warning(f'Failed login attempt for username: {form.username.data}')
                flash('Invalid username or password', 'danger')
        
        return render_template('login.html', form=form)
    
    @app.route('/logout')
    @login_required
    def logout():
        """Logout user and clear session"""
        app.logger.info(f'User logged out: {current_user.username}')
        logout_user()
        session.clear()
        flash('You have been logged out successfully.', 'info')
        return redirect(url_for('index'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Dashboard with patient statistics"""
        try:
            stats = mongo.get_statistics()
            return render_template('dashboard.html', stats=stats)
        except Exception as e:
            app.logger.error(f'Dashboard error: {str(e)}')
            flash('Error loading dashboard data.', 'danger')
            return render_template('dashboard.html', stats={})
    
    @app.route('/patients')
    @login_required
    def patients():
        """List all patients with pagination"""
        try:
            page = request.args.get('page', 1, type=int)
            per_page = 20
            skip = (page - 1) * per_page
            
            patients_list = mongo.get_all_patients(skip=skip, limit=per_page)
            
            return render_template('patients.html', 
                                 patients=patients_list, 
                                 page=page)
        except Exception as e:
            app.logger.error(f'Error loading patients: {str(e)}')
            flash('Error loading patient data.', 'danger')
            return render_template('patients.html', patients=[], page=1)
    
    @app.route('/patient/<int:patient_id>')
    @login_required
    def patient_detail(patient_id):
        """View single patient details"""
        try:
            patient = mongo.get_patient_by_id(patient_id)
            if not patient:
                flash('Patient not found.', 'warning')
                return redirect(url_for('patients'))
            
            return render_template('patient_detail.html', patient=patient)
        except Exception as e:
            app.logger.error(f'Error loading patient {patient_id}: {str(e)}')
            flash('Error loading patient details.', 'danger')
            return redirect(url_for('patients'))
    
    @app.route('/patient/add', methods=['GET', 'POST'])
    @login_required
    def add_patient():
        """Add new patient with input validation"""
        form = PatientForm()
        
        if form.validate_on_submit():
            try:
                # Sanitize and prepare patient data
                patient_data = {
                    'gender': form.gender.data,
                    'age': float(form.age.data),
                    'hypertension': int(form.hypertension.data),
                    'heart_disease': int(form.heart_disease.data),
                    'ever_married': form.ever_married.data,
                    'work_type': form.work_type.data,
                    'Residence_type': form.Residence_type.data,
                    'avg_glucose_level': float(form.avg_glucose_level.data),
                    'bmi': form.bmi.data if form.bmi.data else None,
                    'smoking_status': form.smoking_status.data,
                    'stroke': int(form.stroke.data)
                }
                
                patient_id = mongo.add_patient(patient_data)
                app.logger.info(f'New patient added by {current_user.username}')
                flash('Patient added successfully!', 'success')
                return redirect(url_for('patients'))
                
            except Exception as e:
                app.logger.error(f'Error adding patient: {str(e)}')
                flash('Error adding patient. Please try again.', 'danger')
        
        return render_template('patient_form.html', form=form, action='Add')
    
    @app.route('/patient/edit/<int:patient_id>', methods=['GET', 'POST'])
    @login_required
    def edit_patient(patient_id):
        """Edit existing patient"""
        patient = mongo.get_patient_by_id(patient_id)
        
        if not patient:
            flash('Patient not found.', 'warning')
            return redirect(url_for('patients'))
        
        form = PatientForm()
        
        if form.validate_on_submit():
            try:
                # Update patient data
                patient_data = {
                    'gender': form.gender.data,
                    'age': float(form.age.data),
                    'hypertension': int(form.hypertension.data),
                    'heart_disease': int(form.heart_disease.data),
                    'ever_married': form.ever_married.data,
                    'work_type': form.work_type.data,
                    'Residence_type': form.Residence_type.data,
                    'avg_glucose_level': float(form.avg_glucose_level.data),
                    'bmi': form.bmi.data if form.bmi.data else None,
                    'smoking_status': form.smoking_status.data,
                    'stroke': int(form.stroke.data)
                }
                
                mongo.update_patient(patient_id, patient_data)
                app.logger.info(f'Patient {patient_id} updated by {current_user.username}')
                flash('Patient updated successfully!', 'success')
                return redirect(url_for('patient_detail', patient_id=patient_id))
                
            except Exception as e:
                app.logger.error(f'Error updating patient {patient_id}: {str(e)}')
                flash('Error updating patient. Please try again.', 'danger')
        
        # Populate form with existing data
        if request.method == 'GET':
            form.gender.data = patient['gender']
            form.age.data = patient['age']
            form.hypertension.data = str(patient['hypertension'])
            form.heart_disease.data = str(patient['heart_disease'])
            form.ever_married.data = patient['ever_married']
            form.work_type.data = patient['work_type']
            form.Residence_type.data = patient['Residence_type']
            form.avg_glucose_level.data = patient['avg_glucose_level']
            form.bmi.data = patient['bmi']
            form.smoking_status.data = patient['smoking_status']
            form.stroke.data = str(patient['stroke'])
        
        return render_template('patient_form.html', 
                             form=form, 
                             action='Edit', 
                             patient_id=patient_id)
    
    @app.route('/patient/delete/<int:patient_id>', methods=['POST'])
    @login_required
    def delete_patient(patient_id):
        """Delete patient (POST only for security)"""
        try:
            if mongo.delete_patient(patient_id):
                app.logger.info(f'Patient {patient_id} deleted by {current_user.username}')
                flash('Patient deleted successfully!', 'success')
            else:
                flash('Patient not found.', 'warning')
        except Exception as e:
            app.logger.error(f'Error deleting patient {patient_id}: {str(e)}')
            flash('Error deleting patient.', 'danger')
        
        return redirect(url_for('patients'))
    
    @app.route('/search', methods=['GET', 'POST'])
    @login_required
    def search():
        """Search patients"""
        form = SearchForm()
        results = []
        
        if form.validate_on_submit():
            try:
                query = form.query.data.strip()
                results = mongo.search_patients(query)
                
                if not results:
                    flash('No patients found matching your search.', 'info')
                
            except Exception as e:
                app.logger.error(f'Search error: {str(e)}')
                flash('Error performing search.', 'danger')
        
        return render_template('search.html', form=form, results=results)
    
    @app.route('/load_dataset')
    @login_required
    def load_dataset():
        """Load CSV dataset into MongoDB (admin function)"""
        try:
            csv_path = app.config['DATASET_PATH']
            count = mongo.load_dataset(csv_path)
            app.logger.info(f'Dataset loaded: {count} records by {current_user.username}')
            flash(f'Successfully loaded {count} patient records!', 'success')
        except Exception as e:
            app.logger.error(f'Error loading dataset: {str(e)}')
            flash(f'Error loading dataset: {str(e)}', 'danger')
        
        return redirect(url_for('dashboard'))
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        app.logger.error(f'Internal error: {str(error)}')
        return render_template('500.html'), 500
    
    return app
