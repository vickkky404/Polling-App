from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import get_db_connection, init_db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Initialize DB
init_db()

# Helper decorator
def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Login required', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ---------------- User Auth ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                         (username, email, password))
            conn.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
        except:
            flash('Username or email already exists.', 'danger')
        finally:
            conn.close()
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

# ---------------- Home Page ----------------
@app.route('/')
@login_required
def index():
    conn = get_db_connection()
    polls = conn.execute('SELECT * FROM polls').fetchall()
    conn.close()
    return render_template('index.html', polls=polls)

# ---------------- Create Poll ----------------
@app.route('/create', methods=['GET', 'POST'])
@login_required
def create_poll():
    if request.method == 'POST':
        question = request.form['question']
        category = request.form['category']
        expiry_date = request.form['expiry_date']
        options = request.form.getlist('options')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO polls (user_id, question, category, expiry_date) VALUES (?, ?, ?, ?)',
                       (session['user_id'], question, category, expiry_date))
        poll_id = cursor.lastrowid
        for option in options:
            if option.strip():
                cursor.execute('INSERT INTO options (poll_id, option_text) VALUES (?, ?)', (poll_id, option))
        conn.commit()
        conn.close()
        flash('Poll created successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('create_poll.html')

# ---------------- Poll Vote ----------------
@app.route('/poll/<int:poll_id>', methods=['GET', 'POST'])
@login_required
def poll(poll_id):
    conn = get_db_connection()
    poll = conn.execute('SELECT * FROM polls WHERE id = ?', (poll_id,)).fetchone()
    options = conn.execute('SELECT * FROM options WHERE poll_id = ?', (poll_id,)).fetchall()
    if poll['expiry_date']:
        expiry_dt = datetime.strptime(poll['expiry_date'], '%Y-%m-%d')
        if datetime.now() > expiry_dt:
            flash('This poll has expired.', 'warning')
            return redirect(url_for('results', poll_id=poll_id))
    if request.method == 'POST':
        selected_option = request.form.get('option')
        already_voted = conn.execute(
            'SELECT * FROM votes WHERE user_id = ? AND poll_id = ?',
            (session['user_id'], poll_id)
        ).fetchone()
        if not already_voted and selected_option:
            conn.execute('UPDATE options SET votes = votes + 1 WHERE id = ?', (selected_option,))
            conn.execute('INSERT INTO votes (user_id, poll_id, option_id) VALUES (?, ?, ?)',
                         (session['user_id'], poll_id, selected_option))
            conn.commit()
            conn.close()
            flash('Vote submitted!', 'success')
            return redirect(url_for('results', poll_id=poll_id))
        else:
            flash('You have already voted or did not select an option.', 'danger')
    conn.close()
    return render_template('poll.html', poll=poll, options=options)

# ---------------- Poll Results ----------------
@app.route('/results/<int:poll_id>')
@login_required
def results(poll_id):
    conn = get_db_connection()
    poll = conn.execute('SELECT * FROM polls WHERE id = ?', (poll_id,)).fetchone()
    options = conn.execute('SELECT * FROM options WHERE poll_id = ?', (poll_id,)).fetchall()
    conn.close()
    return render_template('results.html', poll=poll, options=options)

# ---------------- Delete Poll ----------------
@app.route('/delete/<int:poll_id>', methods=['POST'])
@login_required
def delete_poll(poll_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM polls WHERE id = ?', (poll_id,))
    conn.execute('DELETE FROM options WHERE poll_id = ?', (poll_id,))
    conn.commit()
    conn.close()
    flash('Poll deleted successfully!', 'info')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
