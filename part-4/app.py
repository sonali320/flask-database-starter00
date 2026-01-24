"""
Part 4: REST API with Flask
===========================
Build a JSON API for database operations (used by frontend apps, mobile apps, etc.)

What You'll Learn:
- REST API concepts (GET, POST, PUT, DELETE)
- JSON responses with jsonify
- API error handling
- Status codes
- Testing APIs with curl or Postman

Prerequisites: Complete part-3 (SQLAlchemy)
"""

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library_api.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# =============================================================================
# MODELS WITH RELATIONSHIP
# =============================================================================

class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    bio = db.Column(db.Text)
    city = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship: One author has many books
    books = db.relationship('Book', backref='author_obj', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'bio': self.bio,
            'city': self.city,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'book_count': len(self.books)
        }

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('author.id'), nullable=False)
    year = db.Column(db.Integer)
    isbn = db.Column(db.String(20), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'author_id': self.author_id,
            'author_name': self.author_obj.name if self.author_obj else None,
            'year': self.year,
            'isbn': self.isbn,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# =============================================================================
# AUTHOR API ROUTES
# =============================================================================

@app.route('/api/authors', methods=['GET'])
def get_authors():
    sort_column = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Author.query

    if hasattr(Author, sort_column):
        col = getattr(Author, sort_column)
        if order.lower() == 'desc':
            query = query.order_by(col.desc())
        else:
            query = query.order_by(col.asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    authors = pagination.items

    return jsonify({
        'success': True,
        'count': len(authors),
        'total_authors': pagination.total,
        'total_pages': pagination.pages,
        'current_page': pagination.page,
        'sort': sort_column,
        'order': order,
        'authors': [author.to_dict() for author in authors]
    })

@app.route('/api/authors/<int:id>', methods=['GET'])
def get_author(id):
    author = Author.query.get(id)
    if not author:
        return jsonify({'success': False, 'error': 'Author not found'}), 404
    return jsonify({'success': True, 'author': author.to_dict()})

@app.route('/api/authors', methods=['POST'])
def create_author():
    data = request.get_json()
    if not data or not data.get('name'):
        return jsonify({'success': False, 'error': 'Name is required'}), 400

    existing = Author.query.filter_by(name=data['name']).first()
    if existing:
        return jsonify({'success': False, 'error': 'Author already exists'}), 400

    new_author = Author(
        name=data['name'],
        bio=data.get('bio'),
        city=data.get('city')
    )

    db.session.add(new_author)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Author created successfully',
        'author': new_author.to_dict()
    }), 201

@app.route('/api/authors/<int:id>', methods=['PUT'])
def update_author(id):
    author = Author.query.get(id)
    if not author:
        return jsonify({'success': False, 'error': 'Author not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    if 'name' in data:
        author.name = data['name']
    if 'bio' in data:
        author.bio = data['bio']
    if 'city' in data:
        author.city = data['city']

    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Author updated successfully',
        'author': author.to_dict()
    })

@app.route('/api/authors/<int:id>', methods=['DELETE'])
def delete_author(id):
    author = Author.query.get(id)
    if not author:
        return jsonify({'success': False, 'error': 'Author not found'}), 404

    db.session.delete(author)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Author deleted successfully'})

# =============================================================================
# BOOK API ROUTES (Updated for Author relationship)
# =============================================================================

@app.route('/api/books', methods=['GET'])
def get_books():
    sort_column = request.args.get('sort', 'id')
    order = request.args.get('order', 'asc')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Book.query

    if hasattr(Book, sort_column):
        col = getattr(Book, sort_column)
        if order.lower() == 'desc':
            query = query.order_by(col.desc())
        else:
            query = query.order_by(col.asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    books = pagination.items

    return jsonify({
        'success': True,
        'count': len(books),
        'total_books': pagination.total,
        'total_pages': pagination.pages,
        'current_page': pagination.page,
        'sort': sort_column,
        'order': order,
        'books': [book.to_dict() for book in books]
    })

@app.route('/api/books/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({'success': False, 'error': 'Book not found'}), 404
    return jsonify({'success': True, 'book': book.to_dict()})

@app.route('/api/books', methods=['POST'])
def create_book():
    data = request.get_json()
    if not data or not data.get('title') or not data.get('author_id'):
        return jsonify({'success': False, 'error': 'Title and author_id are required'}), 400

    # Check if author exists
    author = Author.query.get(data['author_id'])
    if not author:
        return jsonify({'success': False, 'error': 'Author not found'}), 400

    if data.get('isbn'):
        existing = Book.query.filter_by(isbn=data['isbn']).first()
        if existing:
            return jsonify({'success': False, 'error': 'ISBN already exists'}), 400

    new_book = Book(
        title=data['title'],
        author_id=data['author_id'],
        year=data.get('year'),
        isbn=data.get('isbn')
    )

    db.session.add(new_book)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Book created successfully',
        'book': new_book.to_dict()
    }), 201

@app.route('/api/books/<int:id>', methods=['PUT'])
def update_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({'success': False, 'error': 'Book not found'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400

    if 'title' in data:
        book.title = data['title']
    if 'author_id' in data:
        author = Author.query.get(data['author_id'])
        if not author:
            return jsonify({'success': False, 'error': 'Author not found'}), 400
        book.author_id = data['author_id']
    if 'year' in data:
        book.year = data['year']
    if 'isbn' in data:
        book.isbn = data['isbn']

    db.session.commit()
    return jsonify({
        'success': True,
        'message': 'Book updated successfully',
        'book': book.to_dict()
    })

@app.route('/api/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({'success': False, 'error': 'Book not found'}), 404

    db.session.delete(book)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Book deleted successfully'})

# =============================================================================
# SEARCH & FILTER
# =============================================================================

@app.route('/api/books/search', methods=['GET'])
def search_books():
    query = Book.query

    title = request.args.get('q')
    if title:
        query = query.filter(Book.title.ilike(f'%{title}%'))

    author_name = request.args.get('author')
    if author_name:
        query = query.join(Author).filter(Author.name.ilike(f'%{author_name}%'))

    year = request.args.get('year')
    if year:
        query = query.filter_by(year=int(year))

    books = query.all()
    return jsonify({
        'success': True,
        'count': len(books),
        'books': [book.to_dict() for book in books]
    })

@app.route('/api/authors/search', methods=['GET'])
def search_authors():
    query = Author.query

    name = request.args.get('q')
    if name:
        query = query.filter(Author.name.ilike(f'%{name}%'))

    city = request.args.get('city')
    if city:
        query = query.filter(Author.city.ilike(f'%{city}%'))

    authors = query.all()
    return jsonify({
        'success': True,
        'count': len(authors),
        'authors': [author.to_dict() for author in authors]
    })

# =============================================================================
# ENHANCED TESTING PAGE
# =============================================================================

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Library API Manager</title>
        <style>
            body { font-family: 'Segoe UI', sans-serif; margin: 20px; background: #1a1a2e; color: #eee; }
            .container { max-width: 1200px; margin: auto; }
            h1 { color: #e94560; border-bottom: 2px solid #e94560; padding-bottom: 10px; }
            .section { background: #16213e; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
            input, select { padding: 8px; margin: 5px; border-radius: 4px; border: none; background: #0f3460; color: white; }
            button { padding: 8px 15px; border-radius: 4px; border: none; cursor: pointer; font-weight: bold; margin: 2px; }
            .btn-primary { background: #27ae60; color: white; }
            .btn-secondary { background: #3498db; color: white; }
            .btn-danger { background: #e74c3c; color: white; }
            table { width: 100%; border-collapse: collapse; margin-top: 20px; }
            th { text-align: left; background: #0f3460; padding: 12px; }
            td { padding: 12px; border-bottom: 1px solid #0f3460; }
            .tab { display: none; }
            .tab.active { display: block; }
            .tab-btn { background: #0f3460; color: white; padding: 10px 20px; border: none; cursor: pointer; margin-right: 5px; }
            .tab-btn.active { background: #e94560; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📚 Library API Manager</h1>
            
            <div style="margin-bottom: 20px;">
                <button class="tab-btn active" onclick="showTab('books')">Books</button>
                <button class="tab-btn" onclick="showTab('authors')">Authors</button>
            </div>

            <!-- Books Tab -->
            <div id="books" class="tab active">
                <div class="section">
                    <h3>Add New Book</h3>
                    <select id="book-author-id"></select>
                    <input type="text" id="book-title" placeholder="Title">
                    <input type="number" id="book-year" placeholder="Year">
                    <input type="text" id="book-isbn" placeholder="ISBN">
                    <button class="btn-primary" onclick="addBook()">Add Book</button>
                </div>
                <div class="section">
                    <h3>Books <small>(?page=1&per_page=5&sort=title&order=desc)</small></h3>
                    <div style="margin-bottom: 10px;">
                        <input type="number" id="page" value="1" style="width:60px"> 
                        <input type="number" id="per_page" value="10" style="width:80px">
                        <input type="text" id="sort" value="id" style="width:80px">
                        <input type="text" id="order" value="asc" style="width:60px">
                        <button class="btn-secondary" onclick="fetchBooks()">Refresh</button>
                    </div>
                <div style="margin-bottom: 10px;">
                        <input type="text" id="search-title" placeholder="Search title">
                        <input type="text" id="search-author" placeholder="Author name">
                        <input type="number" id="search-year" placeholder="Year" style="width:80px">
                        <button class="btn-secondary" onclick="searchBooks()">Search</button>
                        <button class="btn-danger" onclick="fetchBooks()">Clear</button>
                    </div>

                    <table>
                        <thead>
                            <tr>
                                <th>ID</th><th>Title</th><th>Author</th><th>Year</th><th>ISBN</th><th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="book-table"></tbody>
                    </table>
                </div>
            </div>

            <!-- Authors Tab -->
            <div id="authors" class="tab">
                <div class="section">
                    <h3>Add New Author</h3>
                    <input type="text" id="author-name" placeholder="Name">
                    <input type="text" id="author-city" placeholder="City">          
                    <button class="btn-primary" onclick="addAuthor()">Add Author</button>
                </div>
            <div style="margin-bottom: 10px;">
                    <input type="text" id="search-author-name" placeholder="Author name">
                    <input type="text" id="search-author-city" placeholder="City">
                    <button class="btn-secondary" onclick="searchAuthors()">Search</button>
                    <button class="btn-danger" onclick="fetchAuthors()">Clear</button>
                </div>

                <div class="section">
                    <h3>Authors</h3>
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th><th>Name</th><th>City</th><th>Book Count</th><th>Actions</th>
                            </tr>
                        </thead>
                        <tbody id="author-table"></tbody>
                    </table>
                </div>
            </div>
        </div>

        <script>
            let authors = [];

            async function loadAuthors() {
                const response = await fetch('/api/authors');
                const data = await response.json();
                authors = data.authors;
                const authorSelect = document.getElementById('book-author-id');
                authorSelect.innerHTML = authors.map(a => 
                    `<option value="${a.id}">${a.name}</option>`
                ).join('');
            }

            async function fetchBooks() {
                const page = document.getElementById('page').value;
                const per_page = document.getElementById('per_page').value;
                const sort = document.getElementById('sort').value;
                const order = document.getElementById('order').value;
                
                const url = `/api/books?page=${page}&per_page=${per_page}&sort=${sort}&order=${order}`;
                const response = await fetch(url);
                const data = await response.json();
                
                const tableBody = document.getElementById('book-table');
                tableBody.innerHTML = data.books.map(book => `
                    <tr id="row-${book.id}">
                        <td>${book.id}</td>
                        <td class="title-cell">${book.title}</td>
                        <td>${book.author_name}</td>
                        <td>${book.year || ''}</td>
                        <td>${book.isbn || ''}</td>
                        <td>
                            <button class="btn-secondary" onclick="editBook(${book.id})">Edit</button>
                            <button class="btn-danger" onclick="deleteBook(${book.id})">Delete</button>
                        </td>
                    </tr>
                `).join('');
            }

            async function fetchAuthors() {
                const response = await fetch('/api/authors');
                const data = await response.json();
                const tableBody = document.getElementById('author-table');
                tableBody.innerHTML = data.authors.map(author => `
                    <tr id="author-row-${author.id}">
                        <td>${author.id}</td>
                        <td>${author.name}</td>
                        <td>${author.city || ''}</td>
                        <td>${author.book_count}</td>
                        <td>
                            <button class="btn-secondary" onclick="editAuthor(${author.id})">Edit</button>
                            <button class="btn-danger" onclick="deleteAuthor(${author.id})">Delete</button>
                        </td>
                    </tr>
                `).join('');
            }

            async function addBook() {
                const data = {
                    title: document.getElementById('book-title').value,
                    author_id: parseInt(document.getElementById('book-author-id').value),
                    year: parseInt(document.getElementById('book-year').value) || null,
                    isbn: document.getElementById('book-isbn').value
                };
                await fetch('/api/books', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                document.getElementById('book-title').value = '';
                document.getElementById('book-year').value = '';
                document.getElementById('book-isbn').value = '';
                fetchBooks();
            }

            async function addAuthor() {
                const data = {
                    name: document.getElementById('author-name').value,
                    city: document.getElementById('author-city').value,
                    bio: document.getElementById('author-bio').value
                };
                await fetch('/api/authors', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                document.getElementById('author-name').value = '';
                document.getElementById('author-city').value = '';
                document.getElementById('author-bio').value = '';
                await loadAuthors();
                fetchAuthors();
            }

            async function deleteBook(id) {
                if (confirm('Delete this book?')) {
                    await fetch(`/api/books/${id}`, {method: 'DELETE'});
                    fetchBooks();
                }
            }

            async function deleteAuthor(id) {
                if (confirm('Delete this author and all their books?')) {
                    await fetch(`/api/authors/${id}`, {method: 'DELETE'});
                    await loadAuthors();
                    fetchAuthors();
                }
            }
            
            function editBook(id) {
    const row = document.getElementById(`row-${id}`);
    const book = {
        title: row.children[1].innerText,
        author: row.children[2].innerText,
        year: row.children[3].innerText,
        isbn: row.children[4].innerText
    };

    row.innerHTML = `
        <td>${id}</td>
        <td><input value="${book.title}" id="title-${id}"></td>
        <td>
            <select id="author-${id}">
                ${authors.map(a =>
                    `<option value="${a.id}" ${a.name === book.author ? 'selected' : ''}>
                        ${a.name}
                    </option>`
                ).join('')}
            </select>
        </td>
        <td><input type="number" value="${book.year}" id="year-${id}"></td>
        <td><input value="${book.isbn}" id="isbn-${id}"></td>
        <td>
            <button class="btn-primary" onclick="saveBook(${id})">Save</button>
            <button class="btn-danger" onclick="fetchBooks()">Cancel</button>
        </td>
    `;
}

        async function saveBook(id) {
    const data = {
        title: document.getElementById(`title-${id}`).value,
        author_id: parseInt(document.getElementById(`author-${id}`).value),
        year: parseInt(document.getElementById(`year-${id}`).value) || null,
        isbn: document.getElementById(`isbn-${id}`).value
    };

    await fetch(`/api/books/${id}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });

    fetchBooks();
}

            function editAuthor(id) {
    const row = document.getElementById(`author-row-${id}`);
    const name = row.children[1].innerText;
    const city = row.children[2].innerText;

    row.innerHTML = `
        <td>${id}</td>
        <td><input value="${name}" id="name-${id}"></td>
        <td><input value="${city}" id="city-${id}"></td>
        <td>-</td>
        <td>
            <button class="btn-primary" onclick="saveAuthor(${id})">Save</button>
            <button class="btn-danger" onclick="fetchAuthors()">Cancel</button>
        </td>
    `;
}

       async function saveAuthor(id) {
    const data = {
        name: document.getElementById(`name-${id}`).value,
        city: document.getElementById(`city-${id}`).value
    };

    await fetch(`/api/authors/${id}`, {
        method: 'PUT',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });

    fetchAuthors();
    loadAuthors();
}

        async function searchBooks() {
    const title = document.getElementById('search-title').value;
    const author = document.getElementById('search-author').value;
    const year = document.getElementById('search-year').value;

    let url = `/api/books/search?`;

    if (title) url += `q=${encodeURIComponent(title)}&`;
    if (author) url += `author=${encodeURIComponent(author)}&`;
    if (year) url += `year=${year}&`;

    const response = await fetch(url);
    const data = await response.json();

    const tableBody = document.getElementById('book-table');
    tableBody.innerHTML = data.books.map(book => `
        <tr id="row-${book.id}">
            <td>${book.id}</td>
            <td>${book.title}</td>
            <td>${book.author_name}</td>
            <td>${book.year || ''}</td>
            <td>${book.isbn || ''}</td>
            <td>
                <button class="btn-secondary" onclick="editBook(${book.id})">Edit</button>
                <button class="btn-danger" onclick="deleteBook(${book.id})">Delete</button>
            </td>
        </tr>
    `).join('');
}
 
        async function searchAuthors() {
    const name = document.getElementById('search-author-name').value;
    const city = document.getElementById('search-author-city').value;

    let url = `/api/authors/search?`;

    if (name) url += `q=${encodeURIComponent(name)}&`;
    if (city) url += `city=${encodeURIComponent(city)}&`;

    const response = await fetch(url);
    const data = await response.json();

    const tableBody = document.getElementById('author-table');
    tableBody.innerHTML = data.authors.map(author => `
        <tr id="author-row-${author.id}">
            <td>${author.id}</td>
            <td>${author.name}</td>
            <td>${author.city || ''}</td>
            <td>${author.book_count}</td>
            <td>
                <button class="btn-secondary" onclick="editAuthor(${author.id})">Edit</button>
                <button class="btn-danger" onclick="deleteAuthor(${author.id})">Delete</button>
            </td>
        </tr>
    `).join('');
}

            function showTab(tabName) {
                document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
                document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
                document.getElementById(tabName).classList.add('active');
                event.target.classList.add('active');
            }

            // Initialize
            loadAuthors().then(() => {
                fetchBooks();
                fetchAuthors();
            });
        </script>
    </body>
    </html>
    '''

# =============================================================================
# INITIALIZE DATABASE
# =============================================================================

def init_db():
    with app.app_context():
        db.create_all()
        
        if Author.query.count() == 0:
            # Sample authors
            authors_data = [
                {'name': 'Eric Matthes', 'city': 'USA', 'bio': 'Python educator'},
                {'name': 'Miguel Grinberg', 'city': 'Canada', 'bio': 'Flask expert'},
                {'name': 'Robert C. Martin', 'city': 'USA', 'bio': 'Clean Code author'}
            ]
            
            for data in authors_data:
                author = Author(**data)
                db.session.add(author)
            
            db.session.commit()
            
            # Sample books
            books_data = [
                {'title': 'Python Crash Course', 'author_id': 1, 'year': 2019, 'isbn': '978-1593279288'},
                {'title': 'Flask Web Development', 'author_id': 2, 'year': 2018, 'isbn': '978-1491991732'},
                {'title': 'Clean Code', 'author_id': 3, 'year': 2008, 'isbn': '978-0132350884'},
            ]
            
            for data in books_data:
                book = Book(**data)
                db.session.add(book)
            
            db.session.commit()
            print('✅ Database initialized with sample data!')

if __name__ == '__main__':
    init_db()
    print("🚀 API running at http://localhost:5000")
    print("📱 Test endpoints:")
    print("   GET /api/books?page=1&per_page=5&sort=title&order=desc")
    print("   GET /api/authors")
    print("   POST /api/books (JSON body required)")
    app.run(debug=True)


# =============================================================================
# REST API CONCEPTS:
# =============================================================================
#
# HTTP Method | CRUD      | Typical Use
# ------------|-----------|---------------------------
# GET         | Read      | Retrieve data
# POST        | Create    | Create new resource
# PUT         | Update    | Update entire resource
# PATCH       | Update    | Update partial resource
# DELETE      | Delete    | Remove resource
#
# =============================================================================
# HTTP STATUS CODES:
# =============================================================================
#
# Code | Meaning
# -----|------------------
# 200  | OK (Success)
# 201  | Created
# 400  | Bad Request (client error)
# 404  | Not Found
# 500  | Internal Server Error
#
# =============================================================================
# KEY FUNCTIONS:
# =============================================================================
#
# jsonify()           - Convert Python dict to JSON response
# request.get_json()  - Get JSON data from request body
# request.args.get()  - Get query parameters (?key=value)
#
# =============================================================================


# =============================================================================
# EXERCISE:
# =============================================================================
#
# 1. Create new class say "Author" with fields id, name, bio, city with its table. 
# Write all CRUD api routes for it similar to Book class.
# Additionally try to link Book and Author class such that each book has one author and one author can have multiple books.

# 1. Create 2 simple frontend using JavaScript fetch()
# This is a bigger exercise. Create a frontend in HTML and JS that uses all api routes and displays data dynamically, along with create/edit/delete functionality.
# Since the API is through n through accessible on the computer/server, you don't need to use render_template from flask, instead, 
# you can directly use ipaddress:portnumber/apiroute from any where. So your HTML JS code can be anywhere on computer (not necessarily in flask)  

# 3. Add pagination: `/api/books?page=1&per_page=10` 
# Hint - the sqlalchemy provides paginate method. 
# OPTIONAL - For ease of understanding, create a new api say /api/books-with-pagination which takes page number and number of books per page

# 4. Add sorting: `/api/books?sort=title&order=desc`
# OPTIONAL - For ease of understanding, create a new api say /api/books-with-sorting
#
# =============================================================================