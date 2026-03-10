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

    hr_contact = db.Column(db.String(120))

    website = db.Column(db.String(100))

    status = db.Column(db.String(20), default='Pending')

    drives = db.relationship(
        'Drive',
        backref='company',
        cascade="all, delete"
    )
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    cgpa = db.Column(db.Float)
    status = db.Column(db.String(20), default='Active')
    resume_link = db.Column(db.String(255))

    applications = db.relationship(
        'Application',
        backref='student',
        cascade="all, delete-orphan"
    )

# UPDATED Drive Model
class Drive(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)

    job_title = db.Column(db.String(100), nullable=False)

    description = db.Column(db.Text)

    salary = db.Column(db.Float)

    eligibility_criteria = db.Column(db.Text)

    application_deadline = db.Column(db.Date)

    status = db.Column(db.String(20), default='Pending')

# UPDATED Application Model
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey('drive.id'), nullable=False)
    application_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='Applied')

    drive = db.relationship('Drive', backref='applications')

    __table_args__ = (
        db.UniqueConstraint('student_id', 'drive_id', name='unique_application'),
    )