from app import db
from database import Users

user_data = {'id': 'C00000005', 'name': 'dheeraj', 'user_type': 'cashier', 'password': 'Dheeraj@95'}

new_user = Users(id=user_data['id'], name=user_data['name'], user_type=user_data['user_type'],
                 password=user_data['password'])

db.add(new_user)

db.commit()

db.refresh(new_user)

db.close()
