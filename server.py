from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
import re
import md5

app = Flask(__name__)
app.secret_key = "NotASecretAnymore"
mysql = MySQLConnector(app,'reddit')


### GET ROUTES ###
@app.route('/')
def index():
    #diplays login form page
    return render_template('index.html')

@app.route('/registration_form')
def registration_form():
    #displays registration form page
    return render_template('registration_form.html')

    #All get routes after login should make sure we're passing correct data for navbar
@app.route('/main')
def main():
    #displays homepage
    return render_template('homepage.html')

@app.route('/sub_form')
def sub_form():
    #displays form for adding a new sub
    return render_template('add_sub_form.html')

@app.route('subs/<subname>')
def show_sub(subname):
    #displays main page for each subreddit and all it's posts, also displays a form for user to add post
    #Add logic to make sure all posts we are displaying are for this specific sub
    #Make sure we know what sub we are on when a user tries to add a post
    return render_template('sub_detail.html')

@app.route('subs/<subname>/<post-id>')
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
@app.route('/login', methods=['POST'])
def login():
    #do all login validations and save user's id in session
    return

@app.route('/register', methods=['POST'])
def register():
    #do all registration validation, show errors or success message
    return

@app.route('/logout', methods=['POST']) #DONE
    session.pop['user_id']
    return redirect('/')

@app.route('/sub', methods=['POST'])
def add_sub():
    #Adds a new subreddit, make sure current logged in user is set as moderator
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