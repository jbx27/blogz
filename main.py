from flask import Flask, request, redirect, render_template, flash, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "totallysecuresessionkey"

#add a blog class
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

#add a User class with the following properties: id, username, password, blogs
class User(db.Model):
    
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()

        if username == "" or password == "" or verify == "":
            flash("Please enter a valid username and password")
            return redirect ('/signup')
        elif len(username) <3 or len(password) < 3:
            flash("Invalid username or password. Please enter a username and password that has at least 3 characters long.")
            return redirect ('/signup')
        elif password != verify:
            flash("Password and verify do not match.")
            return redirect ('/signup')
        elif existing_user:
            flash("Username taken, please choose another Username")
            return redirect('/signup')

        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            #remember user
            session['username'] = username
            return redirect('/newpost')    
    
    return render_template('signup.html')


@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')
        #TODO - figure out why newpost is still being allowed

@app.route('/logout')
def logout():
    del session['username']
    flash("Succesfully Logged Out.")
    return redirect('/blog')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            #'remember' that the user has logged in
            session['username'] = username
            flash("Successfully Logged in")
            return redirect('/newpost')
        else:
            # tell the user why the login failed
            flash('User password incorrect or user does not exist')
    return render_template('login.html')


@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)

@app.route('/blog', methods=['GET', 'POST'])
def blog():


    post_id = request.args.get('id')
    user_id = request.args.get('user')
    if user_id:
        user = User.query.get(user_id)
        user_posts = Blog.query.filter_by(owner_id = user_id).all()
        return render_template('singleUser.html', user = user, user_posts = user_posts)
    if post_id:   
        post = Blog.query.get(post_id)
        user = User.query.get(post.owner_id)
        return render_template('post_page.html', post = post, user = user )
    else:
        posts = Blog.query.all()
        return render_template('blog.html', posts = posts)
    
   
@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if request.method == 'POST':
        post_title = request.form['title']
        post_body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()

#flash message for blank post title or body
        if len(post_title) == 0:
            flash("Title cannot be blank.")
        elif len(post_body) == 0:
            flash("Blog post cannot be blank.")
        else:
            new_post = Blog(post_title, post_body, owner)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog?id={}'.format(new_post.id))

    return render_template('new_post.html')


if __name__ == '__main__':
    app.run()