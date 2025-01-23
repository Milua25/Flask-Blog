from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.simple import EmailField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from wtforms.widgets import TextArea


# Form Class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    username = StringField("Username", validators=[DataRequired()])
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
    title = StringField("Title", validators=[DataRequired()])
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("SlugField", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()], widget=TextArea())
    submit = SubmitField("submit")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("submit")