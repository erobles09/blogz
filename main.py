from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'ABCdefG1234567'

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    body = db.Column(db.String(120))
    
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        
        self.owner = owner

    def is_valid(self):
        if self.title and self.body:
            return True
        else:
            return False

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40))
    password = db.Column(db.String(40))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login','blog','home','signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('index.html',users=users)

@app.route('/newpost', methods=['POST', 'GET'])
def new_post():
    if request.method == 'POST':
        title = request.form['post_title']
        body = request.form['new_post']
        body_error=''
        title_error=''
        if title=="":
                title_error = "A title is required"
        if body=="":
                body_error = "A body is required"
        if title=="" or body=="":
            return render_template('newpost.html',title_error=title_error,body_error=body_error,title=title,body=body)
        else:
                owner = User.query.filter_by(username=session['username']).first()
                new_entry = Blog(title, body, owner)
                db.session.add(new_entry)
                db.session.commit()
                return redirect('/blog?id='+str(new_entry.id))
    else:
        return render_template('newpost.html')


@app.route('/blog', methods=['GET', 'POST'])
def blog():
    user = request.args.get('user')
    if user:
        blogs = Blog.query.filter_by(owner_id=user)
        return render_template('singleUser.html', blogs=blogs)
    solo_post = request.args.get("id")
    if solo_post:
        blog = Blog.query.get(solo_post)
        return render_template("singlepost.html", blog=blog)
    else:
        blogs = Blog.query.all()
        return render_template('blog.html', blogs=blogs, title=" My Blog Entries ")



@app.route('/login', methods=['post','get'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            return redirect('/newpost')
        if user and user.password != password:
            pword_error = "The password was incorrect"
            return render_template('login.html', pword_error=pword_error)
        if not user:
            user_error = "Incorrect username"
            return render_template('login.html', user_error=user_error)
    else:
        return render_template('login.html')

@app.route('/signup', methods=['post','get'])
def signup():
    user_error = ''
    pword_error = ''
    ver_error = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        if not val_input(username):
            user_error = "That does not seem to be a valid username"
        if not val_input(password):
            pword_error = "Invalid password"
        if password != verify:
            ver_error = "Passwords do not match"
        if user_error!='' or pword_error!='' or ver_error!='':
            return render_template('signup.html', username=username, user_error=user_error,pword_error=pword_error,ver_error=ver_error)
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            user_error = "That username already exists"
            return render_template('signup.html', user_error=user_error)
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')
    else:
        return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

def val_input(string):
    length = len(string)
    if length<20 and length>3:
        if " " not in string:
            return True
    else:
        return False



if __name__ == '__main__':
    app.run()