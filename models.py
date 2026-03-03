from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# ... (User model is unchanged) ...

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    company_profile = db.relationship('Company', backref='user', uselist=False, cascade="all, delete")
    student_profile = db.relationship('Student', backref='user', uselist=False, cascade="all, delete")

# UPDATED Company Model
class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    hr_contact = db.Column(db.String(120)) # <-- NEW
    website = db.Column(db.String(100))    # <-- NEW
    status = db.Column(db.String(20), default='Pending')

# ... (Student model is unchanged) ...
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    status = db.Column(db.String(20), default='Active')
    resume_link = db.Column(db.String(255))

# UPDATED Drive Model
class Drive(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    job_title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    salary = db.Column(db.Float)
    eligibility_criteria = db.Column(db.Text) # <-- NEW
    application_deadline = db.Column(db.Date) # <-- NEW
    # Status: 'Pending', 'Approved', 'Closed'
    status = db.Column(db.String(20), default='Pending')
    company = db.relationship('Company', backref='drives')

# UPDATED Application Model
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.id'), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow) # <-- NEW
    status = db.Column(db.String(20), default='Applied')
    student = db.relationship('Student', backref='applications')
    drive = db.relationship('Drive', backref='applications')