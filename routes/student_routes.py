from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Student, Drive, Application

student_bp = Blueprint('student', __name__, url_prefix='/student')

# Helper function to check if the user is a logged-in student
def is_student():
    return session.get('role') == 'student'

# --- Student Dashboard ---
@student_bp.route('/dashboard')
def dashboard():
    if not is_student():
        return redirect(url_for('auth.login'))
    
    # Get the current student
    user_id = session.get('user_id')
    student = Student.query.filter_by(user_id=user_id).first()
    
    # Get all drives the student has already applied to
    my_applications = Application.query.filter_by(student_id=student.id).all()
    applied_drive_ids = [app.drive_id for app in my_applications]
    
    # Get all approved drives that the student has NOT applied to
    available_drives = Drive.query.filter(Drive.status == 'Approved', Drive.id.notin_(applied_drive_ids)).all()
    
    return render_template('student/dashboard.html', 
                           drives=available_drives, 
                           my_applications=my_applications)

# --- Apply to a Drive ---
@student_bp.route('/apply/<int:drive_id>')
def apply(drive_id):
    if not is_student():
        return redirect(url_for('auth.login'))
    
    user_id = session.get('user_id')
    student = Student.query.filter_by(user_id=user_id).first()
    
    # Check if already applied to prevent duplicates
    existing_app = Application.query.filter_by(student_id=student.id, drive_id=drive_id).first()
    
    if not existing_app:
        new_app = Application(student_id=student.id, drive_id=drive_id, status='Applied')
        db.session.add(new_app)
        db.session.commit()
        flash('Successfully applied for the drive!', 'success')
    else:
        flash('You have already applied for this drive.', 'warning')
        
    return redirect(url_for('student.dashboard'))

# --- Student Profile Page ---
@student_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if not is_student():
        return redirect(url_for('auth.login'))
        
    user_id = session.get('user_id')
    student = Student.query.filter_by(user_id=user_id).first()
    
    if request.method == 'POST':
        student = Student.query.filter_by(user_id=session.get('user_id')).first()
        student.name = request.form['name']
        student.department = request.form['department']
        student.cgpa = float(request.form.get('cgpa')) if request.form.get('cgpa') else None
        student.resume_link = request.form.get('resume_link') # <-- NEW
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('student.profile'))
        
    return render_template('student/profile.html', student=student)

# --- View Application History ---
@student_bp.route('/my_applications')
def my_applications():
    if not is_student():
        return redirect(url_for('auth.login'))
        
    user_id = session.get('user_id')
    student = Student.query.filter_by(user_id=user_id).first()
    applications = Application.query.filter_by(student_id=student.id).order_by(Application.id.desc()).all()
    
    return render_template('student/my_applications.html', applications=applications)