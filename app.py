from flask import Flask, render_template, request, redirect, session
import sqlite3
from sqlite3 import Error
from flask_bcrypt import Bcrypt

DATABASE = 'sessions'
app = Flask(__name__)
app.secret_key = "digitechdatasecretkey"
bcrypt = Bcrypt(app)
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

        hashed_password = bcrypt.generate_password_hash(password)

        con = connect_database(DATABASE)
        cur = con.cursor()
        query1 = "SELECT email FROM user"
        cur.execute(query1)
        all_emails = cur.fetchall()
        if (email,) in all_emails:
            return redirect('\signup?error=email+already+associated+with+an+account')
        query_insert = "INSERT INTO user (fname, lname, email, password) VALUES (?, ?, ?, ?)"
        cur.execute(query_insert, (fname, lname, email, hashed_password))
        con.commit()
        con.close()
        return render_template('login.html')
    return render_template('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def render_login_page():
    if request.method == 'POST':
        email = request.form.get('user_email').lower().strip()
        password = request.form.get('user_password')
        query1 = "SELECT user_id, fname, password FROM user WHERE email = ?"
        con = connect_database(DATABASE)
        cur = con.cursor()
        cur.execute(query1, (email,))
        user_info = cur.fetchone()
        con.close()
        try:
            user_id = user_info[0]
            fname = user_info[3]
            user_password = user_info[2]
        except IndexError:
            return redirect('\login?error=email+or+password+is+invalid')

        if not bcrypt.check_password_hash(user_password, password):
            return redirect('\login?error=email+or+password+is+invalid')

        session['email'] = email
        session['user_id'] = user_id
        session['fname'] = fname
        return redirect('/')
    return render_template('login.html')

@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')

@app.route('/my_sessions')
def render_sessions():  # put application's code here

    return render_template('my_sessions.html')

@app.route('/create_sessions')
def render_create_sessions():
    if request.method == 'GET':
        con = connect_database(DATABASE)
        cur = con.cursor()
        query = "SELECT * FROM my_sessions"
        cur.execute(query)
        l = cur.fetchall()
        con.close()
    return render_template('create_sessions.html', loco = l)

@app.route('/schedule')
def render_schedule():
    con = connect_database(DATABASE)
    query = "SELECT Date, Time, end_time, Title, Description, Location FROM schedule"
    cur = con.cursor()
    cur.execute(query)
    schedule_list = cur.fetchall()
    print(schedule_list)
    return render_template('schedule.html', sched=schedule_list)



if __name__ == '__main__':
    app.debug = True
    app.run()
