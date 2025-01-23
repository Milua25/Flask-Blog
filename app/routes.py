from flask import Flask, render_template, request, flash, url_for
from werkzeug.utils import redirect
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import  login_required, login_user, logout_user
from app.forms import PasswordForm, UserForm,PostForm, LoginForm
from app.models import Posts, Users
from app import db

def register_routes(app, login_manager):
    @login_manager.user_loader
    def load_user(user_id):
        return db.get_or_404(Users, user_id)

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
                    username=user_form.username.data,
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
            user_form.username.data = ""
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
    @login_required
    def add_post():
        form = PostForm()
        if request.method == "POST" and form.validate_on_submit():
            post = Posts(
                title=form.title.data,
                content=form.content.data,
                author=form.author.data,
                slug=form.slug.data,
            )
            form.title.data = ""
            form.content.data = ""
            form.author.data = ""
            form.slug.data = ""

            # Add post data to db
            db.session.add(post)
            db.session.commit()
            flash("Post Submitted Successfully!")

            # Redirect
        return render_template("add_post.html", form=form)

    # Get Post page
    @app.route("/posts")
    def posts():
        all_posts = Posts.query.order_by(Posts.date_posted).all()
        print(all_posts)
        return render_template("posts.html", posts=all_posts)

    # Get Individual page
    @app.route("/posts/<int:id>")
    def get_post(id):
        post = Posts.query.get_or_404(id)
        return render_template("post.html", post=post)

    @app.route("/post/edit/<int:id>", methods=["GET", "POST"])
    def edit_post(id):
        post = Posts.query.get_or_404(id)
        post_form = PostForm()
        if post_form.validate_on_submit() and request.method == "POST":
            post.title = post_form.title.data
            post.author = post_form.author.data
            post.content = post_form.content.data
            post.slug = post_form.slug.data
            # Add to database
            db.session.add(post)
            db.session.commit()
            flash("Post has been updated!`")
            return redirect(url_for("get_post", id=post.id))
        post_form.title.data = post.title
        post_form.author.data = post.author
        post_form.content.data = post.content
        post_form.slug.data = post.slug
        return render_template("edit_post.html", form=post_form)

    # Delete Post
    @app.route("/post/delete/<int:id>")
    def delete_post(id):
        post_to_delete = Posts.query.get_or_404(id)
        db.session.delete(post_to_delete)
        db.session.commit()
        flash("Blog Post was deleted!!!")
        return redirect(url_for("posts"))

    # Create Login Page
    @app.route("/login", methods=["GET", "POST"])
    def login():
        form = LoginForm()
        if form.validate_on_submit():
            user = Users.query.filter_by(username=form.username.data).first()
            if user:
                if check_password_hash(user.password_hash, form.password.data):
                    login_user(user)
                    return redirect(url_for("dashboard"))
                else:
                    flash("Wrong Password inputted!!!", "error")
            else:
                flash("Username does not exist!!!")
        return render_template("login.html", form=form)

    # Create Dashboard Page
    @app.route("/dashboard", methods=["GET"])
    @login_required
    def dashboard():
        return render_template("dashboard.html")

    # Logout User
    @app.route("/logout", methods=["GET", "POST"])
    @login_required
    def logout():
        logout_user()
        flash("You have been loggedout!!!")
        return redirect(url_for("login"))

    # Create Custom Error pages
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    # Internal server error
    @app.errorhandler(500)
    def page_not_found(e):
        return render_template("500.html"), 500

