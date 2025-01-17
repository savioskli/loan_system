from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.letter_template import LetterType, LetterTemplate
from forms.letter_template_forms import LetterTypeForm, LetterTemplateForm
from extensions import db

letter_templates_bp = Blueprint('letter_templates', __name__, url_prefix='/admin/letter-templates')

@letter_templates_bp.route('/types', methods=['GET', 'POST'])
def list_types():
    form = LetterTypeForm()
    if form.validate_on_submit():
        new_type = LetterType(
            name=form.name.data,
            description=form.description.data,
            is_active=form.is_active.data
        )
        db.session.add(new_type)
        db.session.commit()
        flash('Letter Type created successfully!', 'success')
        return redirect(url_for('letter_templates.list_types'))
    
    letter_types = LetterType.query.all()
    return render_template('admin/letter_types.html', form=form, letter_types=letter_types)

@letter_templates_bp.route('/types/edit/<int:type_id>', methods=['GET', 'POST'])
def edit_type(type_id):
    letter_type = LetterType.query.get_or_404(type_id)
    form = LetterTypeForm(obj=letter_type)
    
    if form.validate_on_submit():
        form.populate_obj(letter_type)
        db.session.commit()
        flash('Letter Type updated successfully!', 'success')
        return redirect(url_for('letter_templates.list_types'))
    
    return render_template('admin/letter_type_edit.html', form=form, letter_type=letter_type)

@letter_templates_bp.route('/templates', methods=['GET', 'POST'])
def list_templates():
    form = LetterTemplateForm()
    if form.validate_on_submit():
        new_template = LetterTemplate(
            letter_type_id=form.letter_type_id.data,
            name=form.name.data,
            template_content=form.template_content.data,
            is_active=form.is_active.data
        )
        db.session.add(new_template)
        db.session.commit()
        flash('Letter Template created successfully!', 'success')
        return redirect(url_for('letter_templates.list_templates'))
    
    letter_templates = LetterTemplate.query.all()
    return render_template('admin/letter_templates.html', form=form, letter_templates=letter_templates)

@letter_templates_bp.route('/templates/edit/<int:template_id>', methods=['GET', 'POST'])
def edit_template(template_id):
    letter_template = LetterTemplate.query.get_or_404(template_id)
    form = LetterTemplateForm(obj=letter_template)
    
    if form.validate_on_submit():
        form.populate_obj(letter_template)
        db.session.commit()
        flash('Letter Template updated successfully!', 'success')
        return redirect(url_for('letter_templates.list_templates'))
    
    return render_template('admin/letter_template_edit.html', form=form, letter_template=letter_template)
