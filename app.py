from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import configparser
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime



config = configparser.ConfigParser()
config.read('secretKey.ini')

#create flask app instance
app = Flask(__name__)

# add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
#add secret key for csrf
app.config['SECRET_KEY'] = config['DEFAULT']['SecretKey']

# initialize database
db = SQLAlchemy(app)

# create the data model
class Users(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(100),nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.now())

    #create a string
    def __repr__(self):
        return '<Name %r>' % self.name


# Create a Form Class

class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email Address", validators=[DataRequired()])
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
            user = Users(name=form.name.data,email=form.email.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        email = form.email.data
        form.name.data = ''
        form.email.data = ''
        #create flash message
        flash("User added Successfully. Congrats")
    list_users = Users.query.order_by(Users.date_added)

    return render_template("add_user.html",form=form,
                           name=name, 
                           list_users=list_users)

#create namepage
#this is to be deleted
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

















































































