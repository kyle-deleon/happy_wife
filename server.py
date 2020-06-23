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
        query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES ( %(fn)s, %(ln)s, %(em)s, %(pw)s, NOW(), NOW())"
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
                return redirect('/account')
        else:
            flash("incorrect email and/or password")

    return redirect ('/')

@app.route('/on_logout')  
def on_logout():
    session.clear() 
    return redirect('/')

@app.route('/title')
def marriage_title():
    if "user_id" not in session:
        return redirect('/')
    query = "SELECT * FROM users WHERE id = %(sid)s"
    data = {'sid': session['user_id']}
    mysql = connectToMySQL(schema)
    users = mysql.query_db(query,data)
    return render_template("marriage_title.html", users = users)

@app.route('/wife_click/<user_id>', methods = ["POST"])
def wife_click(user_id):
    if "user_id" not in session:
        return redirect('/')

    #is_valid = True
    #if request.form['age'] < 23:
        #is_valid = False
        #flash("Admins must be 24 years old or older")
    #if is_valid:
    query = "UPDATE users SET husband = false, wife = true, partnered = false, updated_at = NOW() WHERE id = %(uid)s"
    data = {'uid':user_id}
    mysql = connectToMySQL(schema)
    mysql.query_db(query, data)

    return redirect ('/partners')

@app.route('/husband_click/<user_id>', methods = ["POST"])
def husband_click(user_id):
    if "user_id" not in session:
        return redirect('/')

    query = "UPDATE users SET husband = true, wife = false, partnered = false, updated_at = NOW() WHERE id = %(uid)s"
    data = {'uid':user_id}
    mysql = connectToMySQL(schema)
    mysql.query_db(query, data)
    return redirect('/partners')

@app.route('/partners')
def partners():
    if "user_id" not in session:
        return redirect('/')

    query = "SELECT * from users WHERE partnered = false"
    mysql = connectToMySQL(schema)
    users = mysql.query_db(query)

    return render_template("partners.html", users = users)

@app.route('/partner_click/<partner_id>')
def partner_click(partner_id):

    query = "UPDATE users SET partnered = true, updated_at = NOW() WHERE id = %(sid)s"
    data = {'sid':session['user_id']}
    mysql = connectToMySQL(schema)
    mysql.query_db(query, data)

    query = "UPDATE users SET partnered = true, updated_at = NOW() WHERE id = %(pid)s"
    data = {'pid':partner_id}
    mysql = connectToMySQL(schema)
    mysql.query_db(query, data)

    query = "INSERT INTO partnerships(user_id, partner_id, created_at, updated_at) VALUES (%(sid)s, %(pid)s, NOW(), NOW())"
    data = {
        'sid':session['user_id'],
        'pid':partner_id}
    mysql = connectToMySQL(schema)
    mysql.query_db(query,data)
    return redirect('/account')

@app.route('/account')
def account():
    if "user_id" not in session:
        return redirect('/')

    query="SELECT * from partnerships JOIN users ON partner_id = users.id WHERE user_id = %(sid)s"
    data = {'sid':session['user_id']}
    mysql = connectToMySQL(schema)
    partners = mysql.query_db(query, data)

    query="SELECT * from partnerships JOIN users ON user_id = users.id WHERE partner_id = %(sid)s"
    data = {'sid':session['user_id']}
    mysql = connectToMySQL(schema)
    partnerships = mysql.query_db(query, data)
    
    query = " SELECT * FROM tasks where for_id = %(sid)s AND task = TRUE"
    data = {'sid':session['user_id']}
    mysql = connectToMySQL(schema)
    tasks = mysql.query_db(query, data)


    return render_template('account.html', partners = partners, partnerships = partnerships, tasks=tasks)

@app.route('/partnership/<partner_id>')
def partnership(partner_id):
    if "user_id" not in session:
        return redirect('/')

    query="SELECT * from partnerships JOIN users ON partner_id = users.id WHERE user_id = %(sid)s"
    data = {'sid':session['user_id']}
    mysql = connectToMySQL(schema)
    partners = mysql.query_db(query, data)

    query="SELECT * from partnerships JOIN users ON user_id = users.id WHERE partner_id = %(sid)s"
    data = {'sid':session['user_id']}
    mysql = connectToMySQL(schema)
    partnerships = mysql.query_db(query, data)

    query = "SELECT * FROM tasks WHERE for_id = %(pid)s AND reward=TRUE"
    data = {'pid': partner_id}
    mysql = connectToMySQL(schema)
    rewards = mysql.query_db(query, data)

    query = "SELECT * FROM tasks WHERE for_id = %(pid)s AND task=TRUE"
    data = {'pid':partner_id}
    mysql = connectToMySQL(schema)
    tasks = mysql.query_db(query, data)

    return render_template('partnership.html', partners = partners, partnerships = partnerships, rewards = rewards, tasks = tasks )

@app.route("/on_create_task/<partnership_id>/<partner_id>", methods=['POST'])
def create_task(partnership_id, partner_id):
    is_valid = True
    if len(request.form['des']) < 3:
        is_valid = False
        flash("A task must consist of at least 3 characters!")
    if len(request.form['val']) < 1:
        is_valid = False
        flash("A task must be worth at least 1 Kid Coin!")
    if is_valid:
        query = "INSERT INTO tasks(partnership_id, created_by_id, for_id, description, value, task, reward, completed, approved, created_at, updated_at) VALUES(%(par)s, %(uid)s, %(pid)s, %(des)s, %(val)s, true, false, false, false, NOW(), NOW())"
        data = {
            'par':partnership_id,
            'uid':session['user_id'],
            'pid':partner_id,
            'des':request.form['des'],
            'val':request.form['val']
        }
        mysql = connectToMySQL(schema)
        mysql.query_db(query,data)
        print(session['user_id'])
        return redirect(f"/partnership/{partner_id}")
    return redirect('/home')

@app.route("/on_create_reward/<partnership_id>/<partner_id>", methods=['POST'])
def create_reward(partnership_id, partner_id):
    is_valid = True
    if len(request.form['des']) < 1:
        is_valid = False
        flash("A task must consist of at least 1 characters!")
    if len(request.form['val']) < 1:
        is_valid = False
        flash("A task must be worth at least 1 Kid Coin!")
    if is_valid:
        query = "INSERT INTO tasks(partnership_id, created_by_id, for_id, description, value, task, reward, completed, approved, created_at, updated_at) VALUES(%(par)s, %(uid)s, %(pid)s, %(des)s, %(val)s, false, true, false, false, NOW(), NOW())"
        data = {
            'par':partnership_id,
            'uid':session['user_id'],
            'pid':partner_id,
            'des':request.form['des'],
            'val':request.form['val']
        }
        mysql = connectToMySQL(schema)
        mysql.query_db(query,data)
        return redirect(f"/partnership/{partner_id}")
    return redirect(f"/partnership/{partner_id}")

@app.route("/rewards")
def rewards_store():
    if "user_id" not in session:
        return redirect('/')

    query = "SELECT * FROM tasks WHERE for_id= %(sid)s AND reward=true"
    data = {'sid':session['user_id']}
    mysql = connectToMySQL(schema)
    rewards = mysql.query_db(query, data)

    return render_template("rewards.html", rewards = rewards)


if __name__ == "__main__":
    app.run(debug=True)