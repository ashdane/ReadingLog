from app import app
from app import db, Book
import re

with app.app_context():
    db.create_all()

    # 🧹 Delete old Aesop's Fables entries
    # db.session.query(Book).filter(Book.title == "Aesop's Fables").delete()
    # db.session.commit()

    # 📖 Load and process the text file
    with open('panchatantra.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    pages = content.split('--page--')

    for page in pages:
        # 🎯 Extract chapter title
        titles = re.findall(r'--title--\s*(.*?)\s*--title--', page, re.DOTALL)
        chapter_title = titles[0].strip() if titles else "Untitled"

        # 🧼 Clean body content (remove the title part)
        body = re.sub(r'--title--\s*.*?\s*--title--', '', page, flags=re.DOTALL).strip()

        # 💾 Add to database
        if body:
            new_page = Book(
                title="Panchatantra",
                chapter_title=chapter_title,
                content=body
            )
            db.session.add(new_page)

    db.session.commit()
    print("Old entries removed and new Panchatantra loaded successfully!")
