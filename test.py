from app import db
from database import Users

user_data = {'id': 'C00000004', 'name': 'ramesh', 'user_type': 'executive', 'password': 'Ramesh@001'}

new_user = Users(id=user_data['id'], name=user_data['name'], user_type=user_data['user_type'],
                 password=user_data['password'])

db.add(new_user)

db.commit()

db.refresh(new_user)

db.close()
