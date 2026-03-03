from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User, Company, Student

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # CHANGED: Get email instead of username
        email = request.form['email']
        password = request.form['password']
        
        # Query by email
        user = User.query.filter_by(email=email, password=password).first()
        
        if user:
            session['user_id'] = user.id
            session['role'] = user.role
            
            # --- Welcome Message Logic ---
            if user.role == 'admin':
                session['name'] = 'Admin'
            elif user.role == 'company':
                comp = Company.query.filter_by(user_id=user.id).first()
                # Fallback to email part if name not found
                session['name'] = comp.name if comp else email.split('@')[0]
            elif user.role == 'student':
                stu = Student.query.filter_by(user_id=user.id).first()
                session['name'] = stu.name if stu else email.split('@')[0]
            # -----------------------------

            if user.role == 'admin': return redirect(url_for('admin.dashboard'))
            if user.role == 'company': return redirect(url_for('company.dashboard'))
            if user.role == 'student': return redirect(url_for('student.dashboard'))
        
        flash('Invalid Email or Password')
    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # ... (getting email, password, role, name is the same) ...
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        name = request.form['name']

        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return redirect(url_for('auth.register'))

        new_user = User(email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        
        if role == 'company':
            # --- THIS IS THE UPDATE ---
            hr_contact = request.form.get('hr_contact')
            website = request.form.get('website')
            new_company = Company(user_id=new_user.id, name=name, hr_contact=hr_contact, website=website, status='Pending')
            db.session.add(new_company)
            # --------------------------
        elif role == 'student':
            department = request.form.get('department')
            new_student = Student(user_id=new_user.id, name=name, department=department, status='Active')
            db.session.add(new_student)
            
        db.session.commit()
        flash('Registration Successful! Please Login.')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.')
    return redirect(url_for('auth.login'))