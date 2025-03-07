from flask import Flask, render_template, request, redirect, url_for
from data_models import db, Author, Book
import os
from datetime import datetime
from sqlalchemy import func

app = Flask(__name__)

# Absolute path to the database file
db_path = os.path.join(os.path.dirname(__file__), 'data', 'library.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'  # Use an absolute path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Ensure the 'data' directory exists
DATA_DIR = os.path.join(app.root_path, 'data')
os.makedirs(DATA_DIR, exist_ok=True)

app.config['SECRET_KEY'] = 'your_secret_key'  # Required for Flask-WTF (CSRF protection)
db.init_app(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()

    # Seed Data (Only if tables are empty)
    if not Author.query.first():  # Check if authors table is empty
        author1 = Author(name="Jane Austen", birth_date=datetime(1775, 12, 16).date(), date_of_death=datetime(1817, 7, 18).date())
        author2 = Author(name="Charles Dickens", birth_date=datetime(1812, 2, 7).date(), date_of_death=datetime(1870, 6, 9).date())
        author3 = Author(name="Agatha Christie", birth_date=datetime(1890, 9, 15).date(), date_of_death=datetime(1976, 1, 12).date())
        author4 = Author(name="J.R.R. Tolkien", birth_date=datetime(1892, 1, 3).date(), date_of_death=datetime(1973, 9, 2).date())
        author5 = Author(name="George Orwell", birth_date=datetime(1903, 6, 25).date(), date_of_death=datetime(1950, 1, 21).date())
        author6 = Author(name="Virginia Woolf", birth_date=datetime(1882, 1, 25).date(), date_of_death=datetime(1941, 3, 28).date())
        author7 = Author(name="Leo Tolstoy", birth_date=datetime(1828, 9, 9).date(), date_of_death=datetime(1910, 11, 20).date())

        db.session.add_all([author1, author2, author3, author4, author5, author6, author7])
        db.session.commit() # Commit authors before using them

        book1 = Book(isbn="9780141439518", title="Pride and Prejudice", publication_year=1813, author_id=author1.id)
        book2 = Book(isbn="9780141439624", title="Oliver Twist", publication_year=1838, author_id=author2.id)
        book3 = Book(isbn="9780007880318", title="Murder on the Orient Express", publication_year=1934, author_id=author3.id)
        book4 = Book(isbn="9780547928227", title="The Hobbit", publication_year=1937, author_id=author4.id)
        book5 = Book(isbn="9780451524935", title="1984", publication_year=1949, author_id=author5.id)
        book6 = Book(isbn="9780156027604", title="Mrs. Dalloway", publication_year=1925, author_id=author6.id)
        book7 = Book(isbn="9780140449174", title="War and Peace", publication_year=1869, author_id=author7.id)
        book8 = Book(isbn="9780743273565", title="The Great Gatsby", publication_year=1925, author_id=author7.id)
        book9 = Book(isbn="9780451526533", title="Animal Farm", publication_year=1945, author_id=author5.id)
        book10 = Book(isbn="9780061122415", title="To Kill a Mockingbird", publication_year=1960, author_id=author1.id)

        db.session.add_all([book1, book2, book3, book4, book5, book6, book7, book8, book9, book10])
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
def home():
    sort_by = request.args.get('sort_by', 'title')
    search_term = request.form.get('search_term', '')  # Get search term from form
    message = request.args.get('message', None) # Get message from redirect

    books = Book.query  # Start with the base query

    if search_term:
        # Perform the search (case-insensitive)
        books = books.filter(func.lower(Book.title).contains(func.lower(search_term)))
        if not books.all():  # Check if any books are found after filtering
            message = "No books found matching your search criteria."
    else:
        message = None  # Clear the message, there isn't a search.

    if sort_by == 'title':
        books = books.order_by(Book.title)
    elif sort_by == 'author':
        books = books.join(Author).order_by(Author.name)

    books = books.all()  # Finally, execute the query

    return render_template('home.html', books=books, search_term=search_term, message=message)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    message = None  # Initialize message variable
    if request.method == 'POST':
        name = request.form['name']
        birthdate_str = request.form['birthdate']  # Corrected field name
        date_of_death_str = request.form['date_of_death']

        try:
            birthdate = datetime.strptime(birthdate_str, '%Y-%m-%d').date()  # Corrected variable name
            date_of_death = datetime.strptime(date_of_death_str, '%Y-%m-%d').date() if date_of_death_str else None
            new_author = Author(name=name, birth_date=birthdate, date_of_death=date_of_death) # Corrected variable name
            db.session.add(new_author)
            db.session.commit()
            message = "Author added successfully!"  # Set success message
        except ValueError:
             message = "Invalid date format.  Please use YYYY-MM-DD."
        except Exception as e:
            db.session.rollback()
            message = f"Error adding author: {e}"

    return render_template('add_author.html', message=message)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    message = None
    authors = Author.query.all()

    if request.method == 'POST':
        isbn = request.form['isbn']
        title = request.form['title']
        publication_year = request.form['publication_year']
        author_id = request.form['author_id']

        try:
            publication_year = int(publication_year)
            author_id = int(author_id)
            new_book = Book(isbn=isbn, title=title, publication_year=publication_year, author_id=author_id)
            db.session.add(new_book)
            db.session.commit()
            message = "Book added successfully!"
        except ValueError:
            message = "Invalid publication year. Please enter a number."
        except Exception as e:
            db.session.rollback()
            message = f"Error adding book: {e}"

    return render_template('add_book.html', authors=authors, message=message)

@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    book = db.session.get(Book, book_id)  # Use db.session.get
    if not book:
        return "Book not found"  # Or handle the error appropriately

    author_id = book.author_id  # Get author_id *before* deleting the book

    try:
        db.session.delete(book)
        db.session.commit()
        message = "Book deleted successfully!"

        # Check if the author has any other books
        other_books = Book.query.filter_by(author_id=author_id).first()
        if not other_books: # No other books by this author
            author = db.session.get(Author, author_id) # Load author object
            if author: # Double check that it exists.
                db.session.delete(author)
                db.session.commit()
                message += " Author also deleted as they have no more books!"
        return redirect(url_for('home', message=message)) # Pass the message through URL
    except Exception as e:
        db.session.rollback()
        return f"Error deleting book: {e}" # Or handle the error appropriately.


if __name__ == '__main__':
    app.run(debug=True,host="0.0.0.0",port=5002)

