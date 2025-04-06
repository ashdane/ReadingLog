from app import app
from app import db, Book
from datetime import datetime

with app.app_context():
    db.create_all() 

    
    with open('aesop.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    pages = content.split('--page--')

    for page in pages:
        new_page = Book(title="Aesop's Fables", content=page.strip())
        db.session.add(new_page)

    db.session.commit()

    print("Database setup complete!")
