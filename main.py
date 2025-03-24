from flask import Flask, render_template, redirect, url_for, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError, Email
from book_database import get_books, add_book
from flask_bcrypt import Bcrypt
from utility import reset_table, compare_authors
from load_books import add_new_books
import datetime




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
    email = db.Column(db.String(20), nullable=False, unique=True)
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
    

reset_table(saved_books, db=db, app=app)

# add_new_books(all_books, db=db, app=app)

class RegisterForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Length(min=4, max=20), Email()], render_kw={"placeholder": "Email", "type":"email"})

    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Register")

    def validate_email(self, email):
        existing_user_email = User.query.filter_by(email=email.data).first()
        if existing_user_email:

            raise ValidationError("This email already exists")

class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Length(min=4, max=20), Email()], render_kw={"placeholder": "Email", "type":"email"})

    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField("Login")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

###########################
# TO-DO:
# use JS to edit/delete books from library (maybe move "add books" to top of library page)
# ADD ABILITY TO LIST ALL BOOKS ON MAIN "ALL BOOKS" PAGE
# IMPLEMENT ABILITY TO SEARCH BOOKS AND POPULATE USING JS TO SELECT
# make text boxes wrap around
# TO-FIX:
#        
#############################


##### Pages below

# home page
@app.route('/', methods=['GET', 'POST'])
def index():

    if current_user.is_authenticated:
        # column = request.args.get('email')
        query = request.args.get('q')

        if query:
            results = User.query.filter(User.email.like(f"%{query}%")).all()
        else:
            results = ['results works', 'but your code doesn\'t!']


        return render_template('index.html', email=current_user.email, results=results)
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
        if actual_book and compare_authors(actual_book.author, author) >= 0.8:
            isbn = actual_book.isbn
        else:
            isbn = None
        new_saved_book = saved_books(user=current_user.email, isbn=isbn, title=title, rating=rating, tags=tags, status=status)
        db.session.add(new_saved_book)
        db.session.commit()
        print("Added book")
    
        return render_template('add-books.html', result="success", email=current_user.email)
    return render_template('add-books.html', email=current_user.email)



# my library page
@app.route('/my-library')
@login_required
def book_list():

    sort_by = ''

    # how do I sort by a category selected by user without 
    # 1. using f' string concat
    # 2. using an if statement for EVERY cat.


    real_books = (
        db.session.query(
            all_books.title,
            all_books.author,
            all_books.pages,
            all_books.year,
            all_books.isbn,
            saved_books.rating,
            saved_books.tags,
            saved_books.status,
            saved_books.id
        )
        .join(saved_books, all_books.isbn == saved_books.isbn)
        .filter(saved_books.user == current_user.email)
        .order_by(saved_books.id)
        .all()
    )
    return render_template('book-list.html', books=real_books, email=current_user.email)

@app.route('/my-library/modify-tag', methods=['POST'])
def modify_tag():
    req = request.get_json()

    print(req)

    id = req.get('id')
    new_tag = req.get('tag')
    

    book = db.session.execute(db.select(saved_books).filter_by(id=id)).scalar_one()
    book.tags = new_tag
    db.session.commit()
    
    res = make_response(jsonify(req), 200)

    return res





### Begin authentication pages

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
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
        new_user = User(email=form.email.data, password=hashed_password)
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
