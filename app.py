from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
import configparser
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import psycopg2
from sqlalchemy_utils import database_exists, create_database
from werkzeug.security import generate_password_hash, check_password_hash




config = configparser.ConfigParser()
config.read('secretKey.ini')

#create flask app instance
app = Flask(__name__)

# add Database
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db' 
app.config['SQLALCHEMY_DATABASE_URI'] = config['DEFAULT']['DB_URL']
#add secret key for csrf
app.config['SECRET_KEY'] = config['DEFAULT']['SecretKey']

# initialize database
db = SQLAlchemy(app)

migrate = Migrate(app,db)


# create the data model
class Users(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(100),nullable=False, unique=True)
    favorite_color = db.Column(db.String(50))
    date_added = db.Column(db.DateTime, default=datetime.now())
    # password hash in db
    password_hash = db.Column(db.String(500))
    #create a property for the passwords
    @property
    def user_password(self):
        raise AttributeError('Password is not a readable atrribute!!!')
    
    @user_password.setter
    def user_password(self, user_password):
        self.password_hash = generate_password_hash(user_password)

    def verify_password(self, user_password):
        return check_password_hash(self.password_hash, user_password)
    

    #create a string
    def __repr__(self):
        return '<Name %r>' % self.name


#create a blog post model
class BlogPosts(db.Model):
     
     id = db.Column(db.Integer,primary_key=True)
     title = db.Column(db.String(250))
     content = db.Column(db.Text)
     author = db.Column(db.String(250))
     date_posted = db.Column(db.DateTime, default=datetime.now())
     slug = db.Column(db.String(250))

# create a BlogPosts Form

class BlogPostsForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")




# Create a Form Class

class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email Address", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    password_hash = PasswordField('Password', validators=[DataRequired(),EqualTo('password_hash2',message='Passwords must match')])
    password_hash2 = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField("Submit")



class PasswordForm(FlaskForm):

    email = StringField("Email Address", validators=[DataRequired()])
    password_hash = PasswordField('Enter your Password', validators=[DataRequired()])

    submit = SubmitField("Submit")

class UserUpdateForm(FlaskForm):
    previous_name = StringField("Previous Name", validators=[DataRequired()])
    new_name = StringField("New Name", validators=[DataRequired()])
    #email = StringField("Email Address", validators=[DataRequired()])
    submit = SubmitField("Submit")

#create a route decorator
@app.route('/')

def index():
    first_name = "Dominus"
    stuff = "this is a bold text"
    fav_piazza = ["Romana","Galiani","Pax",560]
    return render_template("index.html",
                           first_name=first_name, 
                           stuff=stuff,
                           fav_piazza=fav_piazza)

# localhost:5000/user/Chronus
@app.route('/user/<name>')

def user(name):
    return render_template("user.html",user_name=name)


@app.route('/user/add',methods=['GET','POST'])

def add_user():
    name = None
    form = UserForm()
    # validate form
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # hash password before passing it to db
            hash_pw = generate_password_hash(form.password_hash.data, method='scrypt')
            user = Users(name=form.name.data,email=form.email.data,favorite_color=form.favorite_color.data, password_hash=hash_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash = ''
        #create flash message
        flash("User added Successfully. Congrats")
    list_users = Users.query.order_by(Users.date_added)

    return render_template("add_user.html",form=form,
                           name=name, 
                           list_users=list_users)

# update a database record
@app.route('/update/<int:id>', methods=['GET','POST'])

def update_user(id):
    form = UserUpdateForm()

    name_to_update = Users.query.get_or_404(id)

    if request.method == 'POST':
        name_to_update.name = request.form['new_name']
        try:
            db.session.commit()
            flash("User information updated successfully!!!")
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update,
                                   id=id)
        except:
            flash("Something went wrong, its not your fault, its MINE!!!")
            return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update,
                                   id=id)
    else:
        return render_template("update.html",
                                   form=form,
                                   name_to_update=name_to_update,
                                   id=id)
    
@app.route('/delete/<int:id>')

def delete_user(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully")

        list_users = Users.query.order_by(Users.date_added)
        return render_template("add_user.html",
                               form=form,
                               name=name,
                               list_users=list_users)
    except:
        flash("Wooah User refused to be deleted Successfully")
        return render_template("add_user.html",
                               form=form,
                               name=name,
                               list_users=list_users)


@app.route('/test_pw',methods=['GET','POST'])

def test_pw():

    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()

    # validate form
    if form.validate_on_submit():
        email = form.email.data
        password= form.password_hash.data
        #clear the form
        form.email.data = ''
        form.password_hash = ''

        #look up users by email address
        pw_to_check = Users.query.filter_by(email=email).first()

        #check hashed passwords
        passed = check_password_hash(pw_to_check.password_hash, password)


    return render_template("test_pw.html",
                           email=email,
                           password=password,
                           pw_to_check=pw_to_check,
                           passed=passed,
                           form=form)

# Add a blogpost page
@app.route('/add-post',methods=['GET','POST'])

def add_post():
    form = BlogPostsForm()

    if form.validate_on_submit():
        post = BlogPosts(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''

        #add data to database table
        db.session.add(post)
        db.session.commit()
        flash("Blog Post submitted successfully!!!")
    # redirected to webpage
    return render_template("add_blogpost.html",
                           form=form)
# to return JSON
#@app.route('/api')
#def get_sampleJSON():
#    #just prepare a dictionary and flask will jsonify it
#    return {"id": 568459,
#            "user": "User Primo",
#            }


#create namepage
#this is to be deleted later
@app.route('/name',methods=['GET','POST'])

def name():

    name = None
    form = UserForm()
    # validate form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        #create flash message
        flash("Form submitted Successfully. Congrats")

    return render_template("name.html",
                           name=name,
                           form=form)


# create custom error pages

#invalid url 
@app.errorhandler(404)

def page_not_found(err):
    return render_template("404.html"),404

@app.errorhandler(500)

def page_not_found(err):
    return render_template("500.html"),500

@app.cli.command('createdb')
def createdb_command():
    """Creates the database + tables."""

    if not database_exists(config['DEFAULT']['DB_URL']):
        print('Creating database.')
        create_database(config['DEFAULT']['DB_URL'])
    print('Creating tables.')
    db.create_all()
    print('Tables created!')






































































if __name__ == "__main__":
    app.run(debug = False)