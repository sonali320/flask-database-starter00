"""
Part 6: Homework - Product Inventory App
========================================
See Instruction.md for full requirements and hints.

How to Run:
1. Make sure venv is activated
2. Install: pip install flask flask-sqlalchemy
3. Run: python app.py
4. Open browser: http://localhost:5000
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'  # required for flash messages

db = SQLAlchemy(app)

# ===========================
# Product Model
# ===========================
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Float, nullable=False)

# ===========================
# Routes
# ===========================

# Home page with search & summary
@app.route('/', methods=['GET', 'POST'])
def index():
    query = request.args.get('search', '')
    if query:
        products = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
    else:
        products = Product.query.all()

    total_quantity = sum(p.quantity for p in products)
    total_value = sum(p.quantity * p.price for p in products)

    return render_template('index.html', products=products, total_quantity=total_quantity,
                           total_value=total_value, search=query)

# Add Product
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])

        new_product = Product(name=name, quantity=quantity, price=price)
        db.session.add(new_product)
        db.session.commit()
        flash(f'✅ "{name}" added successfully!')
        return redirect(url_for('index'))

    return render_template('add_product.html')

# Edit Product
@app.route('/edit/<int:product_id>', methods=['GET', 'POST'])
def edit_product(product_id):
    product = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.quantity = int(request.form['quantity'])
        product.price = float(request.form['price'])
        db.session.commit()
        flash(f'✏️ "{product.name}" updated successfully!')
        return redirect(url_for('index'))

    return render_template('edit_product.html', product=product)

# Delete Product
@app.route('/delete/<int:product_id>')
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash(f'🗑️ "{product.name}" deleted successfully!')
    return redirect(url_for('index'))

# ===========================
# Initialize DB & Sample Data
# ===========================
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        if Product.query.count() == 0:
            sample_products = [
                Product(name="Apple iPhone 14", quantity=10, price=999.99),
                Product(name="Samsung Galaxy S23", quantity=8, price=899.99),
                Product(name="Dell XPS 13 Laptop", quantity=5, price=1199.99),
                Product(name="Sony WH-1000XM5 Headphones", quantity=15, price=349.99),
                Product(name="Logitech MX Master 3 Mouse", quantity=20, price=99.99)
            ]
            db.session.add_all(sample_products)
            db.session.commit()
            print("✅ Sample products added")

    app.run(debug=True)
