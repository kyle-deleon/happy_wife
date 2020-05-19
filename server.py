from flask import Flask, render_template, request, session, flash, redirect
from flask_bcrypt import Bcrypt
from mysqlconnection import connectToMySQL
import re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

app = Flask(__name__)
app.secret_key = "keep it secret"

bcrypt = Bcrypt(app)
schema = "happy_wife"

@app.route('/')
def log_reg_landing():
    return render_template("login.html")

@app.route('/register')
def register():
    return render_template("reg.html")

@app.route('/on_register', methods=['POST'])
def on_register():
    is_valid = True

    if len(request.form['em']) < 1:
        is_valid = False
        flash("Please enter an email")
    elif not EMAIL_REGEX.match(request.form['em']):
        is_valid = False
        flash("Please enter a valid email")
    else:
        mysql = connectToMySQL(schema)
        query = 'SELECT * FROM users WHERE email = %(em)s;'
        data = {
            'em':request.form['em']
        }
        user = mysql.query_db(query,data)
        if user:
            is_valid = False
            flash("email already in use")

    if len(request.form['fn']) < 2:
        is_valid=False
        flash("Fist name must be atleast 2 characters long.")
    if len(request.form['ln']) < 2:
        is_valid=False
        flash("last name must be atleast 2 characters long.")
    if len(request.form['pw']) < 8:
        is_valid=False
        flash("password must be atleast 8 characters long.")

    if request.form['pw'] != request.form['cpw']:
        is_valid=False
        flash("Passwords must match")

    if is_valid:
        query = "INSERT INTO users (first_name, last_name, email, wife, husband, password, created_at, updated_at) VALUES ( %(fn)s, %(ln)s, %(em)s, %(pw)s, NOW(), NOW())"
        data = {
            "fn": request.form['fn'],
            "ln": request.form['ln'],
            "em": request.form['em'],
            "pw": bcrypt.generate_password_hash(request.form['pw'])
        }
        mysql = connectToMySQL(schema)
        user_id = mysql.query_db(query,data)

        if user_id:
            session['user_id'] = user_id
            session['name'] = request.form['fn']
            return redirect ('/title')

    return redirect('/')

@app.route("/on_login", methods=["POST"])
def on_login():
    is_valid = True

    if not EMAIL_REGEX.match(request.form['em']):
        is_valid = False
        flash("email is not valid")

    if is_valid:
        query = "SELECT users.id, users.first_name, users.password FROM users WHERE users.email = %(em)s"
        data = {
            'em': request.form['em']
        } 
        mysql = connectToMySQL(schema)
        result = mysql.query_db(query, data)

        if result:
            if not bcrypt.check_password_hash(result[0]['password'], request.form['pw']):
                flash("incorrect password and/or email")
                return redirect('/')
            else:
                session['user_id'] = result[0]['id']
                session['name'] = result[0]['first_name']
                return redirect('/home')
        else:
            flash("incorrect email and/or password")

    return redirect ('/')

@app.route('/on_logout')  
def on_logout():
    session.clear() 
    return redirect('/')

@app.route('/title')
def become_admin():
    if "user_id" not in session:
        return redirect('/')
    query = "SELECT * FROM users WHERE id = %(sid)s"
    data = {'sid': session['user_id']}
    mysql = connectToMySQL(schema)
    users = mysql.query_db(query,data)
    return render_template("title.html", users = users)

if __name__ == "__main__":
    app.run(debug=True)