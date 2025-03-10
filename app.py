from flask import Flask, render_template, request, redirect
import sqlite3
from sqlite3 import Error

app = Flask(__name__)
DATABASE = 'sessions'
def connect_database(db_file):
    try:
        con = sqlite3.connect(db_file)
        return con
    except Error:
        print("An error has occurred while connecting to the database")
    return


@app.route('/signup', methods=['POST', 'GET'])
def render_signup_page(num_email=None):
    if request.method == 'POST':
        fname = request.form.get('user_fname').title().strip()
        lname = request.form.get('user_lname').title().strip()
        email = request.form.get('user_email').lower().strip()
        password = request.form.get('user_password')
        confirm_password = request.form.get('user_confirm_password')
        if password != confirm_password:
            return redirect('\signup?error=passwords+do+not+match')

        if len(password) < 8:
            return redirect("\signup?error=password+must+at+least+8+characters")

        con = connect_database(DATABASE)
        query_insert = "INSERT INTO user (fname, lname, email, password) VALUES (?, ?, ?, ?)"
        cur = con.cursor()
        cur.execute(query_insert, (fname, lname, email, password))
        con.commit()
        con.close()
    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def render_login_page():
    return render_template('login.html')

@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
