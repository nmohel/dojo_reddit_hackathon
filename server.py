from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
import md5

app = Flask(__name__)
app.secret_key = "NotASecretAnymore"
mysql = MySQLConnector(app,'reddit')


## GET ROUTES ###
@app.route('/')
def index(): #diplays login/registration page #DONE
    return render_template('index.html')

 ### All get routes after login should make sure we're passing correct data for navbar/user ##
@app.route('/main')
def main(): #displays homepage
    user_query = "SELECT * FROM users WHERE id = :id"
    subs_query = """SELECT subreddits.name, subreddits.url
    FROM subreddits
    JOIN subscriptions ON subreddits.id = subscriptions.subreddit_id
    JOIN users ON subscriptions.user_id = users.id
    WHERE users.id = :id
    """
    subnames_query = "SELECT * FROM subreddits"  
    data = {'id': session['user_id']}
    user = mysql.query_db(user_query,data)
    subs = mysql.query_db(subs_query, data)
    subnames = mysql.query_db(subnames_query)
    return render_template('homepage.html', user=user[0], user_subs=subs, all_subreddits=subnames)

@app.route('/sub_form')
def sub_form():
    #displays form for adding a new sub
    return render_template('add_sub_form.html')

@app.route('/subs/<subname>') #displays main page for each subreddit and all it's posts, also displays a form for user to add post
def show_sub(subname): 
    sub_query = "SELECT * FROM subreddits WHERE name = :subname" #Make sure we know what sub we are on when a user tries to add a post
    sub_data = {'subname': subname}
    sub_info = mysql.query_db(sub_query,sub_data)

    #Add logic to make sure all posts we are displaying are for this specific sub
    post_query = """SELECT posts.id, posts.title, users.username, COUNT(comments.id) AS num_comments, DATE_FORMAT(posts.updated_at, '%b %d, %Y at %r') AS date
    FROM posts
    LEFT JOIN users ON posts.user_id = users.id
    LEFT JOIN comments ON posts.id = comments.post_id 
    WHERE posts.subreddit_id = :subid
    GROUP BY posts.id
    """ 
    post_data = {'subid': sub_info[0]['id']}
    all_posts = mysql.query_db(post_query, post_data)
    print all_posts

    return render_template('sub_detail.html', sub=sub_info[0], posts=all_posts)

@app.route('/subs/<subname>/<post_id>')
def show_sub_post(subname, post_id):
    post_query = """SELECT users.username, posts.text, posts.created_at, posts.id , posts.title, subreddits.url
    FROM posts
    LEFT JOIN users ON users.id = posts.user_id
    LEFT JOIN subreddits ON subreddits.id = posts.subreddit_id
    WHERE posts.id = :post_id
    """
    data = {'post_id': post_id}
                          
    post = mysql.query_db(post_query, data)    

    comments_query = """SELECT users.username,comments.text, comments.created_at, comments.post_id 
    FROM users JOIN comments ON users.id = comments.user_id
    WHERE comments.post_id = :post_id
    """
                          
    comments = mysql.query_db(comments_query,data)  
    print post

    return render_template('post_detail.html',post=post[0], all_comments= comments)
    

@app.route('/message_center')
def show_messages():
    #displays all messages sent to currently logged in user and forms with option to reply
    #also displays form to send a new message
    return render_template('message_center.html')

# POST ROUTES ##
@app.route('/login', methods=['POST']) #DONE
def login():
    username = request.form['username']
    password = request.form['password']

    if len(username) < 1:
        flash("Please enter an username")
    elif len(password) < 1:
        flash("Please enter a password")
    else:
        password = md5.new(password).hexdigest() #hash password to compare against password in db
        check_login_query = "SELECT * FROM users WHERE username = :username AND password = :password" #make sure there is a user in db with matchin email & password
        check_login_data = {'username':username, 'password':password}
        user = mysql.query_db(check_login_query, check_login_data)
        if user: 
            session['user_id'] = user[0]['id'] #save user's id so we can show their name in success view
            return redirect('/main')
        else:
            flash("Sorry! Can't find a user with that email and password combo.")
    return redirect('/')

@app.route('/register', methods=['POST']) #DONE
def register():
    session['register'] = True
    USERNAME_REGEX = re.compile(r'^[a-zA-Z0-9_-]+')
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    print "username", username, "password", password, "confirm", confirm_password

    #All form validations
    if (len(username) < 2) or (len(username) > 45):
        flash("Username must be between 2 and 45 characters")
    elif not USERNAME_REGEX.match(username):
        flash("Username must only contain letters, numbers, underscores ( _ ) or dashes ( - )")
    elif len(password) < 8:
        flash("Password must be at least 8 characters")
    elif password != confirm_password:
        flash("Password and confirm password do not match")
    else:
        #What to do if form is valid
        password = md5.new(password).hexdigest() #hash password
        check_username_query = "SELECT * FROM users WHERE username = :username" #Do query to make sure a user with this email is not already in database
        check_username_data = {'username': username}
        check_username = mysql.query_db(check_username_query,check_username_data)
        if check_username: #email already exists in db
            flash("A user with this email already exists, try another one.")
        else: #add user to db
            print "username", username, "password", password,
            print "\n\n\n"
            register_query = "INSERT INTO users (username, password) VALUES (:username, :password)"
            register_data = {
            'username': username,
            'password':password
            }
            session['user_id'] = mysql.query_db(register_query,register_data) #insert new row to the database, and keep the value of that row's id
            session.pop('register')
            return redirect('/main')
    return redirect('/') #redirect if form isn't valid for some reason or email already in db

@app.route('/logout', methods=['POST']) #DONE
def logout():
    session.pop('user_id')
    return redirect('/')

@app.route('/sub', methods=['POST'])
def add_sub():
    #Adds a new subreddit, make sure current logged in user is subscribed and set as moderator
    return





@app.route('/post', methods=['POST'])
def add_post():
    #adds a new post to a sub, make sure current user is user_id and sub_id is for correct sub
    title = request.form['title']
    text = request.form['text']
    sub_id = request.form['subid']

    sub_query = "SELECT * FROM subreddits WHERE id = :sub_id"
    sub_data = {'sub_id': sub_id }
    sub_info = mysql.query_db(sub_query, sub_data)
    url = sub_info[0]['url']

    if len(request.form['title']) < 1:
        flash("Post title cannot be blank")
    elif len(request.form['text']) < 1:
        flash("Post text cannot be blank")
    else:
        if len(title) > 255:
            title = title[0:255]
        post_query = "INSERT INTO posts (text, user_id, subreddit_id, created_at, updated_at, title) VALUES (:text, :user_id, :sub_id, NOW(), NOW(), :title)"
        post_data = { 
            'text': request.form['text'],
            'user_id': session['user_id'],
            'sub_id': request.form['subid'],
            'title': request.form['title']
        }
        mysql.query_db(post_query, post_data)
        
    return redirect(url)

@app.route('/comment', methods=['POST'])
def add_comment():
    query = "INSERT INTO comments (text, created_at, updated_at,post_id, user_id) VALUES (:text, NOW(), NOW(),:post_id, :user_id)"
    data = {
        'text': request.form['comment'],
        'post_id': request.form['post_id'],
        'user_id': session['user_id'],
    }
    mysql.query_db(query,data)
    url = request.form['sub_url'] + "/" + request.form['post_id']
    return redirect(url)
    

@app.route('/send_message', methods=['POST'])
def send_message():
    #sends a message to another user (either reply or new send)
    return

@app.route('/subscribe', methods=['POST'])
def subscribe():
    #subscribes user to sub
    sub_id = request.form['subid']
    sub_query = "SELECT * FROM subreddits WHERE id = :subid"
    sub_data = {'subid': sub_id}
    sub_info = mysql.query_db(sub_query, sub_data)
    url = sub_info[0]['url']

    query = "INSERT INTO subscriptions (user_id, subreddit_id, moderator) VALUES (:user_id, :sub_id, 0)"
    data = {'user_id': session['user_id'], 'sub_id': sub_id}
    mysql.query_db(query,data)
    return redirect(url)


app.run(debug=True)