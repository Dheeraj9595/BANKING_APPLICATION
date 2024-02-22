import sys
import csv
import os

import database
from database import Base, Accounts, Customers, Users, CustomerLog, Transactions
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_bcrypt import Bcrypt
from flask import Flask

app = Flask(__name__)
engine = create_engine('mysql+mysqlconnector://admin:Root*1234@localhost:3306/flask_bank',echo=True)
Base.metadata.bind = engine
db = scoped_session(sessionmaker(bind=engine))
bcrypt = Bcrypt(app)


def accounts():
    users_data = [
        {'id': 'C00000001', 'name': 'ramesh', 'user_type': 'executive', 'password': 'Ramesh@001'},
        {'id': 'C00000002', 'name': 'suresh', 'user_type': 'cashier', 'password': 'Suresh@002'},
        {'id': 'C00000003', 'name': 'mahesh', 'user_type': 'teller', 'password': 'Mahesh@003'},
    ]

    for user_data in users_data:
        passw_hash = bcrypt.generate_password_hash(user_data['password']).decode('utf-8')
        new_user = Users(id=user_data['id'], name=user_data['name'], user_type=user_data['user_type'],
                         password=passw_hash)
        db.add(new_user)

    db.commit()
    print("accounts Completed ............................................ ")


if __name__ == "__main__":
    accounts()
