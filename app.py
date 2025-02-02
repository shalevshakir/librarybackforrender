from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import date, timedelta



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG']= False
db = SQLAlchemy(app)
CORS(app)



class Book(db.Model):
    __tablename__ = 'books'
    book_ID = db.Column(db.Integer, primary_key=True, nullable=False)
    author = db.Column(db.Text, nullable=False)
    type = db.Column(db.Integer, nullable=False)
    year_publised = db.Column(db.Integer, nullable=False)
    book_name = db.Column(db.Text, nullable=False)
    available = db.Column(db.Boolean, nullable=False, default=True)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    loans = db.relationship('Loan', backref='book', lazy=True)

class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String, nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)
    

    loans = db.relationship('Loan', backref='customer', lazy=True)

class Loan(db.Model):
    __tablename__ = 'loans'
    loan_ID = db.Column(db.Integer, primary_key=True, nullable=False)
    cust_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_ID'), nullable=False)
    loandate = db.Column(db.Date, nullable=False)
    returndate = db.Column(db.Date, nullable=True)
    book_returned = db.Column(db.Boolean, nullable=False, default=False)
   
    

def defaultdata():
    if Book.query.count() == 0:
        books = [
            Book(book_ID=1, author="J.K. Rowling", type=1, year_publised=1997, book_name="Harry Potter", available=True, is_deleted=False),
            Book(book_ID=2, author="J.R.R. Tolkien", type=2, year_publised=1954, book_name="The Lord of the Rings", available=True, is_deleted=False),
            Book(book_ID=3, author="George Orwell", type=3, year_publised=1949, book_name="1984", available=False, is_deleted=False)
        ]
        db.session.add_all(books)

    if Customer.query.count() == 0:
        customers = [
            Customer(id=1, name="Alice", city="Tel Aviv", age=25, phone="0501234567", active=True),
            Customer(id=2, name="Bob", city="Jerusalem", age=32, phone="0523456789", active=True),
            Customer(id=3, name="Charlie", city="Haifa", age=28, phone="0539876543", active=False)
        ]
        db.session.add_all(customers)

    if Loan.query.count() == 0:
        loans = [
            Loan(loan_ID=1, cust_id=1, book_id=1, loandate=date(2025, 1, 10), returndate=date(2025, 1, 20)),
            Loan(loan_ID=2, cust_id=2, book_id=2, loandate=date(2025, 1, 15), returndate=date(2025, 1, 20)),
            Loan(loan_ID=3, cust_id=1, book_id=3, loandate=date(2025, 1, 5), returndate=date(2025, 1, 7))
        ]
        db.session.add_all(loans)

    db.session.commit()

# books crud

# create a new book
@app.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    new_book = Book(
        author=data['author'],
        type=data['type'],
        year_publised=data['year_publised'],
        book_name=data['book_name'],
        available=data.get('available', True),
        is_deleted=False
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message': 'Book added successfully'}), 201


# retrieve all books but not deleted
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.filter_by(is_deleted=False).all()
    return jsonify([{
        'book_ID': book.book_ID,
        'author': book.author,
        'type': book.type,
        'year_publised': book.year_publised,
        'book_name': book.book_name,
        'available': book.available
   
    } for book in books])
    

# Retrieve available books
@app.route('/books/available', methods=['GET'])
def get_available_books():
    books = Book.query.filter_by(available=True, is_deleted=False).all()
    return jsonify([{
        'book_ID': book.book_ID,
        'book_name': book.book_name,
        'author': book.author,
        'type': book.type,
        'year_publised': book.year_publised
    } for book in books])

# delete_book
@app.route('/books/<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    book.is_deleted = True
    db.session.commit()
    return jsonify({'message': 'Book marked as deleted successfully'})
# end of book crud

# customers crud

# Retrieve all customers
@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.filter_by(is_deleted=False).all()
    return jsonify([{
        'id': customer.id,
        'name': customer.name,
        'city': customer.city,
        'age': customer.age,
        'phone': customer.phone,
        'active': customer.active
    } for customer in customers])

# Retrieve active customers and not deleted
@app.route('/customers/active', methods=['GET'])
def get_active_customers():
    customers = Customer.query.filter_by(active=True, is_deleted=False).all()
    return jsonify([{
        'id': customer.id,
        'name': customer.name,
        'phone': customer.phone
    } for customer in customers])

# Create a new customer
@app.route('/customers', methods=['POST'])
def add_customer():
    data = request.get_json()
    new_customer = Customer(
        name=data['name'],
        city=data['city'],
        age=data['age'],
        phone=data['phone']
    )
    db.session.add(new_customer)
    db.session.commit()
    return jsonify({'message': 'Customer added successfully'}), 201

# Mark a specific customer as deleted by ID
@app.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    customer.is_deleted = True
    db.session.commit()
    return jsonify({'message': 'Customer marked as deleted successfully'})
# end of customers crud

# loans crud

# Retrieve all loans

# get overdueloans
@app.route('/loans/overdue', methods=['GET'])
def get_overdue_loans():
    today = date.today()
    overdue_loans = Loan.query.filter(Loan.book_returned == False, Loan.returndate < today).all()
    return jsonify([{
        'loan_ID': loan.loan_ID,
        'loandate': loan.loandate,
        'returndate': loan.returndate,
        'book_returned': loan.book_returned,
        'customer_name': loan.customer.name,  # Include customer name
        'customer_phone': loan.customer.phone,  # Include customer phone
        'book_name': loan.book.book_name  # Include book name
    } for loan in overdue_loans])

@app.route('/loans/non-overdue', methods=['GET'])
def get_non_overdue_loans():
    today = date.today()
    loans = Loan.query.filter(Loan.returndate >= today, Loan.book_returned == False).all()
    return jsonify([{
        'loan_ID': loan.loan_ID,
        'loandate': loan.loandate,
        'returndate': loan.returndate,
        'book_returned': loan.book_returned,
        'customer_name': loan.customer.name,
        'customer_phone': loan.customer.phone,
        'book_name': loan.book.book_name
    } for loan in loans])


# Retrieve all loans
@app.route('/loans', methods=['POST'])
def add_loan():
    data = request.get_json()
    book = Book.query.get_or_404(data['book_id'])

    if not book.available:
        return jsonify({'error': 'Book is not available for loan'}), 400

    loandate = date.today()

    if book.type == 1:
        returndate = loandate + timedelta(days=10)
    elif book.type == 2:
        returndate = loandate + timedelta(days=5)
    elif book.type == 3:
        returndate = loandate + timedelta(days=2)
    else:
        returndate = None  # Default case if book type is not 1, 2, or 3

    new_loan = Loan(
        cust_id=data['cust_id'],
        book_id=data['book_id'],
        loandate=loandate,
        returndate=returndate,
        book_returned=False
    )
    book.available = False
    db.session.add(new_loan)
    db.session.commit()
    return jsonify({'message': 'Loan added successfully'}), 201

# Mark a specific loan as returned by ID
@app.route('/loans/return/<int:loan_id>', methods=['PUT'])
def return_book(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    loan.book_returned = True
    loan.returndate = date.today()
    book = Book.query.get_or_404(loan.book_id)
    book.available = True
    db.session.commit()
    return jsonify({'message': 'Book returned successfully'})

with app.app_context():
    db.create_all()
    defaultdata()

if __name__ == '__main__':
    app.run(debug=False ,use_reloader=False)