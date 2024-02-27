# from app import db
# from database import Users
#
# user_data = {'id': 'C00000005', 'name': 'dheeraj', 'user_type': 'cashier', 'password': 'Dheeraj@95'}
#
# new_user = Users(id=user_data['id'], name=user_data['name'], user_type=user_data['user_type'],
#                  password=user_data['password'])
#
# db.add(new_user)
#
# db.commit()
#
# db.refresh(new_user)
#
# db.close()

from flask import session, redirect, url_for, request, flash, render_template
from app import db
from database import Users
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

# def login():
#     breakpoint()
#     if 'user' in session:
#         return redirect(url_for('dashboard'))
#
#     if request.method == "POST":
#         usern = request.form.get("username")
#         passw = request.form.get("password")
#         # sql_query = text('SELECT * FROM users WHERE id = :u')
#         # result = db.execute(sql_query, {"u": usern}).fetchone()
#         result = db.query(Users).filter_by(name=usern).first()
#         if result is not None:
#             flag = bcrypt.check_password_hash(passw, result.password)
#             if flag:
#                 # if passw:
#                 session['user'] = usern
#                 session['namet'] = result.name
#                 session['usert'] = result.user_type
#                 flash(f"{result.name.capitalize()}, you are successfully logged in!", "success")
#                 return redirect(url_for('dashboard'))
#         flash("Sorry, Username or password not match.", "danger")
#     return render_template("login.html", login=True)

# from flask_bcrypt import Bcrypt
# from app import app
#
# bcrypt = Bcrypt(app)
#
# password = 'Dheeraj@95'
# passw = 'Dheeraj@95'
#
# if bcrypt.check_password_hash(password, passw) is True:
#     print(True)
# else:
#     print(False)


# def check_password(hashed_pass, password):
#     if bcrypt.check_password_hash(pw_hash=hashed_pass, password=password):
#         return True
#     else:
#         return False


# result = check_password('$2b$12$SVggcNhPgcowLJDKPKEuouTv5JbPj5SEe2tzL6W/v5bNsnJz.M5mi', 'Dheeraj@95')
# print(result)

# print(Users.create(id='C00000016', session=db, name='Abhi', user_type='admin', password='Dheeraj@95'))

print(Users.read(session=db, user_id="C00000016"))

