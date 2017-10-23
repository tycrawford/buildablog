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
    def __init__(self, title, body):
        self.title = title
        self.body = body


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(20))
    password = db.Column(db.String(20))

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        userError = ''
        passwordError = ''
        existing_user = User.query.filter_by(username=username).first()
        if not existing_user:
            userError = "Username not in system"
            return render_template("login.html", userError=userError)
        else:
            if existing_user.password != password:
                passwordError = "Password not valid"
                return render_template("login.html", passwordError=passwordError)
            else:
                session['username'] = username
                return redirect("/newpost")
    else:
        return render_template("login.html")
        #TODO Enters username stored in database with correct password, redirect to NewPost
    #TODO Enters correct username but with wrong password, gets redirected to login with password message, save username
    #TODO Enters incorrect username, redirected to login with no username stored
    #TODO Link to Create Account that directs to /signup

@app.route("/signup", methods=['GET', 'POST'])
def signup():
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
            return render_template("createUser.html", userError=userError, filledUser=username, passwordError=passwordError, verifyError=verifyError)
    else:
        return render_template("createUser.html")

@app.route("/logout")
def logout():
    del session['username']
    return redirect('/login')
# @app.route('/', methods=['POST', 'GET'])
# def index():

#     if request.method == 'POST':              if request.method == 'POST'=
#         task_name = request.form['task']          blog_name = request.form['title']
#         new_task = Task(task_name)                blog_body = request.form['body']
#         db.session.add(new_task)                  new_blog = Blog(blog_name, blog_body)
#         db.session.commit()                       db.session.add(new_blog)
#                                                   db.session.commit()
#     
#     tasks = Task.query.filter_by(completed=False).all()
#     completed_tasks = Task.query.filter_by(completed=True).all()
#     return render_template('todos.html',title="Get It Done!", 
#         tasks=tasks, completed_tasks=completed_tasks)


# @app.route('/delete-task', methods=['POST'])
# def delete_task():

#     task_id = int(request.form['task-id'])
#     task = Task.query.get(task_id)
#     task.completed = True
#     db.session.add(task)
#     db.session.commit()

#     return redirect('/')

# @app.route('/blog')

@app.route('/newpost')
def newpost():
    titleError = request.args.get('titleError')
    bodyError = request.args.get('bodyError')
    title = request.args.get('title')
    body = request.args.get('body')
    if titleError == None and bodyError == None:
        return render_template('newPost.html')
    else:
        print("ran else")
        print(title, body, titleError, bodyError)
        return render_template('newPost.html', title=title, body=body,titleError=titleError, bodyError=bodyError)


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    rebuiltString = ''
    idList = [blog.id for blog in Blog.query.all()]
    titleList = [blog.title for blog in Blog.query.all()]
    bodyList = [blog.body for blog in Blog.query.all()]
    print(idList)
    startIndex = 0
    for index in range(len(titleList)):
        rebuiltString = rebuiltString + '<h2> <a href="/blog?id={0}">'.format(str(idList[startIndex]))  + titleList[startIndex] + "</a> </h2> <br> " + "<p> " + bodyList[startIndex] + "</p> <br>"
        startIndex += 1
    if request.method == 'POST':
        bodyError = ''
        titleError = ''
        blog_name = request.form['title']
        blog_body = request.form['body']
        if len(blog_body) == 0:
            bodyError = "Body was left empty"
        if len(blog_name) == 0:
            titleError = "Title was left empty"
        if bodyError == '' and titleError == '':
            new_blog = Blog(blog_name, blog_body)
            db.session.add(new_blog)
            db.session.commit()
            idList = [blog.id for blog in Blog.query.all()]
            titleList = [blog.title for blog in Blog.query.all()]
            bodyList = [blog.body for blog in Blog.query.all()]
            workIndex = bodyList.index(blog_body)
            singlePost = '<h2> ' + titleList[workIndex] + '</h2> <br> <p>' + bodyList[workIndex] + "</p>"
            #return render_template('blog.html', posts=str(singlePost))
            # return render_template('blog.html', posts=str(rebuiltString))
            return redirect("/blog?id={0}".format(str(idList[workIndex])))
        else:
            return redirect('/newpost?bodyError=' + bodyError + "&titleError=" + titleError + "&title=" + blog_name + "&body=" + blog_body)
    else:

        if request.args.get('id') == None:
            return render_template('blog.html', posts=str(rebuiltString))
        else:
            WID = int(request.args.get('id'))
            singlePost = '<h2> ' + titleList[idList.index(WID)] + '</h2> <br> <p>' + bodyList[idList.index(WID)] + "</p>"
            return render_template('blog.html', posts=str(singlePost))



if __name__ == '__main__':
    app.run()