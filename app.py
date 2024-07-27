from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import configparser
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import psycopg2
from sqlalchemy_utils import database_exists, create_database


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

    #create a string
    def __repr__(self):
        return '<Name %r>' % self.name


# Create a Form Class

class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email Address", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
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
            user = Users(name=form.name.data,email=form.email.data,favorite_color=form.favorite_color.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        email = form.email.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
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
    app.debug = True
    app.run()