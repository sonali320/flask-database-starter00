# Part 6: Homework - Product Inventory App

## Activity Description

Build a **Product Inventory** application where you can:
- View all products in a table
- Add new products (name, quantity, price)
- Delete products from inventory

This homework combines everything you learned in Parts 1-5.

---

## What You Need to Do

### 1. Create 3 Routes in app.py

| Route           | Method       | What it does                       |
|-----------------|--------------|------------------------------------|
| `/`             | GET          | Show all products in a table       |
| `/add`          | GET, POST    | Show form + save new product       |
| `/delete/<id>`  | GET          | Delete product and go back to home |

### 2. Create Templates Folder

```
part-6/
├── app.py
├── Instruction.md
└── templates/         <- Create this folder
    ├── index.html     <- Products table
    └── add.html       <- Add product form
```

---

## Step-by-Step Guide

### Step 1: Create templates folder
```bash
mkdir templates
```

### Step 2: Create index.html (Home Page)

This page should show:
- A heading "Product Inventory"
- A link/button to go to `/add` page
- A table with columns: ID, Name, Quantity, Price, Action
- Delete link for each product

### Step 3: Create add.html (Add Product Form)

This page should have:
- A heading "Add New Product"
- A form with 3 input fields: name, quantity, price
- A submit button
- A link to go back to home

### Step 4: Add routes in app.py

Write the 3 routes in the section marked "Your code here..."

---

## Hints

### Hint 1: Home Route (`/`)
```python
@app.route('/')
def index():
    products = Product.query.all()  # Get all products from database
    return render_template('index.html', products=products)
```

### Hint 2: Add Route (`/add`)
```python
@app.route('/add', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form['name']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])

        new_product = Product(name=name, quantity=quantity, price=price)
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('add.html')
```

### Hint 3: Delete Route (`/delete/<id>`)
```python
@app.route('/delete/<int:id>')
def delete_product(id):
    product = Product.query.get_or_404(id)
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for('index'))
```

### Hint 4: HTML Table (index.html)
```html
<!DOCTYPE html>
<html>
<head>
    <title>Product Inventory</title>
</head>
<body>
    <h1>Product Inventory</h1>
    <a href="/add">+ Add Product</a>

    <table border="1">
        <tr>
            <th>ID</th>
            <th>Name</th>
            <th>Quantity</th>
            <th>Price</th>
            <th>Action</th>
        </tr>
        {% for product in products %}
        <tr>
            <td>{{ product.id }}</td>
            <td>{{ product.name }}</td>
            <td>{{ product.quantity }}</td>
            <td>${{ product.price }}</td>
            <td><a href="/delete/{{ product.id }}">Delete</a></td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
```

### Hint 5: HTML Form (add.html)
```html
<!DOCTYPE html>
<html>
<head>
    <title>Add Product</title>
</head>
<body>
    <h1>Add New Product</h1>

    <form method="POST">
        <label>Name:</label><br>
        <input type="text" name="name" required><br><br>

        <label>Quantity:</label><br>
        <input type="number" name="quantity" required><br><br>

        <label>Price:</label><br>
        <input type="number" name="price" step="0.01" required><br><br>

        <button type="submit">Add Product</button>
    </form>

    <br>
    <a href="/">← Back to Home</a>
</body>
</html>
```

---

## How to Test

1. Run the app: `python app.py`
2. Open: http://localhost:5000
3. Click "Add Product" → Fill form → Submit
4. See product in table
5. Click "Delete" → Product removed

---

## Bonus Challenges (Optional)

- Add `/edit/<id>` route to update product
- Show total inventory value (sum of quantity × price)
- Add search feature to find products by name
- Style the pages with CSS

---

## How to Run

```bash
# Make sure venv is activated
pip install flask flask-sqlalchemy
python app.py
```

Open browser: http://localhost:5000

Good luck!
