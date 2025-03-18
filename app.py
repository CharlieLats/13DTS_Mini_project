from flask import Flask, render_template, request, redirect, session
import sqlite3
from sqlite3 import Error

DATABASE = 'sessions'
app = Flask(__name__)
app.secret_key = "secret_key"
def connect_database(db_file):
    try:
        con = sqlite3.connect(db_file)
        return con
    except Error:
        print("An error has occurred while connecting to the database")
    return


@app.route('/signup', methods=['POST', 'GET'])
def render_signup_page():
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
        cur = con.cursor()
        query1 = "SELECT email FROM user"
        cur.execute(query1)
        all_emails = cur.fetchall()
        if (email,) in all_emails:
            return redirect('\signup?error=email+already+associated+with+an+account')
        query_insert = "INSERT INTO user (fname, lname, email, password) VALUES (?, ?, ?, ?)"
        cur.execute(query_insert, (fname, lname, email, password))
        con.commit()
        con.close()
    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def render_login_page():
    if request.method == 'POST':
        con = connect_database(DATABASE)
        cur = con.cursor()
        query1 = "SELECT user_id, email, password, fname FROM user"
        cur.execute(query1)
        all_emails = cur.fetchall()
        user_info = cur.fetchone()
        con.close()
        if len(all_emails) > 0:
            email = request.form.get('user_email').lower().strip()
            password = request.form.get('user_password')
            email_found = False
            for i, x in enumerate(all_emails):
                if email in x:
                    email_location = all_emails[i]
                    email_found = True
            if email_found == True:
                if password == email_location[2]:
                    session['user_id'] = user_info[0]
                    session['email'] = user_info[1]
                    session['fname'] = user_info[3]

                else:
                    return redirect('\signup?error=passwords+do+not+match')
            else:
                return redirect('\signup?error=email+not+associated+with+an+account')
        else:
            return redirect('\signup?error=email+not+associated+with+an+account')


    return render_template('login.html')

@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')

@app.route('/my_sessions')
def render_sessions():  # put application's code here
    return render_template('my_sessions.html')

@app.route('/create_sessions')
def render_create_sessions():  # put application's code here
    return render_template('create_sessions.html')

@app.route('/schedule')
def render_schedule():  # put application's code here
    return render_template('schedule.html')


if __name__ == '__main__':
    app.debug = True
    app.run()
