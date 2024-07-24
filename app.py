from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import configparser

config = configparser.ConfigParser()
config.read('secretKey.ini')

#create flask app instance
app = Flask(__name__)
app.config['SECRET_KEY'] = config['DEFAULT']['SecretKey']

# Create a Form Class

class UserForm(FlaskForm):
    name = StringField("Kindly input your name", validators=[DataRequired()])
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

#create namepage
@app.route('/name',methods=['GET','POST'])

def name():
    name = None
    form = UserForm()
    # validate form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''

    return render_template("name.html",name=name,form=form)


# create custom error pages

#invalid url 
@app.errorhandler(404)

def page_not_found(err):
    return render_template("404.html"),404

@app.errorhandler(500)

def page_not_found(err):
    return render_template("500.html"),500

















































































