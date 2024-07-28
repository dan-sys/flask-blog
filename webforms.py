from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea

# create a login Form
class LoginForm(FlaskForm):
    username = StringField("User Name", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

# create a BlogPosts Form

class BlogPostsForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a Form Class

class UserForm(FlaskForm):
    username = StringField("User Name", validators=[DataRequired()])
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email Address", validators=[DataRequired()])
    password_hash = PasswordField('Password', validators=[DataRequired(),EqualTo('password_hash2',message='Passwords must match')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")


class PasswordForm(FlaskForm):

    email = StringField("Email Address", validators=[DataRequired()])
    password_hash = PasswordField('Enter your Password', validators=[DataRequired()])
    submit = SubmitField("Submit")