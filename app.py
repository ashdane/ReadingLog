from flask import Flask, render_template, session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ReadingLog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey'  # Required for session handling

db = SQLAlchemy(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)  # 1 page per row

class UserProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    page_no = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['username'] = username
            return redirect(url_for('read', page_no=1))
        else:
            return "Invalid Credentials"

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    username = session.get('username')
    if not username:
        return redirect(url_for('index'))

    user = User.query.filter_by(username=username).first()
    if not user:
        return redirect(url_for('index'))

    # Total pages = Total pages across all books
    last_page = Book.query.order_by(Book.id.desc()).first()
    total_pages = last_page.id if last_page else 0

    # Pages read by user
    pages_read = UserProgress.query.filter_by(user_id=user.id).count()

    pages_left = total_pages - pages_read

    # Pages read per session - Grouped by session (based on timestamp date)
    progress_data = UserProgress.query.filter_by(user_id=user.id).all()

    sessions = {}
    for progress in progress_data:
        date = progress.timestamp.date()
        if date not in sessions:
            sessions[date] = 0
        sessions[date] += 1

    session_dates = list(sessions.keys())
    pages_per_session = list(sessions.values())

    # Generate Bar Chart
    fig1, ax1 = plt.subplots()
    ax1.bar([str(date) for date in session_dates], pages_per_session)
    ax1.set_title('Pages Read Per Session')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Pages Read')
    img1 = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img1, format='png')
    img1.seek(0)
    bar_chart = base64.b64encode(img1.getvalue()).decode()
    plt.close()

    # Generate Pie Chart
    fig2, ax2 = plt.subplots()
    ax2.pie([pages_read, pages_left], labels=['Read', 'Unread'], autopct='%1.1f%%')
    ax2.set_title('Pages Read vs Not Read')
    img2 = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img2, format='png')
    img2.seek(0)
    pie_chart = base64.b64encode(img2.getvalue()).decode()
    plt.close()

    return render_template('dashboard.html',
                           total_pages=total_pages,
                           pages_read=pages_read,
                           pages_left=pages_left,
                           bar_chart=bar_chart,
                           pie_chart=pie_chart)

@app.route('/read/<int:page_no>')
def read(page_no):
    page = Book.query.get_or_404(page_no)

    username = session.get('username', 'guest')
    user = User.query.filter_by(username=username).first()

    if user:
        already_read = UserProgress.query.filter_by(user_id=user.id, page_no=page_no).first()

        if not already_read:
            progress = UserProgress(
                user_id=user.id,
                book_id=page.id,
                page_no=page_no,
                timestamp=datetime.utcnow()
            )
            db.session.add(progress)
            db.session.commit()

    next_page = page_no + 1 if Book.query.get(page_no + 1) else None

    return render_template('read.html', page=page, next_page=next_page)

@app.route('/reset')
def reset_progress():
    username = session.get('username')
    if not username:
        return redirect(url_for('index'))

    user = User.query.filter_by(username=username).first()
    if user:
        UserProgress.query.filter_by(user_id=user.id).delete()
        db.session.commit()

    return redirect(url_for('dashboard'))


if __name__ == "__main__":
    app.run(debug=True)
