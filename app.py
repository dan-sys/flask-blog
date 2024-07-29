from flask import Flask, render_template, flash, request, redirect, url_for
import configparser
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import psycopg2
from sqlalchemy_utils import database_exists, create_database
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from webforms import UserForm, LoginForm, BlogPostsForm, PasswordForm



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
#set up login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login_fcn'


# create the data model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(25),nullable=False, unique=True)
    name = db.Column(db.String(100),nullable=False)
    email = db.Column(db.String(100),nullable=False, unique=True)
    date_added = db.Column(db.DateTime, default=datetime.now())
    # password hash in db
    password_hash = db.Column(db.String(500))
    # user can have many posts
    posts = db.relationship('BlogPosts', backref='poster_info')
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
     #author = db.Column(db.String(250))
     date_posted = db.Column(db.DateTime, default=datetime.now())
     slug = db.Column(db.String(250))
     #create a foreign key to link to users db
     author_id = db.Column(db.Integer, db.ForeignKey('users.id'))


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

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

#create login fcn
@app.route('/login',methods=['GET','POST'])

def login_fcn():
    form = LoginForm()

    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        # check if user password matches the hash in the db
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Logged in successfully")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong password - hermano. Try again")
        else:
            flash("User does/may not exist. Try again")
    return render_template('login.html',form=form)

#create dashboard fcn
@app.route('/dashboard',methods=['GET','POST'])
@login_required

def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)

    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.username = request.form['username']
        try:
            db.session.commit()
            flash("User information updated successfully!!!")
            return render_template("dashboard.html",
                                   form=form,
                                   name_to_update=name_to_update,
                                   id=id)
        except:
            flash("Something went wrong, its not your fault, its MINE!!!")
            return render_template("dashboard.html",
                                   form=form,
                                   name_to_update=name_to_update,
                                   id=id)
    else:
        return render_template("dashboard.html",
                                   form=form,
                                   name_to_update=name_to_update,
                                   id=id)


@app.route('/logout',methods=['GET','POST'])
@login_required

def logout():
    logout_user()
    flash("You have been logged Out of here bro! Go and warm eba")
    return redirect(url_for('login_fcn'))


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
            user = Users(username=form.username.data,name=form.name.data,email=form.email.data, password_hash=hash_pw)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.username.data = ''
        form.name.data = ''
        form.email.data = ''
        form.password_hash = ''
        #create flash message
        flash("User added Successfully. Congrats")
    list_users = Users.query.order_by(Users.date_added)

    return render_template("add_user.html",form=form,
                           name=name, 
                           list_users=list_users)

# update a database user record
@app.route('/update/<int:id>', methods=['GET','POST'])
@login_required
def update_user(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)

    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.username = request.form['username']
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
@login_required
def add_post():
    form = BlogPostsForm()

    if form.validate_on_submit():
        poster = current_user.id
        post = BlogPosts(title=form.title.data, content=form.content.data, author_id=poster, slug=form.slug.data)
        form.title.data = ''
        form.content.data = ''
        form.slug.data = ''

        #add data to database table
        db.session.add(post)
        db.session.commit()
        flash("Blog Post submitted successfully!!!")
    # redirected to webpage
    return render_template("add_blogpost.html",
                           form=form)

@app.route('/posts')
def show_posts():
    # query db to get blog posts from Database table
    #we are quering the model -- note this
    posts = BlogPosts.query.order_by(BlogPosts.date_posted)
    return render_template("posts.html",
                           posts=posts)

@app.route('/posts/<int:id>')
def show_single_post(id):
    post = BlogPosts.query.get_or_404(id)
    return render_template('single_post.html',post=post)


@app.route('/posts/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit_post(id):
    post_to_edit = BlogPosts.query.get_or_404(id)
    form = BlogPostsForm()

    if form.validate_on_submit():
        post_to_edit.title = form.title.data
        post_to_edit.slug = form.slug.data
        post_to_edit.content = form.content.data

        #update db with newly modified post
        db.session.add(post_to_edit)
        db.session.commit()
        flash("Post has been updated")
        return redirect(url_for('show_single_post',id=post_to_edit.id))

    form.title.data = post_to_edit.title
    form.slug.data = post_to_edit.slug
    form.content.data = post_to_edit.content
    return render_template('edit_post.html',form=form)


@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = BlogPosts.query.get_or_404(id)

    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash("Blog Post deleted successfully")
        posts = BlogPosts.query.order_by(BlogPosts.date_posted)
        return render_template("posts.html",
                           posts=posts)
    except:
        flash("Problem occured when deleting Blog Post")
        posts = BlogPosts.query.order_by(BlogPosts.date_posted)
        return render_template("posts.html",
                           posts=posts)



# to return JSON
#@app.route('/api')
#def get_sampleJSON():
#    #just prepare a dictionary and flask will jsonify it
#    return {"id": 568459,
#            "user": "User Primo",
#            }


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