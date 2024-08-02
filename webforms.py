from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
import re

# create a login Form
class LoginForm(FlaskForm):
    username = StringField("User Name", validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

# create a BlogPosts Form

class BlogPostsForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = CKEditorField("Content", validators=[DataRequired()])
    author = StringField("Author")
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")

#
class UserNameCheck():
    def __init__(self, banned, regex, message=None):
        self.banned = banned
        self.regex = regex

        if not message:
            message = 'Please choose another username. Illegal characters found'
        self.message = message

    def __call__(self, form, field):
        p = re.compile(self.regex)
        if field.data.lower() in (word.lower() for word in self.banned):
            raise ValidationError(self.message)
        if re.search(p, field.data.lower()):
            raise ValidationError(self.message)
        

# Create a Form Class

class UserForm(FlaskForm):
    username = StringField("User Name", validators=[DataRequired(),
                                                    UserNameCheck(message="Reserved keywords & special characters not allowed",
                                                                 banned=['root', 'admin', 'sys', 'administrator'],
                                                                 regex="^(?=.*[-+!@#$%^&*., ?])"),
                                                    Length(min=2, max=20,message="username must be between 2 - 20 characters")])
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email Address", validators=[DataRequired()])
    about_author = TextAreaField("About Author")
    password_hash = PasswordField('Password', validators=[DataRequired(),EqualTo('password_hash2',message='Passwords must match')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")


class PasswordForm(FlaskForm):

    email = StringField("Email Address", validators=[DataRequired()])
    password_hash = PasswordField('Enter your Password', validators=[DataRequired()])
    submit = SubmitField("Submit")

#search form

class SearchForm(FlaskForm):
    search_term = StringField("Search term", validators=[DataRequired()])
    submit = SubmitField("Submit")


