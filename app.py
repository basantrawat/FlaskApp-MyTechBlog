from flask import Flask, render_template, request, redirect, session
from flask_mysqldb import MySQL
from datetime import datetime
import json
from werkzeug.utils import secure_filename
import hashlib


app = Flask(__name__)

# Configuring JSON
with open('static/config.json', 'r') as c:
    params = json.load(c)["params"]

app.secret_key = b'5y2LF4Q8znxec'

# MYSQL connectivity through flask-mysqldb package
mysql = MySQL(app)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_DB'] = 'blutechnews'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'


def select(query, dataSet):
    cur = mysql.connection.cursor()
    cur.execute(query, dataSet)
    data = cur.fetchall()
    return (data)


def insert(query, dataSet):
    cur = mysql.connection.cursor()
    cur.execute(query, dataSet)
    mysql.connection.commit()


def delete(query):
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()


def fetch(query):
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()


@app.route('/')
@app.route('/index')
def index():
    query = """SELECT * FROM post"""
    posts = select(query, "")
    if 'username' in session:
        return render_template('index.html', posts=posts, params=params, username=session['username'])

    else:
        return render_template('index.html', posts=posts, params=params)


@app.route('/about')
def about():
    if 'username' in session:
        return render_template('about.html', params=params, username=session['username'])
    else:
        return render_template('about.html', params=params)


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if(request.method == 'POST'):
        name, email, phone, message = request.form.get('name'), request.form.get(
            'email'), request.form.get('phone_no'), request.form.get('msg')
        dataSet = (name, email, phone, message,)
        query = """INSERT INTO CONTACTS (name,email,phone_no,msg) VALUES (%s,%s,%s,%s)"""
        insert(query, dataSet)
        if 'username' in session:
            return render_template('contact.html', params=params, msg="Message Sent Successfully!", username=session['username'])
        return render_template('contact.html', params=params, msg="Message Sent Successfully!")
    else:
        if 'username' in session:
            return render_template('contact.html', params=params, username=session['username'])
        return render_template('contact.html', params=params)


@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    dataSet = (post_slug,)
    query = """SELECT * FROM post WHERE slug=%s"""
    posts = select(query, dataSet)
    if 'username' in session:
        return render_template('post.html', posts=posts, params=params, username=session['username'])
    return render_template('post.html', posts=posts, params=params)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect('/')

    elif(request.method == 'POST'):
        usermail, password = request.form.get(
            'usermail'), request.form.get('password')

        password = hashlib.sha512(password.encode('utf-8')).hexdigest()

        dataSet = (usermail, password,)
        query = """SELECT * FROM users WHERE UserEmail=%s and Password=%s"""
        users = select(query, dataSet)

        """CREATING SESSION"""
        session['username'] = users[0]['UserName']

        if(usermail == users[0]['UserEmail'] and password == users[0]['Password']):
            return redirect('dashboard')
        else:
            return render_template('login.html', params=params, error_msg="Wrong Credentials !!!")
    else:
        return render_template('login.html', params=params)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if(request.method == 'POST'):
        username, usermail, password = request.form.get(
            'username'), request.form.get('usermail'), request.form.get('password')

        password = hashlib.sha512(password.encode('utf-8')).hexdigest()
        dataSet = (username, usermail, password,)
        query = """INSERT INTO users (UserName,UserEmail,Password) VALUES (%s,%s,%s)"""
        insert(query, dataSet)
        return render_template('login.html', params=params)
    else:
        return render_template('signup.html', params=params)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect('/')


@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return render_template('dashboard.html', params=params)
    else:
        return redirect('login')


app.run(debug=True)


# export FLASK_ENV=development
# to restart server
