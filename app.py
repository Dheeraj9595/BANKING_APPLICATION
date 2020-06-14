import os
import sys
from flask import send_file
from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify
from flask_bcrypt import Bcrypt
from flask_session import Session
from database import Base,Accounts,Customers,Users
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = os.urandom(24)

# Configure session to use filesystem
# app.config["SESSION_PERMANENT"] = False
# app.config["SESSION_TYPE"] = "filesystem"
# Session(app)

# Set up database
engine = create_engine('sqlite:///database.db',connect_args={'check_same_thread': False},echo=True)
Base.metadata.bind = engine
db = scoped_session(sessionmaker(bind=engine))
# @app.route("/")
# def welcomepage():
#     return render_template("welcomepage.html")
# def index():
#     if 'user' in session:
#         return redirect(url_for('dashboard'))
    
#     return render_template("login.html" , login=True)
    
# MAIN
@app.route('/')
@app.route("/dashboard")
def dashboard():
    return render_template("home.html", home=True)
    # if 'user' not in session:
    #     return redirect(url_for('index'))
    # else:
    #     return render_template("home.html" , home=True)

@app.route("/addcustomer" , methods=["GET", "POST"])
def addcustomer():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] != "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="executive":
        if request.method == "POST":
            cust_ssn_id = int(request.form.get("cust_ssn_id"))
            name = request.form.get("name")
            address = request.form.get("address")
            age= int(request.form.get("age"))
            state = request.form.get("state")
            city = request.form.get("city")
            result = db.execute("SELECT * from customers WHERE cust_ssn_id = :c", {"c": cust_ssn_id}).fetchone()
            if result is None :
                query = Customers(cust_ssn_id=cust_ssn_id,name=name,address=address,age=age,state=state,city=city,status='activate')
                # result = db.execute("INSERT INTO customers (cust_ssn_id,name,address,age,state,city) VALUES (:c,:n,:add,:a,:s,:city)", {"c": cust_ssn_id,"n":name,"add":address,"a": age,"s":state,"city":city})
                db.add(query)
                db.commit()
                if query.cust_id is None:
                    flash("Data is not inserted","danger")
                else:
                    flash(f"Customer {query.name} is created with customer ID : {query.cust_id}.","success")
                    return redirect(url_for('dashboard'))
            flash(f'SSN id : {cust_ssn_id} is already present in database.','warning')
        
    return render_template('addcustomer.html', addcustomer=True)

@app.route("/viewcustomer" , methods=["GET", "POST"])
def viewcustomer():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] != "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="executive":
        if request.method == "POST":
            cust_ssn_id = request.form.get("cust_ssn_id")
            cust_id = request.form.get("cust_id")
            data = db.execute("SELECT * from customers WHERE cust_id = :c or cust_ssn_id = :d", {"c": cust_id, "d": cust_ssn_id}).fetchone()
            if data is not None and data.status != 'deactivate':
                print(data)
                json_data = {
                    'cust_id': data.cust_id,
                    'cust_ssn_id': data.cust_ssn_id,
                    'name': data.name,
                    'address': data.address,
                    'age': data.age,
                    'state': data.state,
                    'city': data.city
                }
                return render_template('viewcustomer.html', viewcustomer=True, data=json_data)
            
            flash("Customer is Deactivated or not found! Please,Check you input.", 'danger')

    return render_template('viewcustomer.html', viewcustomer=True)

@app.route('/editcustomer')
def editcustomer():
    return redirect(url_for('dashboard'))

@app.route('/deletecustomer')
def deletecustomer():
    return redirect(url_for('dashboard'))

@app.route("/addaccount" , methods=["GET", "POST"])
def addaccount():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] != "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="executive":
        if request.method == "POST":
            cust_id = request.form.get("cust_id")
            acc_type = request.form.get("acc_type")
            amount= int(request.form.get("amount"))
            result = db.execute("SELECT * from customers WHERE cust_ssn_id = :c", {"c": cust_id}).fetchone()
            if result is not None :
                query = Accounts(acc_type=acc_type,balance=amount,cust_id=cust_id)
                db.add(query)
                db.commit()
                if query.cust_id is None:
                    flash("Data is not inserted","danger")
                else:
                    flash(f"Customer {query.acc_id} is created with customer ID : {query.cust_id}.","success")
                    return redirect(url_for('dashboard'))
            flash(f'SSN id : {cust_id} is not present in database.','warning')

    return render_template('addaccount.html', addcustomer=True)

@app.route("/delaccount" , methods=["GET", "POST"])
def delaccount():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] != "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="executive":
        if request.method == "POST":
            acc_id = int(request.form.get("acc_id"))
            acc_type = request.form.get("acc_type")
            result = db.execute("SELECT * from accounts WHERE acc_id = :a", {"a": acc_id}).fetchone()
            if result is not None :
                query = db.execute("delete from accounts WHERE acc_id = :a and acc_type=:at", {"a": acc_id,"at":acc_type})
                db.commit()
                flash(f"Customer account is deleted.","success")
                return redirect(url_for('dashboard'))
            flash(f'SSN id : {acc_id} is not present in database.','warning')
    return render_template('delaccount.html', addcustomer=True)

# # Change Pasword
# @app.route("/change-password", methods=["GET", "POST"])
# def changepass():
#     if 'user' not in session:
#         return redirect(url_for('login'))
#     msg=""
#     if request.method == "POST":
#         try:
#             epswd = request.form.get("epassword")
#             cpswd = request.form.get("cpassword")
#             passw_hash = bcrypt.generate_password_hash(cpswd).decode('utf-8')
#             exist=db.execute("SELECT password FROM accounts WHERE id = :u", {"u": session['user']}).fetchone()
#             if bcrypt.check_password_hash(exist['password'], epswd) is True:
#                 res=db.execute("UPDATE accounts SET password = :u WHERE id = :v",{"u":passw_hash,"v":session['user']})
#                 db.commit()
#                 if res.rowcount > 0:
#                     return redirect(url_for('dashboard'))
#         except exc.IntegrityError:
#             msg = "Unable to process try again"
#     msg="Existing Not matching"
#     return render_template("change_password.html",m=msg)

# # Reset
# @app.route("/reset", methods=["GET", "POST"])
# def reset():
#     msg=""
#     if session['usert']=="admin":
        
#         if request.method == "POST":
#             rollno = request.form.get("rollno")
#             passw_hash = bcrypt.generate_password_hash("srit").decode('utf-8')
#             res=db.execute("UPDATE accounts SET password = :u WHERE id = :v",{"u":passw_hash,"v":rollno})
#             db.commit()
#             if res is not None:
#                 return redirect(url_for('dashboard'))
#         msg=""
#         return render_template("pswdreset.html",m=msg)
#     else:
#         return redirect(url_for('dashboard'))
# LOGOUT
@app.route("/logout")
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))
# LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == "POST":
        usern = request.form.get("username").upper()
        passw = request.form.get("password").encode('utf-8')
        result = db.execute("SELECT * FROM users WHERE id = :u", {"u": usern}).fetchone()
        if result is not None:
            print(result['password'])
            if bcrypt.check_password_hash(result['password'], passw) is True:
                session['user'] = usern
                session['namet'] = result.name
                session['usert'] = result.user_type
                flash(f"{result.name.capitalize()}, you are successfully logged in!", "success")
                return redirect(url_for('dashboard'))
        flash("Sorry, Username or password not match.","danger")
    return render_template("login.html", login=True)
# Main
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
