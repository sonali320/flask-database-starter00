"""
Part 3: Flask-SQLAlchemy ORM
============================
Say goodbye to raw SQL! Use Python classes to work with databases.

What You'll Learn:
- Setting up Flask-SQLAlchemy
- Creating Models (Python classes = database tables)
- ORM queries instead of raw SQL
- Relationships between tables (One-to-Many)

Prerequisites: Complete part-1 and part-2
Install: pip install flask-sqlalchemy
"""

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

app = Flask(__name__)
app.secret_key = 'your-secret-key'

# Database: academy.db (NEW)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///academy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# =============================================================================
# MODELS - TEACHER EXACTLY LIKE STUDENT (EXERCISE 1)
# =============================================================================
class Teacher(db.Model):  # EXERCISE 1: Exactly like Student
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)  # Many→1 Course
    
    def __repr__(self):
        return f'<Teacher {self.name}>'

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    teachers = db.relationship('Teacher', backref='course', lazy=True)  # 1 Course → Many Teachers
    students = db.relationship('Student', backref='course', lazy=True)
    
    def __repr__(self):
        return f'<Course {self.name}>'

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    def __repr__(self):
        return f'<Student {self.name}>'

# =============================================================================
# ROUTES - FULL TEACHER CRUD (EXERCISE 1)
# =============================================================================
@app.route('/')
def index():
    # EXERCISE 2: Students with Course + Teacher names
    students = Student.query.join(Course).outerjoin(Teacher).order_by(desc(Student.id)).all()
    return render_template('index.html', students=students)

@app.route('/teachers')
def teachers():
    teachers = Teacher.query.join(Course).order_by(Teacher.name).all()
    return render_template('teachers.html', teachers=teachers)

@app.route('/add-teacher', methods=['GET', 'POST'])
def add_teacher():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course_id = request.form['course_id']
        new_teacher = Teacher(name=name, email=email, course_id=course_id)
        db.session.add(new_teacher)
        db.session.commit()
        flash('Teacher added successfully!', 'success')
        return redirect(url_for('teachers'))
    courses = Course.query.all()
    return render_template('add_teacher.html', courses=courses)

@app.route('/edit-teacher/<int:id>', methods=['GET', 'POST'])
def edit_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    if request.method == 'POST':
        teacher.name = request.form['name']
        teacher.email = request.form['email']
        teacher.course_id = request.form['course_id']
        db.session.commit()
        flash('Teacher updated!', 'success')
        return redirect(url_for('teachers'))
    courses = Course.query.all()
    return render_template('edit_teacher.html', teacher=teacher, courses=courses)

@app.route('/delete-teacher/<int:id>')
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    db.session.delete(teacher)
    db.session.commit()
    flash('Teacher deleted!', 'danger')
    return redirect(url_for('teachers'))

# Student & Course routes (unchanged)
@app.route('/courses')
def courses():
    courses = Course.query.all()
    return render_template('courses.html', courses=courses)

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course_id = request.form['course_id']
        new_student = Student(name=name, email=email, course_id=course_id)
        db.session.add(new_student)
        db.session.commit()
        flash('Student added!', 'success')
        return redirect(url_for('index'))
    courses = Course.query.all()
    return render_template('add.html', courses=courses)

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.query.get_or_404(id)
    if request.method == 'POST':
        student.name = request.form['name']
        student.email = request.form['email']
        student.course_id = request.form['course_id']
        db.session.commit()
        flash('Student updated!', 'success')
        return redirect(url_for('index'))
    courses = Course.query.all()
    return render_template('edit.html', student=student, courses=courses)

@app.route('/delete/<int:id>')
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted!', 'danger')
    return redirect(url_for('index'))

@app.route('/add-course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form.get('description', '')
        teacher_id = request.form['teacher_id']  # NEW FIELD
        
        new_course = Course(name=name, description=description)
        db.session.add(new_course)
        db.session.commit()
        db.session.refresh(new_course)  # Get course ID
        
        # Assign teacher to course
        teacher = Teacher.query.get(teacher_id)
        if teacher:
            teacher.course_id = new_course.id  # Link teacher to new course
            db.session.commit()
        
        flash('Course added with teacher assignment!', 'success')
        return redirect(url_for('courses'))
    
    teachers = Teacher.query.all()  # PASS TEACHERS TO TEMPLATE
    return render_template('add_course.html', teachers=teachers)


# =============================================================================
# INITIALIZE DATABASE WITH SAMPLE DATA
# =============================================================================
def init_db():
    with app.app_context():
        db.create_all()
        if Teacher.query.count() == 0:
            # Sample Courses
            courses = [
                Course(name='Mathematics', description='Algebra & Calculus'),
                Course(name='Physics', description='Mechanics & Electromagnetism'),
                Course(name='Chemistry', description='Organic & Inorganic Chemistry'),
            ]
            db.session.add_all(courses)
            db.session.commit()
            
            # Sample Teachers (Many → 1 Course) - EXERCISE 1
            teachers = [
                Teacher(name='Dr. Sarah Wilson', email='sarah@academy.com', course_id=1),
                Teacher(name='Mr. John Davis', email='john@academy.com', course_id=1),
                Teacher(name='Prof. Lisa Chen', email='lisa@academy.com', course_id=2),
                Teacher(name='Dr. Raj Patel', email='raj@academy.com', course_id=3),
            ]
            db.session.add_all(teachers)
            
            # Sample Students
            students = [
                Student(name='Rahul Kumar', email='rahul@student.com', course_id=1),
                Student(name='Priya Singh', email='priya@student.com', course_id=2),
            ]
            db.session.add_all(students)
            db.session.commit()
            print("✅ academy.db created with Teachers + Students + Courses!")

if __name__ == '__main__':
    init_db()
    app.run(debug=True)


# =============================================================================
# ORM vs RAW SQL COMPARISON:
# =============================================================================
#
# Operation      | Raw SQL                          | SQLAlchemy ORM
# ---------------|----------------------------------|---------------------------
# Get all        | SELECT * FROM students           | Student.query.all()
# Get by ID      | SELECT * WHERE id = ?            | Student.query.get(id)
# Filter         | SELECT * WHERE name = ?          | Student.query.filter_by(name='John')
# Insert         | INSERT INTO students VALUES...   | db.session.add(student)
# Update         | UPDATE students SET...           | student.name = 'New'; db.session.commit()
# Delete         | DELETE FROM students WHERE...    | db.session.delete(student)
#
# =============================================================================
# COMMON QUERY METHODS:
# =============================================================================
#
# Student.query.all()                    - Get all records
# Student.query.first()                  - Get first record
# Student.query.get(1)                   - Get by primary key
# Student.query.get_or_404(1)            - Get or show 404 error
# Student.query.filter_by(name='John')   - Filter by exact value
# Student.query.filter(Student.name.like('%john%'))  - Filter with LIKE
# Student.query.order_by(Student.name)   - Order results
# Student.query.count()                  - Count records
#
# =============================================================================



# =============================================================================
# EXERCISE:
# =============================================================================
#
# 1. Add a `Teacher` model with a relationship to Course 
# (have one Course can be taught by many Teachers and one Teacher can only teach only one Course)
# In other words, create new Teacher model exactly like Student with all others things same 
# (relationship between the two, frontend page for teacher list, add new teacher, backend routes for add new teacher, edit teacher, delete teacher)
# Additional exercise - display list of students with course name and teacher name (taken from the course name) and vice versa

# 2. Try different query methods: `filter()`, `order_by()`, `limit()`
#
# =============================================================================