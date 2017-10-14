from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
import md5

app = Flask(__name__)
app.secret_key = "NotASecretAnymore"
mysql = MySQLConnector(app,'reddit')


### GET ROUTES ###
@app.route('/')
def index(): #diplays login/registration page #DONE
    return render_template('index.html')

 ### All get routes after login should make sure we're passing correct data for navbar/user ##
@app.route('/main')
def main():
    #displays homepage
    return render_template('homepage.html')

@app.route('/sub_form')
def sub_form():
    #displays form for adding a new sub
    return render_template('add_sub_form.html')

@app.route('/subs/<subname>')
def show_sub(subname):
    #displays main page for each subreddit and all it's posts, also displays a form for user to add post
    #Add logic to make sure all posts we are displaying are for this specific sub
    #Make sure we know what sub we are on when a user tries to add a post
    return render_template('sub_detail.html')

@app.route('/subs/<subname>/<post_id>')
def show_sub_post(subname, post_id):
    #displays main page for each post and all it's comments, also displays a form for user to add comment
    #Add logic to make sure all comments are for this specific post
    #Make sure we know what post we are on when user tries to add a comment
    return render_template('post_detail.html')

@app.route('/message_center')
def show_messages():
    #displays all messages sent to currently logged in user and forms with option to reply
    #also displays form to send a new message
    return render_template('message_center.html')

## POST ROUTES ##
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
            mysql.query_db(register_query,register_data) #insert new row to the database, and keep the value of that row's id
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
    return

@app.route('/comment', methods=['POST'])
def add_comment():
    #adds a new comment to a post, make sure current user is user_id and post_id is for correct post
    return

@app.route('/send_message', methods=['POST'])
def send_message():
    #sends a message to another user (either reply or new send)
    return

@app.route('/subscribe', methods=['POST'])
def subscribe():
    #subscribes user to sub
    return


app.run(debug=True)