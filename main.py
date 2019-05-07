from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "forflashmessages"

#add a blog class
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body):
        self.title = title
        self.body = body

#add a User class with the following properties: id, username, password, blogs
class User(db.Model):
    
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        #TODO check that user has a valid username and password
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
        else:
            #TODO - tell user they aren't in our database
            return "<h1>Duplicate User</h1>"
    
    
    return render_template('signup.html')




@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            # TODO - 'remember' that the user has logged in
            return redirect('/newpost')
        else:
            #say why login failed
            pass

    return render_template('login.html')




#@app.route('/index')




@app.route('/', methods=['POST', 'GET'])
def index():
    return redirect('/blog')

@app.route('/blog', methods=['GET', 'POST'])
def blog():
    post_id = request.args.get('id')
    if (post_id):
        post = Blog.query.get(post_id)
        return render_template('post_page.html', post = post)
    else:
        posts = Blog.query.all()
        return render_template("/blog.html", posts = posts)
    
   
@app.route('/newpost', methods=['GET', 'POST'])
def newpost():
    if request.method == 'POST':
        post_title = request.form['title']
        post_body = request.form['body']

#flash message for blank post title or body
        if len(post_title) == 0:
            flash("Title cannot be blank.")
        elif len(post_body) == 0:
            flash("Blog post cannot be blank.")
        else:
            new_post = Blog(post_title, post_body)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog?id={}'.format(new_post.id))

    return render_template('new_post.html')


if __name__ == '__main__':
    app.run()