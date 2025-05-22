from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from utils.decorators import admin_required
from models.staff import Staff
from models.role import Role
from forms.staff_forms import StaffForm
from extensions import db

staff_bp = Blueprint('staff', __name__)

@staff_bp.route('/staff')
@login_required
@admin_required
def index():
    staff_members = Staff.query.join(Role).all()
    return render_template('admin/staff/index.html', staff_members=staff_members)

@staff_bp.route('/staff/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create():
    form = StaffForm()
    form.role_id.choices = [(r.id, r.name) for r in Role.query.all()]
    
    if form.validate_on_submit():
        staff = Staff(
            email=form.email.data,
            username=form.username.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            role_id=form.role_id.data,
            organization_id=form.organization_id.data if form.organization_id.data else None
        )
        staff.set_password(form.password.data)
        
        db.session.add(staff)
        db.session.commit()
        
        flash('Staff member created successfully!', 'success')
        return redirect(url_for('staff.index'))
    
    return render_template('admin/staff/form.html', form=form, title='Create Staff Member')
