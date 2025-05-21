from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models.location import County, SubCounty, Ward
from forms.location_forms import CountyForm, SubCountyForm, WardForm
from extensions import db
from utils.logging_utils import log_activity

location_bp = Blueprint('location', __name__)

# County Routes
@location_bp.route('/admin/counties')
@login_required
def manage_counties():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    
    query = County.query
    if search:
        query = query.filter(County.name.ilike(f'%{search}%'))
    
    pagination = query.order_by(County.name).paginate(page=page, per_page=per_page)
    counties = pagination.items
    
    return render_template('admin/locations/counties/index.html',
                           counties=counties,
                           pagination=pagination,
                           search=search)

@location_bp.route('/admin/counties/new', methods=['GET', 'POST'])
@login_required
def new_county():
    form = CountyForm()
    form.county = None
    
    if form.validate_on_submit():
        county = County(
            name=form.name.data,
            code=form.code.data,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        db.session.add(county)
        db.session.commit()
        
        log_activity(
            'Created new county',
            f'Created county {county.name}',
            'county',
            county.id
        )
        
        flash('County created successfully.', 'success')
        return redirect(url_for('location.manage_counties'))
    
    return render_template('admin/locations/counties/new.html', form=form)

@location_bp.route('/admin/counties/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_county(id):
    county = County.query.get_or_404(id)
    form = CountyForm(obj=county)
    form.county = county
    
    if form.validate_on_submit():
        county.name = form.name.data
        county.code = form.code.data
        county.updated_by = current_user.id
        db.session.commit()
        
        log_activity(
            'Updated county',
            f'Updated county {county.name}',
            'county',
            county.id
        )
        
        flash('County updated successfully.', 'success')
        return redirect(url_for('location.manage_counties'))
    
    return render_template('admin/locations/counties/edit.html', form=form, county=county)

@location_bp.route('/admin/counties/<int:id>/delete', methods=['POST'])
@login_required
def delete_county(id):
    county = County.query.get_or_404(id)
    name = county.name
    
    db.session.delete(county)
    db.session.commit()
    
    log_activity(
        'Deleted county',
        f'Deleted county {name}',
        'county',
        id
    )
    
    flash('County deleted successfully.', 'success')
    return redirect(url_for('location.manage_counties'))

# SubCounty Routes
@location_bp.route('/admin/subcounties')
@login_required
def manage_subcounties():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    county_id = request.args.get('county', type=int)
    
    query = SubCounty.query
    if search:
        query = query.filter(SubCounty.name.ilike(f'%{search}%'))
    if county_id:
        query = query.filter(SubCounty.county_id == county_id)
    
    pagination = query.order_by(SubCounty.name).paginate(page=page, per_page=per_page)
    subcounties = pagination.items
    counties = County.query.order_by(County.name).all()
    
    return render_template('admin/locations/subcounties/index.html',
                           subcounties=subcounties,
                           counties=counties,
                           pagination=pagination,
                           search=search,
                           selected_county=county_id)

@location_bp.route('/admin/subcounties/new', methods=['GET', 'POST'])
@login_required
def new_subcounty():
    form = SubCountyForm()
    form.subcounty = None
    form.county_id.choices = [(c.id, c.name) for c in County.query.order_by('name')]
    
    if form.validate_on_submit():
        subcounty = SubCounty(
            name=form.name.data,
            county_id=form.county_id.data,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        db.session.add(subcounty)
        db.session.commit()
        
        log_activity(
            'Created new sub-county',
            f'Created sub-county {subcounty.name}',
            'subcounty',
            subcounty.id
        )
        
        flash('Sub-County created successfully.', 'success')
        return redirect(url_for('location.manage_subcounties'))
    
    return render_template('admin/locations/subcounties/new.html', form=form)

@location_bp.route('/admin/subcounties/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_subcounty(id):
    subcounty = SubCounty.query.get_or_404(id)
    form = SubCountyForm(obj=subcounty)
    form.subcounty = subcounty
    form.county_id.choices = [(c.id, c.name) for c in County.query.order_by('name')]
    
    if form.validate_on_submit():
        subcounty.name = form.name.data
        subcounty.county_id = form.county_id.data
        subcounty.updated_by = current_user.id
        db.session.commit()
        
        log_activity(
            'Updated sub-county',
            f'Updated sub-county {subcounty.name}',
            'subcounty',
            subcounty.id
        )
        
        flash('Sub-County updated successfully.', 'success')
        return redirect(url_for('location.manage_subcounties'))
    
    return render_template('admin/locations/subcounties/edit.html', form=form, subcounty=subcounty)

@location_bp.route('/admin/subcounties/<int:id>/delete', methods=['POST'])
@login_required
def delete_subcounty(id):
    subcounty = SubCounty.query.get_or_404(id)
    name = subcounty.name
    
    db.session.delete(subcounty)
    db.session.commit()
    
    log_activity(
        'Deleted sub-county',
        f'Deleted sub-county {name}',
        'subcounty',
        id
    )
    
    flash('Sub-County deleted successfully.', 'success')
    return redirect(url_for('location.manage_subcounties'))

# Ward Routes
@location_bp.route('/admin/wards')
@login_required
def manage_wards():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search', '')
    county_id = request.args.get('county', type=int)
    subcounty_id = request.args.get('subcounty', type=int)
    
    query = Ward.query
    if search:
        query = query.filter(Ward.name.ilike(f'%{search}%'))
    if subcounty_id:
        query = query.filter(Ward.subcounty_id == subcounty_id)
    elif county_id:
        query = query.join(SubCounty).filter(SubCounty.county_id == county_id)
    
    pagination = query.join(SubCounty).join(County).order_by(County.name, SubCounty.name, Ward.name).paginate(page=page, per_page=per_page)
    wards = pagination.items
    counties = County.query.order_by(County.name).all()
    
    # Get subcounties for the selected county
    subcounties = []
    if county_id:
        subcounties = SubCounty.query.filter_by(county_id=county_id).order_by(SubCounty.name).all()
    
    return render_template('admin/locations/wards/index.html',
                           wards=wards,
                           counties=counties,
                           subcounties=subcounties,
                           pagination=pagination,
                           search=search,
                           selected_county=county_id,
                           selected_subcounty=subcounty_id)

@location_bp.route('/admin/wards/new', methods=['GET', 'POST'])
@login_required
def new_ward():
    form = WardForm()
    form.ward = None
    form.subcounty_id.choices = [(sc.id, f"{sc.name} - {sc.county.name}") 
                                for sc in SubCounty.query.join(County).order_by(County.name, SubCounty.name)]
    
    if form.validate_on_submit():
        ward = Ward(
            name=form.name.data,
            subcounty_id=form.subcounty_id.data,
            created_by=current_user.id,
            updated_by=current_user.id
        )
        db.session.add(ward)
        db.session.commit()
        
        log_activity(
            'Created new ward',
            f'Created ward {ward.name}',
            'ward',
            ward.id
        )
        
        flash('Ward created successfully.', 'success')
        return redirect(url_for('location.manage_wards'))
    
    return render_template('admin/locations/wards/new.html', form=form)

@location_bp.route('/admin/wards/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_ward(id):
    ward = Ward.query.get_or_404(id)
    form = WardForm(obj=ward)
    form.ward = ward
    form.subcounty_id.choices = [(sc.id, f"{sc.name} - {sc.county.name}") 
                                for sc in SubCounty.query.join(County).order_by(County.name, SubCounty.name)]
    
    if form.validate_on_submit():
        ward.name = form.name.data
        ward.subcounty_id = form.subcounty_id.data
        ward.updated_by = current_user.id
        db.session.commit()
        
        log_activity(
            'Updated ward',
            f'Updated ward {ward.name}',
            'ward',
            ward.id
        )
        
        flash('Ward updated successfully.', 'success')
        return redirect(url_for('location.manage_wards'))
    
    return render_template('admin/locations/wards/edit.html', form=form, ward=ward)

@location_bp.route('/admin/wards/<int:id>/delete', methods=['POST'])
@login_required
def delete_ward(id):
    ward = Ward.query.get_or_404(id)
    name = ward.name
    
    db.session.delete(ward)
    db.session.commit()
    
    log_activity(
        'Deleted ward',
        f'Deleted ward {name}',
        'ward',
        id
    )
    
    flash('Ward deleted successfully.', 'success')
    return redirect(url_for('location.manage_wards'))

# API Routes for Dynamic Dropdowns
@location_bp.route('/api/counties/<int:county_id>/subcounties')
@login_required
def get_subcounties(county_id):
    subcounties = SubCounty.query.filter_by(county_id=county_id).order_by(SubCounty.name).all()
    return jsonify([{'id': sc.id, 'name': sc.name} for sc in subcounties])

@location_bp.route('/api/subcounties/<int:subcounty_id>/wards')
@login_required
def get_wards(subcounty_id):
    wards = Ward.query.filter_by(subcounty_id=subcounty_id).order_by(Ward.name).all()
    return jsonify([{'id': w.id, 'name': w.name} for w in wards])
