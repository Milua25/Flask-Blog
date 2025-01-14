import os
from flask import Flask, render_template, request, flash, url_for
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import StringField, SubmitField
from wtforms.fields.simple import EmailField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from load_dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import String, Text, Integer, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea
from sqlalchemy.schema import FetchedValue

# Load environment variables
load_dotenv()


# Form Class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8),
                                                     EqualTo("password_2", message="Password must match")])
    password_2 = PasswordField("Confirm Password", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    submit = SubmitField("submit")

class PasswordForm(FlaskForm):
    email = EmailField("What's your Email?", validators=[DataRequired(), Email()])
    password = PasswordField("What's your Password? ", validators=[DataRequired()])
    submit = SubmitField("submit")

class PostForm(FlaskForm):
    title =StringField("Title", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("SlugField", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()], widget=TextArea())
    submit = SubmitField("submit")



# Create a flask instance
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"


# Initialize the Database
class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)

class Users(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False, unique=True)
    favorite_color: Mapped[str] = mapped_column(String(100), nullable=True)
    password_hash: Mapped[str] = mapped_column(String(250), nullable=False)
    date_added: Mapped[datetime] = mapped_column(nullable=False, default=datetime.now())

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # create string
    def __repr__(self):
        return "<Name %r>" % self.name

class Posts(db.Model):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    author: Mapped[str] = mapped_column(String(255))
    date_posted: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
#    date_updated: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    slug: Mapped[str] = mapped_column(String(255))

    # create string
    def __repr__(self):
        return "<Title %r>" % self.title


migrate = Migrate()
migrate.init_app(app, db)


# with app.app_context():
#     db.create_all()

# Initialize the bootstrap
bootstrap = Bootstrap5()
bootstrap.init_app(app)


# Create a route decorator
@app.route("/")
def home():
    stuff = "This is <strong>Bold</strong> Text"
    fav_pizza_menu = ["Ham", "Cheese", "Onions"]
    return render_template("index.html", stuff=stuff, fav_pizza_menu=fav_pizza_menu)


@app.route("/user/<name>")
def user(name):
    return render_template("user.html", user=name)


# Create a Name Page
@app.route("/name", methods=["GET", "POST"])
def name():
    name = None
    user_form = UserForm()
    # Validate Form
    if request.method == "POST" and user_form.validate_on_submit():
        name = user_form.name.data
        user_form.name.data = ""
        flash("Form Submitted Successfully", "info")
    return render_template("name.html", name=name, form=user_form)


# Create Password test Page
@app.route("/test_pw", methods=["GET", "POST"])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    password_form = PasswordForm()
    # Validate Form
    if request.method == "POST" and password_form.validate_on_submit():
        email = password_form.email.data
        password = password_form.password.data
        password_form.email.data = ""
        password_form.password.data = ""

        pw_to_check = Users.query.filter_by(email=email).first()
        if pw_to_check is None:
            return render_template("test_pw.html", email=email, password=password, form=password_form,
                                   pw_to_check=pw_to_check)
        # Check Hashed Password
        passed = check_password_hash(pw_to_check.password_hash, password)
        print(passed, pw_to_check, email)
    return render_template("test_pw.html", email=email, password=password, form=password_form, passed=passed,
                           pw_to_check=pw_to_check)


# Create User Page
@app.route("/user/add", methods=["GET", "POST"])
def add_user():
    name = None
    user_form = UserForm()
    our_users = Users.query.order_by(Users.date_added).all()
    # Validate Form
    if request.method == "POST" and user_form.validate_on_submit():
        user = Users.query.filter_by(email=user_form.email.data).first()
        print(user)
        if user is None:
            new_user = Users(
                name=user_form.name.data,
                email=user_form.email.data,
                password_hash=generate_password_hash(user_form.password.data, method="pbkdf2"),
                favorite_color=user_form.favorite_color.data
            )
            print(new_user)
            db.session.add(new_user)
            db.session.commit()
            flash("Form Submitted Successfully", "info")
        else:
            flash("User email already exist!!", "error")
        user_form.name.data = ""
        user_form.email.data = ""
        user_form.favorite_color.data = ""
        user_form.password.data = ""
        return render_template("add_user.html", name=name, form=user_form, our_users=our_users)
    name = user_form.name.data
    return render_template("add_user.html", name=name, form=user_form, our_users=our_users)


# Update Database Record
@app.route("/update/<int:id>", methods=["GET", "POST"])
def update_user(id):
    user_form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST" and user_form.validate_on_submit():
        name_to_update.name = user_form.name.data
        name_to_update.email = user_form.email.data
        name_to_update.favorite_color = user_form.favorite_color.data
        try:
            db.session.commit()
            flash("User updated successfully!")
            return render_template("update.html", form=user_form, name_to_update=name_to_update)
        except IntegrityError:
            flash("Error! Try again")
            return render_template("update.html", form=user_form, name_to_update=name_to_update)
    else:
        user_form.name.data = name_to_update.name
        user_form.email.data = name_to_update.email
        return render_template("update.html", form=user_form, name_to_update=name_to_update)


# Delete user from database
@app.route("/delete/<int:id>", methods=["GET", "POST"])
def delete_user(id):
    user_to_delete = Users.query.get_or_404(id)
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!!!")
        return redirect(url_for("add_user"))
    except:
        flash("Failed deleting user!!!")
        return redirect(url_for("add_user"))


# Add Post page
@app.route("/add/post", methods=["GET", "POST"])
def add_post():
    form = PostForm()
    if request.method == "POST" and form.validate_on_submit():
        post  = Posts(
            title = form.title.data,
            content = form.content.data,
            author = form.author.data,
            slug = form.slug.data,
        )
        form.title.data = ""
        form.content.data = ""
        form.author.data = ""
        form.slug.data = ""

        # Add post data to db
        db.session.add(post)
        db.session.commit()
        flash("Post Submitted Successfully!")

        #Redirect
    return render_template("add_post.html", form=form)

# Get Post page
@app.route("/posts")
def posts():
    all_posts =  Posts.query.order_by(Posts.date_posted).all()
    print(all_posts)
    return render_template("posts.html", posts=all_posts)



# Get Individual page
@app.route("/posts/<int:id>")
def get_post(id):
    post =  Posts.query.get_or_404(id)
    return render_template("post.html", post=post)



# Create Custom Error pages
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Internal server error
@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)
