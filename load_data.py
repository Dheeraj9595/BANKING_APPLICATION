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
engine = create_engine('mysql+mysqlconnector://admin:Root*1234@localhost:3306/flask_bank', echo=True)
Base.metadata.bind = engine
db = scoped_session(sessionmaker(bind=engine))
bcrypt = Bcrypt()


def accounts():
    users_data = [
        {'id': 'C00000009', 'name': 'shahrukh', 'user_type': 'executive', 'password': 'Dheeraj@95'},
        {'id': 'C00000010', 'name': 'salman', 'user_type': 'cashier', 'password': 'Dheeraj@95'},
        {'id': 'C00000011', 'name': 'amir', 'user_type': 'teller', 'password': 'Dheeraj@95'},
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

