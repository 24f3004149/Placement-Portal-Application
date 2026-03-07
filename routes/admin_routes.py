from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from sqlalchemy import or_
from models import db, User, Company, Student, Drive, Application

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def is_admin():
    return session.get('role') == 'admin'

@admin_bp.route('/dashboard')
def dashboard():
    if not is_admin(): return redirect(url_for('auth.login'))
    
    stats = {
        'total_students': Student.query.count(),
        'total_companies': Company.query.count(),
        'total_drives': Drive.query.count(),
        'pending_companies': Company.query.filter_by(status='Pending').count(),
        'total_applications': Application.query.count(),
    }
    return render_template('admin/dashboard.html', stats=stats)

@admin_bp.route('/companies')
def manage_companies():
    if not is_admin(): return redirect(url_for('auth.login'))
    
    search_query = request.args.get('q', '')
    if search_query:
        companies = Company.query.filter(
            or_(Company.id.like(search_query), Company.name.contains(search_query))
        ).all()
    else:
        companies = Company.query.all()
        
    return render_template('admin/manage_companies.html', companies=companies, search_query=search_query)

@admin_bp.route('/students')
def manage_students():
    if not is_admin(): return redirect(url_for('auth.login'))
    search_query = request.args.get('q', '')
    if search_query:
        students = Student.query.join(User).filter(
            or_(Student.id.like(search_query), 
                Student.name.contains(search_query),
                User.email.contains(search_query))
        ).all()
    else:
        students = Student.query.all()
    return render_template('admin/manage_students.html', students=students, search_query=search_query)

@admin_bp.route('/drives')
def manage_drives():
    if not is_admin(): return redirect(url_for('auth.login'))
    drives = Drive.query.all()
    return render_template('admin/manage_drives.html', drives=drives)

@admin_bp.route('/applications')
def manage_applications():
    if not is_admin(): return redirect(url_for('auth.login'))
    applications = Application.query.order_by(Application.id.desc()).all()
    return render_template('admin/manage_applications.html', applications=applications)

@admin_bp.route('/student/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    if not is_admin(): return redirect(url_for('auth.login'))
    
    student = Student.query.get_or_404(id)
    
    if request.method == 'POST':
        student.name = request.form['name']
        student.department = request.form['department']
        cgpa_str = request.form.get('cgpa')
        student.cgpa = float(cgpa_str) if cgpa_str else None
        
        db.session.commit()
        flash(f'Updated details for {student.name}.', 'success')
        return redirect(url_for('admin.manage_students'))
    
    return render_template('admin/edit_student.html', student=student)



@admin_bp.route('/company/approve/<int:id>')
def approve_company(id):
    if not is_admin(): return redirect(url_for('auth.login'))
    company = Company.query.get_or_404(id)
    company.status = 'Approved'
    db.session.commit()
    flash(f'{company.name} Approved!')
    return redirect(url_for('admin.manage_companies'))

@admin_bp.route('/company/reject/<int:id>')
def reject_company(id):
    if not is_admin(): return redirect(url_for('auth.login'))
    company = Company.query.get_or_404(id)
    company.status = 'Rejected'
    db.session.commit()
    return redirect(url_for('admin.manage_companies'))

@admin_bp.route('/company/blacklist/<int:id>')
def blacklist_company(id):
    if not is_admin(): return redirect(url_for('auth.login'))
    company = Company.query.get_or_404(id)
    if company.status == 'Approved':
        company.status = 'Blacklisted'
    elif company.status == 'Blacklisted':
        company.status = 'Approved'
    db.session.commit()
    return redirect(url_for('admin.manage_companies'))

@admin_bp.route('/company/delete/<int:id>')
def delete_company(id):
    if not is_admin(): return redirect(url_for('auth.login'))
    company = Company.query.get_or_404(id)
    user = User.query.get(company.user_id)
    db.session.delete(company)
    if user: db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin.manage_companies'))

@admin_bp.route('/student/blacklist/<int:id>')
def blacklist_student(id):
    if not is_admin(): return redirect(url_for('auth.login'))
    student = Student.query.get_or_404(id)
    if student.status == 'Active':
        student.status = 'Blacklisted'
    elif student.status == 'Blacklisted':
        student.status = 'Active'
    db.session.commit()
    return redirect(url_for('admin.manage_students'))

@admin_bp.route('/student/delete/<int:id>')
def delete_student(id):
    if not is_admin(): return redirect(url_for('auth.login'))
    student = Student.query.get_or_404(id)
    user = User.query.get(student.user_id)
    db.session.delete(student)
    if user: db.session.delete(user)
    db.session.commit()
    return redirect(url_for('admin.manage_students'))

@admin_bp.route('/drive/approve/<int:id>')
def approve_drive(id):
    if not is_admin(): return redirect(url_for('auth.login'))
    drive = Drive.query.get_or_404(id)
    drive.status = 'Approved'
    db.session.commit()
    return redirect(url_for('admin.manage_drives'))

@admin_bp.route('/drive/reject/<int:id>')
def reject_drive(id):
    if not is_admin(): return redirect(url_for('auth.login'))
    drive = Drive.query.get_or_404(id)
    drive.status = 'Rejected'
    db.session.commit()
    return redirect(url_for('admin.manage_drives'))