from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Company, Drive, Application
from datetime import datetime

company_bp = Blueprint('company', __name__, url_prefix='/company')

def is_company():
    return session.get('role') == 'company'

@company_bp.route('/dashboard')
def dashboard():
    if not is_company():
        return redirect(url_for('auth.login'))
    
    user_id = session.get('user_id')
    company = Company.query.filter_by(user_id=user_id).first()
    
    if company.status != 'Approved':
        flash('Your company profile is pending approval from the admin. You cannot access the dashboard yet.', 'warning')
        return render_template('company/pending.html')

    drives = Drive.query.filter_by(company_id=company.id).order_by(Drive.id.desc()).all()
    
    return render_template('company/dashboard.html', company=company, drives=drives)

@company_bp.route('/drive/create', methods=['GET', 'POST'])
def create_drive():
    if not is_company():
        return redirect(url_for('auth.login'))
        
    if request.method == 'POST':
        user_id = session.get('user_id')
        company = Company.query.filter_by(user_id=user_id).first()
        
        if company.status == 'Approved':
            deadline_str = request.form.get('application_deadline')
            deadline_obj = datetime.strptime(deadline_str, '%Y-%m-%d').date() if deadline_str else None

            new_drive = Drive(
                company_id=company.id,
                job_title=request.form['job_title'],
                description=request.form['description'],
                salary=float(request.form['salary']) if request.form['salary'] else None,
                eligibility_criteria=request.form.get('eligibility_criteria'),
                application_deadline=deadline_obj,
                status='Pending'
            )
            db.session.add(new_drive)
            db.session.commit()
            flash('Placement drive created successfully! It is now pending admin approval.', 'success')
            return redirect(url_for('company.dashboard'))
            
    return render_template('company/create_drive.html')

@company_bp.route('/drive/<int:drive_id>/applicants')
def view_applicants(drive_id):
    if not is_company():
        return redirect(url_for('auth.login'))
        
    drive = Drive.query.get_or_404(drive_id)
    applications = Application.query.filter_by(drive_id=drive.id).all()
    
    return render_template('company/view_applicants.html', drive=drive, applications=applications)

@company_bp.route('/application/update/<int:application_id>', methods=['POST'])
def update_application_status(application_id):
    if not is_company():
        return redirect(url_for('auth.login'))
        
    application = Application.query.get_or_404(application_id)
    new_status = request.form['status']
    
    application.status = new_status
    db.session.commit()
    
    flash(f"Updated {application.student.name}'s status to {new_status}", 'success')
    return redirect(url_for('company.view_applicants', drive_id=application.drive_id))

@company_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if not is_company(): return redirect(url_for('auth.login'))
    user_id = session.get('user_id')
    company = Company.query.filter_by(user_id=user_id).first()
    if request.method == 'POST':
        company.name = request.form['name']
        company.hr_contact = request.form['hr_contact']
        company.website = request.form['website']
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('company.profile'))
    return render_template('company/profile.html', company=company)

@company_bp.route('/drive/edit/<int:drive_id>', methods=['GET', 'POST'])
def edit_drive(drive_id):
    if not is_company(): return redirect(url_for('auth.login'))
    drive = Drive.query.get_or_404(drive_id)
    if request.method == 'POST':
        drive.job_title = request.form['job_title']
        drive.description = request.form['description']
        
        db.session.commit()
        flash('Drive updated successfully!', 'success')
        return redirect(url_for('company.dashboard'))
    return render_template('company/edit_drive.html', drive=drive)

@company_bp.route('/drive/delete/<int:drive_id>')
def delete_drive(drive_id):
    if not is_company(): return redirect(url_for('auth.login'))
    drive = Drive.query.get_or_404(drive_id)
    db.session.delete(drive)
    db.session.commit()
    flash('Drive deleted successfully!', 'danger')
    return redirect(url_for('company.dashboard'))

@company_bp.route('/drive/close/<int:drive_id>')
def close_drive(drive_id):
    if not is_company(): return redirect(url_for('auth.login'))
    drive = Drive.query.get_or_404(drive_id)
    drive.status = 'Closed'
    db.session.commit()
    flash('Drive has been closed.', 'info')
    return redirect(url_for('company.dashboard'))