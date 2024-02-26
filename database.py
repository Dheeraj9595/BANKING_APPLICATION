import os
import sys, datetime
from sqlalchemy import Column, ForeignKey, Integer, String, BigInteger
from sqlalchemy.orm import declarative_base
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'
    id = Column(String(20), primary_key=True)
    name = Column(String(250), nullable=False)
    user_type = Column(String(250), nullable=False)
    password = Column(String(250))


class Customers(Base):
    __tablename__ = 'customers'
    cust_id = Column(Integer, primary_key=True, autoincrement=True)
    cust_ssn_id = Column(Integer, unique=True)
    name = Column(String(250), nullable=False)
    address = Column(String(250), nullable=False)
    age = Column(Integer)
    state = Column(String(250), nullable=False)
    city = Column(String(250), nullable=False)
    status = Column(String(250), nullable=False)


class CustomerLog(Base):
    __tablename__ = 'customerlog'
    log_id = Column(Integer, primary_key=True, autoincrement=True)
    cust_id = Column(Integer, ForeignKey('customers.cust_id'))
    log_message = Column(String(250), nullable=False)
    time_stamp = Column(DateTime(timezone=False), default=datetime.datetime.utcnow)


class Accounts(Base):
    __tablename__ = 'accounts'
    acc_id = Column(Integer, primary_key=True, autoincrement=True)
    acc_type = Column(String(250), nullable=False)
    balance = Column(Integer, nullable=False)
    cust_id = Column(Integer, ForeignKey('customers.cust_id'))
    customers = relationship(Customers)
    status = Column(String(250), nullable=False)
    message = Column(String(250))
    last_update = Column(DateTime)


class Transactions(Base):
    __tablename__ = "transactions"
    trans_id = Column(Integer, primary_key=True, autoincrement=True)
    acc_id = Column(Integer, ForeignKey('accounts.acc_id'))
    trans_message = Column(String(250), nullable=False)
    amount = Column(Integer, nullable=False)
    time_stamp = Column(DateTime(timezone=False), default=datetime.datetime.utcnow)


def check_password(hashed_pass, password):
    if bcrypt.check_password_hash(pw_hash=hashed_pass, password=password):
        return True
    else:
        return False


engine = create_engine('mysql+mysqlconnector://admin:Root*1234@localhost:3306/flask_bank')
Base.metadata.create_all(engine)
