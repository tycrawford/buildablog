from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://buildablog:password@localhost:3306/buildablog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


# class Task(db.Model):

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(120))
#     completed = db.Column(db.Boolean)

#     def __init__(self, name):
#         self.name = name
#         self.completed = False

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(300))

    def __init__(self, title, body):
        self.title = title
        self.body = body


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