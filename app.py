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
    if 'user_id' in session:
        print(session)
        return redirect('/logout')
    else:
        if request.method == 'POST':
            email = request.form.get('user_email').lower().strip()
            hashed_password = request.form.get('tutee_password')
            query1 = "SELECT user_id, fname, password FROM user WHERE email = ?"
            con = connect_database(DATABASE)
            cur = con.cursor()
            cur.execute(query1, (email,))
            user_info = cur.fetchone()
            con.close()
            try:
                user_id = user_info[0]
                fname = user_info[1]
                user_password = user_info[2]
            except IndexError:
                print('Index Error')
                return redirect('\login?error=email+or+password+is+invalid')

            if bcrypt.check_password_hash(user_password, hashed_password) == False:
                return redirect('\login?error=email+or+password+is+invalid')
            else:
                session['email'] = email
                session['user_id'] = user_id
                session['fname'] = fname
                return redirect('/')
        return render_template('login.html')

@app.route('/logout', methods=['POST', 'GET'])
def render_logout():
        session.pop('email')
        session.pop('user_id')
        session.pop('fname')
        return redirect('/login')
@app.route('/')
def hello_world():  # put application's code here
    return render_template('index.html')

@app.route('/my_sessions', methods=['GET', 'POST'])
def render_sessions():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    if request.method == 'GET':
        try:
            con = connect_database(DATABASE)  # connect to database
            query = (f"SELECT location, date, title, description, start_time, end_time, session_id FROM my_sessions "
                     f"WHERE user_id = ? ORDER BY session_id DESC")
            cur = con.cursor()
            cur.execute(query, (user_id, ))
            session_list = cur.fetchall()
            print(session_list)
            con.close()
            return render_template('my_sessions.html', list_of_sessions=session_list, user_id=user_id)
        except Error as e:
            print('Error')
            return render_template('my_sessions.html', error=f"An error occurred: {e}")
    elif request.method == 'POST':
        sess_id = request.form.get('session_id')
        try:
            con = connect_database(DATABASE)
            query = "DELETE FROM my_sessions WHERE session_id = ?"
            cur = con.cursor()
            cur.execute(query, (sess_id,))
            con.commit()
            con.close()
            return redirect('/my_sessions')
        except Error as e:
            print('Error')
            return render_template('my_sessions.html', error=f"An error occurred: {e}")


@app.route('/create_sessions', methods=['POST', 'GET'])
def render_create_sessions():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        s_location = request.form.get('location')
        s_date = request.form.get('date')
        s_start_time = request.form.get('start_time')
        s_end_time = request.form.get('end_time')
        s_tute_id = session['user_id']
        try:
            con = connect_database(DATABASE)
            cur = con.cursor()
            check_session_query = ("SELECT * FROM my_sessions WHERE user_id = ? AND date = ? AND location = ? "
                                   "AND start_time = ? AND end_time = ?")
            cur.execute(check_session_query, (s_tute_id, s_date, s_location, s_start_time, s_end_time))
            existing_session_list = cur.fetchall()
            if existing_session_list:
                con.close()
                return render_template('create_sessions.html', error=f"session already exists")
            insert_session_query = ("INSERT INTO my_sessions (location, date, title, description, start_time, end_time, "
                                    "user_id) VALUES (?, ?, ?, ?, ?, ?, ?)")
            cur.execute(insert_session_query, (s_location, s_date, 'Tutoring Session',
                                               'Session with Charlie Laterveer', s_start_time, s_end_time, s_tute_id,))
            print('Success')
            con.commit()
            con.close()
            return redirect('/my_sessions')
        except Error as e:
            print(f"Error occurred: {e}")
            return render_template('create_sessions.html', error=f"An error occurred: {e}")
    return render_template('create_sessions.html')

@app.route('/schedule', methods=['POST', 'GET'])
def render_schedule():
    if request.method == 'GET':
        con = connect_database(DATABASE)
        query = "SELECT Location, Date, Title, Description, Time, end_time FROM schedule"
        cur = con.cursor()
        cur.execute(query)
        schedule_list = cur.fetchall()
        return render_template('schedule.html', sched=schedule_list)
    elif request.method == 'POST':
        Location = request.form.get('val0')
        Date = request.form.get('val1')
        Title = request.form.get('val2')
        Description = request.form.get('val3')
        Time = request.form.get('val4')
        end_time = request.form.get('val5')
        user_id = session['user_id']
        try:
            con = connect_database(DATABASE)
            cur = con.cursor()
            check_session_query = ("SELECT * FROM my_sessions WHERE user_id = ? AND date = ? AND location = ? "
                                   "AND start_time = ? AND end_time = ?")
            cur.execute(check_session_query, (user_id, Date, Location, Time, end_time))
            existing_session_list = cur.fetchall()
            if existing_session_list:
                con.close()
                return redirect('/schedule')
            insert_session_query = ("INSERT INTO my_sessions (location, date, title, description, start_time, "
                                    "end_time, user_id) VALUES (?, ?, ?, ?, ?, ?, ?) ")
            cur.execute(insert_session_query, (Location, Date, Title, Description, Time, end_time, user_id))
            con.commit()
            con.close()
        except Error as e:
            print(f"Error occurred: {e}")
            return render_template('schedule.html', error=f"An error occurred: {e}")
    return redirect('/my_sessions')


if __name__ == '__main__':
    app.debug = True
    app.run()
