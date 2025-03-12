from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from book_database import get_books, add_book
from flask_bcrypt import Bcrypt
import helper_functions
from load_books import add_new_books

# init
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secretkey'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# creates table to store login info
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

# creates table for saved books by user table
class saved_books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(20))
    isbn = db.Column(db.String(13))
    title = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Double)
    tags = db.Column(db.String(10))
    status = db.Column(db.String(10), nullable=False)


# creates table for for list of all books
class all_books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    pages = db.Column(db.Integer)
    year = db.Column(db.Integer)
    author = db.Column(db.String(30))
    isbn = db.Column(db.String(15))

with app.app_context():
    ## statement to reset table values and columns
    # saved_books.__table__.drop(db.engine)
    
    db.create_all()

    ## code to add new books from load_books.py file
    # new_books = add_new_books()
    # for book in new_books:
    #     add_this = all_books(title=book[0], pages=book[1], year=book[2],author=book[3],isbn=book[4])
    #     db.session.add(add_this)
    # db.session.commit()


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username=username.data).first()
        if existing_user_username:
            raise ValidationError("This username already exists")

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Login")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

##### Pages below

# home page
@app.route('/', methods=['GET', 'POST'])
def index():
    if current_user.is_authenticated:
        return render_template('index.html', username=current_user.username)
    return render_template('index.html')


# add books page
@app.route('/add', methods=['GET', 'POST'])
@login_required
def add_book():
    if request.method == 'POST':
        title = request.form.get('title')
        author = request.form.get('author')
        rating = request.form.get('rating')
        tags = request.form.get('tags')
        status = request.form.get('status')
        actual_book = db.session.query(all_books).filter(all_books.title.ilike(title)).first()
        if actual_book and helper_functions.compare_authors(actual_book.author, author) >= 0.8:
            isbn = actual_book.isbn
        else:
            isbn = None
        new_saved_book = saved_books(user=current_user.username, isbn=isbn, title=title, rating=rating, tags=tags, status=status)
        db.session.add(new_saved_book)
        db.session.commit()
        print("Added book")
        return render_template('add-books.html', result="success")
    return render_template('add-books.html')


# booklist page
@app.route('/booklist')
@login_required
def book_list():
    
    books = db.session.query(saved_books).filter_by(user=current_user.username)
    real_books = []
    for book in books:
        if book.isbn is not None:
            book_data = db.session.query(all_books).filter_by(isbn=book.isbn).first()
            real_books.append([book_data.title, book_data.author, book_data.pages, book_data.year, book_data.isbn, book.rating, book.tags, book.status])  

    return render_template('book-list.html', books=real_books)



### Begin authentication pages

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                # bcrypt.che
                login_user(user)
                return redirect(url_for('index'))
            else:
                print("Login failed")
                print(user.password)
                print(form.password.data)

    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

### End authentication pages


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000, debug=True)