  
from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:123@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

app.secret_key = '123abc123'
class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    body = db.Column(db.Text(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True)
    password = db.Column(db.String(25))
    blog = db.relationship('Blog', backref ='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/')
def index():
    blogs = Blog.query.all()
    return render_template('blog.html', title="Build a Blog!", blogs=blogs)

@app.route('/blog',methods=['POST','GET'])
def show_blog():

    if request.args:
        blog_id = request.args.get('id')
        blogs = Blog.query.filter_by(id=blog_id).all()
        return render_template('single_post.html', blogs=blogs)

    else:
        blogs = Blog.query.all()
        return render_template('blog.html', title="Build a Blog!", blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def create_new_post():

    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form ['body']
        owner = User.query.filter_by (username=session ['username']).first()
        new_blog = Blog(blog_title, blog_body, owner)

        title_error = ''
        body_error = ''
        if len(blog_title) == 0:
            title_error = "Please enter a title for your post."
        if len(blog_body) == 0:
            body_error = "Please enter text for your blog."

        if not title_error and not body_error:
            db.session.add(new_blog)
            db.session.commit()

            return redirect ("/blog?id=" + str(new_blog.id))

        else:
            blogs = Blog.query.all()
            return render_template('new_post.html', title="Build a Blog!", blogs=blogs,
                blog_title=blog_title, title_error=title_error, 
                blog_body=blog_body, body_error=body_error)

    if request.method == 'GET':
        return render_template ('new_post.html', title = "New blog entry")

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username = username).first()
        if user and user.password == password:
            session['username'] = username
            flash("Logged in")
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
   if request.method == 'POST':
       username = request.form['username']
       password = request.form['password']
       verify = request.form['verify']
       existing_user = User.query.filter_by(username=username).first()
       
       if not username and not password and not verify:
           flash("All fields must be complete")
       elif existing_user:
           flash("User already exists")
       elif password != verify:
           flash("Passwords do not match")
       elif len(password) < 3 or len(password) > 20:
           flash("Password must be between 3 and 20 characters")
       elif len(username) < 3 or len(username) > 20:
           flash("Password must be between 3 and 20 characters")
       elif not existing_user:
           new_user = User(username, password)
           db.session.add(new_user)
           db.session.commit()
           session['username'] = username
           return redirect('/newpost')
   return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    flash('You are logged out', 'success')
    return redirect('/blog')
    
if __name__ == '__main__':
    app.run()           