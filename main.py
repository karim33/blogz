from flask import Flask, request, redirect, render_template, session
from flask_sqlalchemy import SQLAlchemy
# colab with Osman Abate

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz123@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'abu123hayat'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    content = db.Column(db.String(1000))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))


    def __init__(self, title, content, owner):
        self.title = title
        self.content = content
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    posts = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':

        user_email=request.form['email']
        password=request.form['password']

        verify_user = User.query.filter_by(email=user_email).first()

        if verify_user != None and verify_user.password == password: # verify_user.password retrieves the password word in out database and we compare it to password from user
            session['email']= user_email
            return redirect('/')
        else:
            #TODO - explain why login failed
            pass

    return render_template('login.html')
@app.before_request #runs at the begining of every request and check for the email in the dict., if its not there and directs them to log in
def require_login():
    allowed_routes =['login', 'signup']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        user_email=request.form['email']
        password=request.form['password']
        verify=request.form['verify']

        email_error =""
        verify_error=""
        user_email_error=""

        if len(user_email)>=20 or len(user_email)==0:
            email_error="Please enter valid eamil"
            return email_error

        if password != verify:
            verify_error = "password dont match"
            return verify_error

        if len(email_error)>0: # if we have multiple error messages, this is saying if any of them are true. alt. if email_error:
            return "Test"

        verify_user = User.query.filter_by(email=user_email).first()
        if verify_user == None: # checks if input email is in the database and if not present returns none
            #TODO signup/register user_email
            new_user = User(user_email, password)
            db.session.add(new_user)
            db.session.commit()

            #TODO Remember the user
            session['email']=user_email

            return redirect('/')
        else:
            user_email_error="email already in use"

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')


@app.route('/', methods=['POST', 'GET'])
def index():

    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        error_title=""
        error_content=""
        blog_title = request.form['title']
        blog_content = request.form['content']
        if len(blog_title) >= 120 or len(blog_title)==0:
            error_title = "Limit message under 120 characthers"
            blog_title="" #displays empty title instead of the the error content
        if len(blog_content) >=1000 or len(blog_content)==0:
            error_content = "Limit message under 1000 characthers"
            blog_content=""
        if len(error_title)>0 or len(error_content)>0:
            return render_template('index.html',page_name="Build a Blog!", title=blog_title, content= blog_content, error_title=error_title, error_content=error_content)
        else:
            new_post = Blog(blog_title, blog_content, owner)
            db.session.add(new_post)
            db.session.commit()
            return redirect("/mainpage?id="+str(new_post.id))

    posts = Blog.query.filter_by(owner=owner).all()
    return render_template('newpost.html',page_name="Add a Blog Entry", posts=posts)


@app.route('/mainpage', methods=['GET'])
def add():
    blog_id = request.args.get('id')
    blog_user = request.args.get('email')

    if blog_id:
        post = Blog.query.filter_by(id=blog_id).first()
        return render_template('singleblog.html', page_name="Build A Blog", post=post)

    elif blog_user:
        user_id = User.query.filter_by(email=blog_user).first().id
        posts = Blog.query.filter_by(owner_id=user_id).all()
        return render_template('mainpage.html', posts=posts)
        #return "Hello"

    else:
        users= User.query.all()
        return render_template('userlist.html', page_name = "blog users!", users=users)

@app.route('/index', methods=['GET'])
def test():
    blog_id = request.args.get('id')
    if blog_id==None:
        posts = Blog.query.all()
        return render_template('index.html', page_name="Blog Posts!", posts=posts)

    else:
        singl_post= Blog.query.filter_by(id=blog_id).first()
        return render_template('singleblog.html', post=singl_post)

if __name__ == '__main__':
    app.run()
