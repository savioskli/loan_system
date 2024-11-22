from flask import Blueprint, render_template, request, flash, redirect, url_for
from models.product import Product
from extensions import db
from datetime import datetime

products_bp = Blueprint('products', __name__)

@products_bp.route('/products')
def manage_products():
    products = Product.query.all()
    return render_template('admin/products/list.html', products=products)

@products_bp.route('/products/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        try:
            product = Product(
                name=request.form['name'],
                code=request.form['code'],
                status=request.form['status'],
                interest_rate=request.form['interest_rate'],
                rate_method=request.form['rate_method'],
                processing_fee=request.form['processing_fee'],
                maintenance_fee=request.form['maintenance_fee'],
                insurance_fee=request.form['insurance_fee'],
                frequency=request.form['frequency'],
                min_amount=float(request.form['min_amount']),
                max_amount=float(request.form['max_amount']),
                min_term=int(request.form['min_term']),
                max_term=int(request.form['max_term']),
                collateral=request.form['collateral'],
                income_statement=request.form['income_statement']
            )
            db.session.add(product)
            db.session.commit()
            flash('Product added successfully!', 'success')
            return redirect(url_for('products.manage_products'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding product: {str(e)}', 'error')
            return redirect(url_for('products.add_product'))
    
    return render_template('admin/products/form.html', product=None)

@products_bp.route('/products/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    product = Product.query.get_or_404(id)
    
    if request.method == 'POST':
        try:
            product.name = request.form['name']
            product.code = request.form['code']
            product.status = request.form['status']
            product.interest_rate = request.form['interest_rate']
            product.rate_method = request.form['rate_method']
            product.processing_fee = request.form['processing_fee']
            product.maintenance_fee = request.form['maintenance_fee']
            product.insurance_fee = request.form['insurance_fee']
            product.frequency = request.form['frequency']
            product.min_amount = float(request.form['min_amount'])
            product.max_amount = float(request.form['max_amount'])
            product.min_term = int(request.form['min_term'])
            product.max_term = int(request.form['max_term'])
            product.collateral = request.form['collateral']
            product.income_statement = request.form['income_statement']
            product.updated_at = datetime.utcnow()
            
            db.session.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('products.manage_products'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating product: {str(e)}', 'error')
    
    return render_template('admin/products/form.html', product=product)

@products_bp.route('/products/delete/<int:id>', methods=['POST'])
def delete_product(id):
    product = Product.query.get_or_404(id)
    try:
        db.session.delete(product)
        db.session.commit()
        flash('Product deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting product: {str(e)}', 'error')
    
    return redirect(url_for('products.manage_products'))
