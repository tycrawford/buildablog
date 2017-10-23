from flask import Flask, request, redirect, render_template, session, flash 
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
app.secret_key = 'whomstdvent'
db = SQLAlchemy(app)

#Index
#LOGIN A form wherein previous users can log in
#SIGNUP A form wherein new users can signup 
#LOGOUT A confirmation screen from a logout link that shows a user has been logged out
#NEWPOST A form for signed in users to add posts to the blog
#BLOG A list of all blog posts

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(300))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')
    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['blog', 'login', 'signup', 'index']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'username' not in session:
        loginHeader = """
        <a href="/signup"> Create an Account </a> <br>
        <a href="/login"> Log In </a>
        """
    else:
        loginHeader = """
        Logged in as {0}
        <a href="/logout"> Logout </a>
        """.format(session['username'])
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        userError = ''
        passwordError = ''
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            userError = "Username not in system"
            return render_template("login.html", loginHeader=loginHeader, userError=userError)
        else:
            if existing_user.password != password:
                passwordError = "Password not valid"
                return render_template("login.html", loginHeader=loginHeader, passwordError=passwordError)
            else:
                session['username'] = username
                return redirect("/newpost")
    else:
        return render_template("login.html", loginHeader=loginHeader)
        #TODO Enters username stored in database with correct password, redirect to NewPost
    #TODO Enters correct username but with wrong password, gets redirected to login with password message, save username
    #TODO Enters incorrect username, redirected to login with no username stored
    #TODO Link to Create Account that directs to /signup

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if 'username' not in session:
        loginHeader = """
        <a href="/signup"> Create an Account </a> <br>
        <a href="/login"> Log In </a>
        """
    else:
        loginHeader = """
        Logged in as {0}
        <a href="/logout"> Logout </a>
        """.format(session['username'])
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        userError = ''
        verifyError = ''
        passwordError = ''
        existing_user = User.query.filter_by(username=username).first()
        
        if len(username) < 4 or len(username) > 20:
            userError = "Username must be between 3 and 20 characters"
        if existing_user:
            userError = "That username is already in use"

        #TODO Compare Usernames to those in database
        if len(password) < 4 or len(password) > 20:
            passwordError = "Password must be between 3 and 20 characters"
        if password != verify:
            verifyError = "Passwords do not match!"
        if len(username) == 0:
            userError = 'Must enter a username'
        if len(password) == 0:
            passwordError = 'Must enter a password'
        if len(verify) == 0:
            verifyError = 'Must verify your password'
        if userError == '' and verifyError == '' and passwordError == '' and not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect("/newpost")
            
        else:    
            return render_template("createUser.html", loginHeader=loginHeader, userError=userError, filledUser=username, passwordError=passwordError, verifyError=verifyError)
    else:
        return render_template("createUser.html", loginHeader=loginHeader)

@app.route("/logout")
def logout():
    del session['username']
    return redirect('/login')


@app.route('/newpost')
def newpost():
    loginHeader = """
    Logged in as {0}
    <a href="/logout"> Logout </a>
    """.format(session['username'])
    titleError = request.args.get('titleError')
    bodyError = request.args.get('bodyError')
    title = request.args.get('title')
    body = request.args.get('body')
    if titleError == None and bodyError == None:
        return render_template('newPost.html', loginHeader=loginHeader)
    else:
        return render_template('newPost.html', loginHeader=loginHeader, title=title, body=body,titleError=titleError, bodyError=bodyError)

@app.route('/')
def index():
    if 'username' not in session:
        loginHeader = """
        <a href="/signup"> Create an Account </a> <br>
        <a href="/login"> Log In </a>
        """
    else:
        loginHeader = """
        Logged in as {0}
        <a href="/logout"> Logout </a>
        """.format(session['username'])
    users = User.query.all()
    return render_template('index.html', loginHeader=loginHeader, users=users)

@app.route('/blog', methods=['POST', 'GET'])
def blog():
    rebuiltString = ''
    idList = [blog.id for blog in Blog.query.all()]
    titleList = [blog.title for blog in Blog.query.all()]
    bodyList = [blog.body for blog in Blog.query.all()]
    ownerList = [blog.owner_id for blog in Blog.query.all()]
    startIndex = 0
    if 'username' not in session:
        loginHeader = """
        <a href="/signup"> Create an Account </a> <br>
        <a href="/login"> Log In </a>
        """
    else:
        loginHeader = """
        Logged in as {0}
        <a href="/logout"> Logout </a>
        """.format(session['username'])
    for index in range(len(titleList)):
        owner = User.query.filter_by(id=ownerList[startIndex]).first()
        owner = str(owner.username)
        rebuiltString = rebuiltString + '<h2> <a href="/blog?id={0}">'.format(str(idList[startIndex]))  + titleList[startIndex] + "</a> </h2>" + 'By <a href="/blog?user={0}">'.format(owner) + str(owner) + "</a><br> <p> " + bodyList[startIndex] + "</p> <br>"
        startIndex += 1
    if request.method == 'POST': #If Posting new blog from newpost
        bodyError = ''
        titleError = ''
        blog_name = request.form['title']
        blog_body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()
        if len(blog_body) == 0:
            bodyError = "Body was left empty"
        if len(blog_name) == 0:
            titleError = "Title was left empty"
        if bodyError == '' and titleError == '': # IF Case is no errors, good blog post
            new_blog = Blog(blog_name, blog_body, owner) #New blog object
            db.session.add(new_blog) #add new blog to session
            db.session.commit() #commit
            idList = [blog.id for blog in Blog.query.all()] #get all IDS
            titleList = [blog.title for blog in Blog.query.all()]
            bodyList = [blog.body for blog in Blog.query.all()]
            workIndex = bodyList.index(blog_body)
            singlePost = '<h2> ' + titleList[workIndex] + '</h2> <br>' + '<a href="/blog?user={0}">'.format(owner.username) + str(owner.username) + '<p>' + bodyList[workIndex] + "</p>"
            #return render_template('blog.html', posts=str(singlePost))
            # return render_template('blog.html', posts=str(rebuiltString))
            return redirect("/blog?id={0}".format(str(idList[workIndex])))
        else:
            return redirect('/newpost?bodyError=' + bodyError + "&titleError=" + titleError + "&title=" + blog_name + "&body=" + blog_body)
    else:

        if request.args.get('id') == None:
            if request.args.get('user') == None:
                return render_template('blog.html', loginHeader=loginHeader, posts=str(rebuiltString))
            else: #if there is a user args
                singleUserPosts = ''
                owner = request.args.get('user')
                owner_id = User.query.filter_by(username=owner).first()
                owner_id = owner_id.id
                idList = [blog.id for blog in Blog.query.filter_by(owner_id=owner_id)]
                titleList = [blog.title for blog in Blog.query.filter_by(owner_id=owner_id)]
                bodyList = [blog.body for blog in Blog.query.filter_by(owner_id=owner_id)]
                ownerIDList = [blog.owner_id for blog in Blog.query.filter_by(owner_id=owner_id)]
                startIndex = 0
                for index in range(len(titleList)):
                    singleUserPosts = singleUserPosts + '<h2> <a href="/blog?id={0}">'.format(str(idList[startIndex]))
                    singleUserPosts = singleUserPosts + str(titleList[startIndex]) + "</a></h2>"
                    singleUserPosts = singleUserPosts + '<a href="/blog?user={0}">'.format(owner) 
                    singleUserPosts = singleUserPosts + str(owner) + "</a><p>"+ "<br>"
                    singleUserPosts = singleUserPosts + str(bodyList[startIndex]) + "</p> <br>"
                    startIndex += 1
                return render_template('blog.html', loginHeader=loginHeader, posts=str(singleUserPosts))
        else:
            WID = int(request.args.get('id'))
            ownerID = int(ownerList[idList.index(WID)])
            owner = User.query.filter_by(id=ownerID).first()
            owner = owner.username
            singlePost = '<h2> ' + titleList[idList.index(WID)] + '</h2>' + 'By <a href="/blog?user={0}">'.format(owner) + str(owner) + '</a><p>' + bodyList[idList.index(WID)] + "</p>"
            return render_template('blog.html', loginHeader=loginHeader, posts=str(singlePost))



if __name__ == '__main__':
    app.run()