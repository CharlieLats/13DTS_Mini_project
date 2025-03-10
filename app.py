from flask import Flask, render_template
import sqlite3
from sqlite3 import Error

app = Flask(__name__)

def connect_database(db_file):
    try:
        con = sqlite3.connect(db_file)
        return con
    except Error:
        print("An error has occurred while connecting to the database")
    return


@app.route('/signup', methods=['POST', 'GET'])
def render_signup_page():
    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def render_login_page():
    return render_template('login.html')

@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
