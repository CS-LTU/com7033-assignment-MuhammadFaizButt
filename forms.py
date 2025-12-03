from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, FloatField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
from app.models import User
import re

class RegistrationForm(FlaskForm):
    """User registration form with validation"""
    
    username = StringField('Username', 
                          validators=[
                              DataRequired(message='Username is required'),
                              Length(min=3, max=20, message='Username must be between 3 and 20 characters')
                          ])
    
    email = StringField('Email', 
                       validators=[
                           DataRequired(message='Email is required'),
                           Email(message='Invalid email address')
                       ])
    
    password = PasswordField('Password', 
                            validators=[
                                DataRequired(message='Password is required'),
                                Length(min=6, message='Password must be at least 6 characters')
                            ])
    
    confirm_password = PasswordField('Confirm Password',
                                    validators=[
                                        DataRequired(message='Please confirm your password'),
                                        EqualTo('password', message='Passwords must match')
                                    ])
    
    def validate_username(self, username):
        """Check if username already exists"""
        # Prevent SQL injection by using ORM
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
        
        # Additional validation: only alphanumeric and underscore
        if not re.match(r'^[a-zA-Z0-9_]+$', username.data):
            raise ValidationError('Username can only contain letters, numbers, and underscores.')
    
    def validate_email(self, email):
        """Check if email already exists"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')

class LoginForm(FlaskForm):
    """User login form"""
    
    username = StringField('Username', 
                          validators=[DataRequired(message='Username is required')])
    
    password = PasswordField('Password', 
                            validators=[DataRequired(message='Password is required')])

class PatientForm(FlaskForm):
    """Patient data form with validation"""
    
    gender = SelectField('Gender', 
                        choices=[('', 'Select Gender'), ('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')],
                        validators=[DataRequired(message='Gender is required')])
    
    age = FloatField('Age', 
                     validators=[
                         DataRequired(message='Age is required'),
                         NumberRange(min=0, max=120, message='Age must be between 0 and 120')
                     ])
    
    hypertension = SelectField('Hypertension', 
                              choices=[('0', 'No'), ('1', 'Yes')],
                              validators=[DataRequired(message='Hypertension status is required')])
    
    heart_disease = SelectField('Heart Disease', 
                               choices=[('0', 'No'), ('1', 'Yes')],
                               validators=[DataRequired(message='Heart disease status is required')])
    
    ever_married = SelectField('Ever Married', 
                              choices=[('', 'Select'), ('No', 'No'), ('Yes', 'Yes')],
                              validators=[DataRequired(message='Marital status is required')])
    
    work_type = SelectField('Work Type', 
                           choices=[
                               ('', 'Select Work Type'),
                               ('children', 'Children'),
                               ('Govt_job', 'Government Job'),
                               ('Never_worked', 'Never Worked'),
                               ('Private', 'Private'),
                               ('Self-employed', 'Self-employed')
                           ],
                           validators=[DataRequired(message='Work type is required')])
    
    Residence_type = SelectField('Residence Type', 
                                choices=[('', 'Select'), ('Rural', 'Rural'), ('Urban', 'Urban')],
                                validators=[DataRequired(message='Residence type is required')])
    
    avg_glucose_level = FloatField('Average Glucose Level', 
                                   validators=[
                                       DataRequired(message='Glucose level is required'),
                                       NumberRange(min=0, max=500, message='Glucose level must be between 0 and 500')
                                   ])
    
    bmi = StringField('BMI (Body Mass Index)')
    
    smoking_status = SelectField('Smoking Status', 
                                choices=[
                                    ('', 'Select Status'),
                                    ('formerly smoked', 'Formerly Smoked'),
                                    ('never smoked', 'Never Smoked'),
                                    ('smokes', 'Smokes'),
                                    ('Unknown', 'Unknown')
                                ],
                                validators=[DataRequired(message='Smoking status is required')])
    
    stroke = SelectField('Stroke', 
                        choices=[('0', 'No Stroke'), ('1', 'Had Stroke')],
                        validators=[DataRequired(message='Stroke status is required')])
    
    def validate_bmi(self, bmi):
        """Validate BMI if provided"""
        if bmi.data:
            try:
                bmi_value = float(bmi.data)
                if bmi_value < 0 or bmi_value > 100:
                    raise ValidationError('BMI must be between 0 and 100')
            except ValueError:
                raise ValidationError('BMI must be a valid number')

class SearchForm(FlaskForm):
    """Search form for patients"""
    
    query = StringField('Search', validators=[DataRequired(message='Please enter a search term')])
