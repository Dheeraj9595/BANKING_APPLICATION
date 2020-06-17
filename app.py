import os
import io
import sys
from flask import send_file
from flask import Flask, session, render_template, request, redirect, url_for, flash, jsonify, Response, make_response
from flask_bcrypt import Bcrypt
from flask_session import Session
from database import Base,Accounts,Customers,Users,CustomerLog,Transactions
from sqlalchemy import create_engine, exc
from sqlalchemy.orm import scoped_session, sessionmaker
import datetime
import pdfkit
import xlwt

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
                result = db.query(Customers).count()
                if result == 0 :
                    query = Customers(cust_id=110110000,cust_ssn_id=cust_ssn_id,name=name,address=address,age=age,state=state,city=city,status='activate')
                else:
                    query = Customers(cust_ssn_id=cust_ssn_id,name=name,address=address,age=age,state=state,city=city,status='activate')
                # result = db.execute("INSERT INTO customers (cust_ssn_id,name,address,age,state,city) VALUES (:c,:n,:add,:a,:s,:city)", {"c": cust_ssn_id,"n":name,"add":address,"a": age,"s":state,"city":city})
                db.add(query)
                db.commit()
                if query.cust_id is None:
                    flash("Data is not inserted! Check you input.","danger")
                else:
                    temp = CustomerLog(cust_id=query.cust_id,log_message="Customer Created")
                    db.add(temp)
                    db.commit()
                    flash(f"Customer {query.name} is created with customer ID : {query.cust_id}.","success")
                    return redirect(url_for('viewcustomer'))
            flash(f'SSN id : {cust_ssn_id} is already present in database.','warning')
        
    return render_template('addcustomer.html', addcustomer=True)

@app.route("/viewcustomer/<cust_id>")
@app.route("/viewcustomer" , methods=["GET", "POST"])
def viewcustomer(cust_id=None):
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
            if data is not None:
                return render_template('viewcustomer.html', viewcustomer=True, data=data)
            
            flash("Customer not found! Please,Check you input.", 'danger')
        elif cust_id is not None:
            data = db.execute("SELECT * from customers WHERE cust_id = :c", {"c": cust_id}).fetchone()
            if data is not None:
                return render_template('viewcustomer.html', viewcustomer=True, data=data)
            
            flash("Customer not found! Please,Check you input.", 'danger')
    else:
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))

    return render_template('viewcustomer.html', viewcustomer=True)

@app.route('/editcustomer')
@app.route('/editcustomer/<cust_id>', methods=["GET", "POST"])
def editcustomer(cust_id=None):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] != "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="executive":
        if cust_id is not None:
            if request.method != "POST":
                cust_id = int(cust_id)
                data = db.execute("SELECT * from customers WHERE cust_id = :c", {"c": cust_id}).fetchone()
                if data is not None and data.status != 'deactivate':
                    return render_template('editcustomer.html', editcustomer=True, data=data)
                else:
                    flash('Customer is deactivated or not present in database.','warning')
            else:
                cust_id = int(cust_id)
                name = request.form.get("name")
                address = request.form.get("address")
                age= int(request.form.get("age"))
                result = db.execute("SELECT * from customers WHERE cust_id = :c and status = 'activate'", {"c": cust_id}).fetchone()
                if result is not None :
                    result = db.execute("UPDATE customers SET name = :n , address = :add , age = :ag WHERE cust_id = :a", {"n": name,"add": address,"ag": age,"a": cust_id})
                    db.commit()
                    temp = CustomerLog(cust_id=cust_id,log_message="Customer Data Updated")
                    db.add(temp)
                    db.commit()
                    flash(f"Customer data are updated successfully.","success")
                else:
                    flash('Invalid customer Id. Please, check customer Id.','warning')

    return redirect(url_for('viewcustomer'))

@app.route('/deletecustomer')
@app.route('/deletecustomer/<cust_id>')
def deletecustomer(cust_id=None):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] != "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="executive":
        if cust_id is not None:
            cust_id = int(cust_id)
            result = db.execute("SELECT * from customers WHERE cust_id = :a and status = 'activate'", {"a": cust_id}).fetchone()
            if result is not None :
                # delete from accounts WHERE acc_id = :a and acc_type=:at", {"a": acc_id,"at":acc_type}
                query = db.execute("UPDATE customers SET status='deactivate' WHERE cust_id = :a", {"a": cust_id})
                db.commit()
                temp = CustomerLog(cust_id=cust_id,log_message="Customer Deactivated")
                db.add(temp)
                db.commit()
                flash(f"Customer is deactivated.","success")
                return redirect(url_for('dashboard'))
            else:
                flash(f'Customer with id : {cust_id} is already deactivated or not present in database.','warning')
    return redirect(url_for('viewcustomer'))

@app.route('/activatecustomer')
@app.route('/activatecustomer/<cust_id>')
def activatecustomer(cust_id=None):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] != "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="executive":
        if cust_id is not None:
            cust_id = int(cust_id)
            result = db.execute("SELECT * from customers WHERE cust_id = :a and status = 'deactivate'", {"a": cust_id}).fetchone()
            if result is not None :
                query = db.execute("UPDATE customers SET status='activate' WHERE cust_id = :a", {"a": cust_id})
                db.commit()
                temp = CustomerLog(cust_id=cust_id,log_message="Customer Activated")
                db.add(temp)
                db.commit()
                flash(f"Customer is activated.","success")
                return redirect(url_for('dashboard'))
            flash(f'Customer with id : {cust_id} is already activated or not present in database.','warning')
    return redirect(url_for('viewcustomer'))

@app.route('/customerstatus')
def customerstatus():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] != "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="executive":
        # join query to get one log message per customer id
        data = db.execute("SELECT customers.cust_id as id, customers.cust_ssn_id as ssn_id, customerlog.log_message as message, customerlog.time_stamp as date from (select cust_id,log_message,time_stamp from customerlog group by cust_id ORDER by time_stamp desc) as customerlog JOIN customers ON customers.cust_id = customerlog.cust_id group by customerlog.cust_id order by customerlog.time_stamp desc").fetchall()
        if data:
            return render_template('customerstatus.html',customerstatus=True , data=data)
        else:
            flash('No data found.','danger')
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
            cust_id = int(request.form.get("cust_id"))
            acc_type = request.form.get("acc_type")
            amount= float(request.form.get("amount"))
            message = "Account successfully created"
            result = db.execute("SELECT * from customers WHERE cust_id = :c", {"c": cust_id}).fetchone()
            if result is not None :
                result = db.execute("SELECT * from accounts WHERE cust_id = :c and acc_type = :at", {"c": cust_id, "at": acc_type}).fetchone()
                if result is None:
                    result = db.query(Accounts).count()
                    if result == 0 :
                        query = Accounts(acc_id=360110000,acc_type=acc_type,balance=amount,cust_id=cust_id,status='active',message=message,last_update=datetime.datetime.now())
                    else:
                        query = Accounts(acc_type=acc_type,balance=amount,cust_id=cust_id,status='active',message=message,last_update=datetime.datetime.now())
                    db.add(query)
                    db.commit()
                    if query.acc_id is None:
                        flash("Data is not inserted! Check you input.","danger")
                    else:
                        flash(f"{query.acc_type} account is created with customer ID : {query.acc_id}.","success")
                        return redirect(url_for('dashboard'))
                else:
                    flash(f'Customer with id : {cust_id} has already {acc_type} account.','warning')
            else:
                flash(f'Customer with id : {cust_id} is not present in database.','warning')

    return render_template('addaccount.html', addaccount=True)

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
                # delete from accounts WHERE acc_id = :a and acc_type=:at", {"a": acc_id,"at":acc_type}
                query = db.execute("UPDATE accounts SET status='deactive' WHERE acc_id = :a and acc_type=:at", {"a": acc_id,"at":acc_type})
                db.commit()
                flash(f"Customer account is Deactivated Successfully.","success")
                return redirect(url_for('dashboard'))
            flash(f'Account with id : {acc_id} is not present in database.','warning')
    return render_template('delaccount.html', delaccount=True)

@app.route("/viewaccount" , methods=["GET", "POST"])
def viewaccount():
    if 'user' not in session:
        return redirect(url_for('login'))        
    if session['usert']=="executive" or session['usert']=="teller" or session['usert']=="cashier":
        if request.method == "POST":
            acc_id = request.form.get("acc_id")
            cust_id = request.form.get("cust_id")
            data = db.execute("SELECT * from accounts WHERE cust_id = :c or acc_id = :d", {"c": cust_id, "d": acc_id}).fetchall()
            if data:
                return render_template('viewaccount.html', viewaccount=True, data=data)
            
            flash("Account not found! Please,Check you input.", 'danger')
    else:
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    return render_template('viewaccount.html', viewaccount=True)

@app.route("/viewaccountstatus" , methods=["GET", "POST"])
def viewaccountstatus():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] != "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="executive":
        data = db.execute("select * from accounts").fetchall()
        if data:
            return render_template('viewaccountstatus.html', viewaccount=True, data=data)
        else:
            flash("Accounts are not found!", 'danger')
    return render_template('viewaccountstatus.html', viewaccount=True)

@app.route('/deposit',methods=['GET','POST'])
@app.route('/deposit/<acc_id>',methods=['GET','POST'])
def deposit(acc_id=None):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] == "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="teller" or session['usert']=="cashier":
        if acc_id is None:
            return redirect(url_for('viewaccount'))
        else:
            if request.method == "POST":
                amount = request.form.get("amount")
                data = db.execute("select * from accounts where acc_id = :a and status='active'",{"a":acc_id}).fetchone()
                if data is not None:
                    balance = int(amount) + int(data.balance)
                    query = db.execute("UPDATE accounts SET balance= :b WHERE acc_id = :a", {"b":balance,"a": data.acc_id})
                    db.commit()
                    flash(f"{amount} Amount deposited into account: {data.acc_id} successfully.",'success')
                    temp = Transactions(acc_id=data.acc_id,trans_message="Amount Deposited",amount=amount)
                    db.add(temp)
                    db.commit()
                else:
                    flash(f"Account not found or Deactivated.",'danger')
            else:
                data = db.execute("select * from accounts where acc_id = :a",{"a":acc_id}).fetchone()
                if data is not None:
                    return render_template('deposit.html', deposit=True, data=data)
                else:
                    flash(f"Account not found or Deactivated.",'danger')

    return redirect(url_for('dashboard'))

    
@app.route('/withdraw',methods=['GET','POST'])
@app.route('/withdraw/<acc_id>',methods=['GET','POST'])
def withdraw(acc_id=None):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] == "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="teller" or session['usert']=="cashier":
        if acc_id is None:
            return redirect(url_for('viewaccount'))
        else:
            if request.method == "POST":
                amount = request.form.get("amount")
                data = db.execute("select * from accounts where acc_id = :a and status='active'",{"a":acc_id}).fetchone()
                if data is not None:
                    if int(data.balance)>=int(amount):
                        balance =  int(data.balance)-int(amount)
                        query = db.execute("UPDATE accounts SET balance= :b WHERE acc_id = :a", {"b":balance,"a": data.acc_id})
                        db.commit()
                        flash(f"{amount} Amount withdrawn from account: {data.acc_id} successfully.",'success')
                        temp = Transactions(acc_id=data.acc_id,trans_message="Amount Withdrawn",amount=amount)
                        db.add(temp)
                        db.commit()
                    else:
                        flash(f"Account doesn't have sufficient Balance.",'success')
                        return redirect(url_for('viewaccount'))
                else:
                    flash(f"Account not found or Deactivated.",'danger')
            else:
                data = db.execute("select * from accounts where acc_id = :a",{"a":acc_id}).fetchone()
                if data is not None:
                    return render_template('withdraw.html', deposit=True, data=data)
                else:
                    flash(f"Account not found or Deactivated.",'danger')

    return redirect(url_for('dashboard'))

@app.route('/transfer',methods=['GET','POST'])
@app.route('/transfer/<cust_id>',methods=['GET','POST'])
def transfer(cust_id=None):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] == "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="teller" or session['usert']=="cashier":
        if cust_id is None:
            return redirect(url_for('viewaccount'))
        else:
            if request.method == 'POST':
                src_type = request.form.get("src_type")
                trg_type = request.form.get("trg_type")
                amount = int(request.form.get("amount"))
                if src_type != trg_type:
                    src_data  = db.execute("select * from accounts where cust_id = :a and acc_type = :t and status='active'",{"a":cust_id,"t":src_type}).fetchone()
                    trg_data  = db.execute("select * from accounts where cust_id = :a and acc_type = :t and status='active'",{"a":cust_id,"t":trg_type}).fetchone()
                    if src_data is not None and trg_data is not None:
                        if src_data.balance > amount:
                            src_balance = src_data.balance - amount
                            trg_balance = trg_data.balance + amount
                            
                            test = db.execute("update accounts set balance = :b where cust_id = :a and acc_type = :t",{"b":src_balance,"a":cust_id,"t":src_type})
                            db.commit()
                            temp = Transactions(acc_id=src_data.acc_id,trans_message="Amount Transfered to "+str(trg_data.acc_id),amount=amount)
                            db.add(temp)
                            db.commit()

                            db.execute("update accounts set balance = :b where cust_id = :a and acc_type = :t",{"b":trg_balance,"a":cust_id,"t":trg_type})
                            db.commit()
                            temp = Transactions(acc_id=trg_data.acc_id,trans_message="Amount received from "+str(src_data.acc_id),amount=amount)
                            db.add(temp)
                            db.commit()

                            flash(f"Amount transfered to {trg_data.acc_id} from {src_data.acc_id} successfully",'success')
                        else:
                            flash("Insufficient amount to transfer.","danger")
                            
                    else:
                        flash("Accounts not found","danger")

                else:
                    flash("Can't Transfer amount to same account.",'warning')

            else:
                data = db.execute("select * from accounts where cust_id = :a",{"a":cust_id}).fetchall()
                if data and len(data) == 2:
                    return render_template('transfer.html', deposit=True, cust_id=cust_id)
                else:
                    flash("Data Not found or Invalid Customer ID",'danger')
                    return redirect(url_for('viewaccount'))

    return redirect(url_for('dashboard'))

@app.route("/statement" , methods=["GET", "POST"])
def statement():
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] == "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))       
    if session['usert']=="teller" or session['usert']=="cashier":
        if request.method == "POST":
            acc_id = request.form.get("acc_id")
            number = request.form.get("number")
            start_date = request.form.get("start_date")
            end_date = request.form.get("end_date")
            if number is not None:
                data = db.execute("SELECT * FROM (SELECT * FROM transactions where acc_id=:d ORDER BY trans_id DESC LIMIT :l)Var1 ORDER BY trans_id ASC;", {"d": acc_id,"l":number}).fetchall()
            else:
                data = db.execute("SELECT * FROM transactions WHERE acc_id=:a and DATE(time_stamp) >= :s AND DATE(time_stamp) <= :e;",{"a":acc_id,"s":start_date,"e":end_date}).fetchall()
            if data:
                return render_template('statement.html', statement=True, data=data, acc_id=acc_id)
            else:
                flash("Account not found! Please,Check you input.", 'danger')
                return redirect(url_for('dashboard'))
    else:
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))
    return render_template('statement.html', viewaccount=True)

@app.route('/pdf_xl_statement/<acc_id>')
@app.route('/pdf_xl_statement/<acc_id>/<ftype>')
def pdf_xl_statement(acc_id=None,ftype=None):
    if 'user' not in session:
        return redirect(url_for('login'))
    if session['usert'] == "executive":
        flash("You don't have access to this page","warning")
        return redirect(url_for('dashboard'))       
    if session['usert']=="teller" or session['usert']=="cashier":
        if acc_id is not None:
            data = db.execute("SELECT * FROM transactions WHERE acc_id=:a order by time_stamp limit 20;",{"a":acc_id}).fetchall()
            column_names = ['TransactionId', 'Description', 'Date', 'Amount']
            if data:
                if ftype is None:
                    rendered = render_template('pdf_xl_statement.html',data=data ,acc_id=acc_id)
                    pdf = pdfkit.from_string(rendered,False)
                    response = make_response(pdf)
                    response.headers['Content-Type'] = 'application/pdf'
                    response.headers['Content-Dispostion'] = 'inline; filename=statment'+str(acc_id)+'.pdf'

                    return response
                elif ftype == 'xl':
                    output = io.BytesIO()
                    #create WorkBook object
                    workbook = xlwt.Workbook()
                    #add a sheet
                    sh = workbook.add_sheet('Account statment')

                    #add headers
                    sh.write(0, 0, 'Transaction ID')
                    sh.write(0, 1, 'Description')
                    sh.write(0, 2, 'Date')
                    sh.write(0, 3, 'Amount')

                    idx = 0
                    for row in data:
                        sh.write(idx+1, 0, str(row.trans_id))
                        sh.write(idx+1, 1, row.trans_message)
                        sh.write(idx+1, 2, str(row.time_stamp))
                        sh.write(idx+1, 3, str(row.amount))
                        idx += 1

                    workbook.save(output)
                    output.seek(0)

                    response = Response(output, mimetype="application/ms-excel", headers={"Content-Disposition":"attachment;filename=statment-"+str(acc_id)+".xls"})
                    return response
            else:
                flash("Invalid account Id",'danger')
        else:
            flash("Please, provide account Id",'warning')
    return redirect(url_for('dashboard'))

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
            if bcrypt.check_password_hash(result['password'], passw) is True:
                session['user'] = usern
                session['namet'] = result.name
                session['usert'] = result.user_type
                flash(f"{result.name.capitalize()}, you are successfully logged in!", "success")
                return redirect(url_for('dashboard'))
        flash("Sorry, Username or password not match.","danger")
    return render_template("login.html", login=True)

@app.route('/api')
@app.route('/api/v1')
def api():
    return """
    <h2>List of Api</h2>
    <ol>
        <li>
            <a href="/api/v1/customerlog">Customer Log</a>
        </li>
    </ol>
    """

@app.route('/customerlog', methods=["GET", "POST"])
@app.route('/api/v1/customerlog', methods=["GET", "POST"])
def customerlog():
    if 'user' not in session:
        flash("Please login","warning")
        return redirect(url_for('login'))
    if session['usert'] != "executive":
        flash("You don't have access to this api","warning")
        return redirect(url_for('dashboard'))
    if session['usert']=="executive":
        if request.method == "POST":
            cust_id = request.json['cust_id']
            data = db.execute("select log_message,time_stamp from customerlog where cust_id= :c ORDER by time_stamp desc",{'c':cust_id}).fetchone()
            t = {
                    "message" : data.log_message,
                    "date" : data.time_stamp
                }
            return jsonify(t)
        else:
            dict_data = []
            data = db.execute("SELECT customers.cust_id as id, customers.cust_ssn_id as ssn_id, customerlog.log_message as message, customerlog.time_stamp as date from customerlog JOIN customers ON customers.cust_id = customerlog.cust_id order by customerlog.time_stamp desc limit 50").fetchall()
            for row in data:
                t = {
                    "id" : row.id,
                    "ssn_id" : row.ssn_id,
                    "message" : row.message,
                    "date" : row.date
                }
                dict_data.append(t)
            return jsonify(dict_data)
    
# Main
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
