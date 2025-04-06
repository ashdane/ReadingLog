from app import app, db, User
from datetime import datetime

with app.app_context():
    new_user = User(username='daniel', password='1234')
    db.session.add(new_user)
    db.session.commit()

    print("User created successfully!")
