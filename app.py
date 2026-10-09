import os, sqlite3, secrets
from functools import wraps
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, url_for, session, flash, g, abort
from werkzeug.security import generate_password_hash, check_password_hash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.environ.get('REV_DB_PATH', os.path.join(BASE_DIR, 'rev_pro_hub.db'))
app = Flask(__name__)
app.config.update(
    SECRET_KEY=os.environ.get('REV_SECRET_KEY') or secrets.token_hex(32),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=os.environ.get('REV_HTTPS_ONLY', '0') == '1',
    MAX_CONTENT_LENGTH=2 * 1024 * 1024,
)

ROLES = {'public_visitor', 'student', 'researcher', 'health_professional', 'trainer', 'administrator'}
RESTRICTED_ROLES = {'student', 'researcher', 'health_professional', 'trainer', 'administrator'}


def db_conn():
    if 'db' not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute('PRAGMA foreign_keys = ON')
    return g.db

@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE COLLATE NOCASE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'public_visitor',
        approved INTEGER NOT NULL DEFAULT 0,
        active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL
    )''')
    db.commit()
    admin_email = os.environ.get('REV_ADMIN_EMAIL', '').strip().lower()
    admin_password = os.environ.get('REV_ADMIN_PASSWORD', '')
    admin_name = os.environ.get('REV_ADMIN_NAME', 'REV Pro-Hub Administrator')
    if admin_email and admin_password:
        existing = db.execute('SELECT id FROM users WHERE email = ?', (admin_email,)).fetchone()
        if not existing:
            db.execute('INSERT INTO users(full_name,email,password_hash,role,approved,active,created_at) VALUES(?,?,?,?,1,1,?)',
                       (admin_name, admin_email, generate_password_hash(admin_password), 'administrator', datetime.now(timezone.utc).isoformat()))
            db.commit()
    db.close()

init_db()

@app.before_request
def basic_session_refresh():
    session.permanent = True


def current_user():
    uid = session.get('user_id')
    if not uid:
        return None
    return db_conn().execute('SELECT id, full_name, email, role, approved, active, created_at FROM users WHERE id=?', (uid,)).fetchone()

@app.context_processor
def inject_user():
    return {'current_user': current_user()}


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user():
            flash('Please sign in to continue.', 'info')
            return redirect(url_for('login', next=request.path))
        return fn(*args, **kwargs)
    return wrapper


def approved_access_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user:
            flash('Sign in to request access to restricted modules.', 'info')
            return redirect(url_for('login', next=request.path))
        if not user['active']:
            session.clear()
            flash('This account is inactive. Contact the platform administrator.', 'error')
            return redirect(url_for('login'))
        if not user['approved'] or user['role'] not in RESTRICTED_ROLES:
            return render_template('pending.html', user=user), 403
        return fn(*args, **kwargs)
    return wrapper


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user or user['role'] != 'administrator' or not user['approved']:
            abort(403)
        return fn(*args, **kwargs)
    return wrapper

@app.route('/')
def index():
    db = db_conn()
    stats = {
        'research_projects': db.execute("SELECT COUNT(*) FROM users WHERE role='researcher' AND approved=1").fetchone()[0],
        'registered_users': db.execute('SELECT COUNT(*) FROM users WHERE active=1').fetchone()[0],
        'public_modules': 6,
        'restricted_modules': 4,
    }
    return render_template('index.html', stats=stats)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        requested_role = request.form.get('requested_role', 'public_visitor')
        if requested_role not in ROLES - {'administrator'}:
            requested_role = 'public_visitor'
        if len(full_name) < 2 or '@' not in email or len(password) < 10:
            flash('Enter your full name, a valid email, and a password with at least 10 characters.', 'error')
            return render_template('register.html')
        try:
            db_conn().execute('INSERT INTO users(full_name,email,password_hash,role,approved,active,created_at) VALUES(?,?,?,?,0,1,?)',
                              (full_name, email, generate_password_hash(password), 'public_visitor', datetime.now(timezone.utc).isoformat()))
            db_conn().commit()
        except sqlite3.IntegrityError:
            flash('An account with that email already exists. Please sign in.', 'error')
            return render_template('register.html')
        # Requested roles are intentionally not self-assigned; they are surfaced as a notice for the user to request later.
        session['user_id'] = db_conn().execute('SELECT id FROM users WHERE email=?', (email,)).fetchone()['id']
        flash('Registration complete. You can use public resources now. Restricted access requires administrator approval.', 'success')
        return redirect(url_for('dashboard'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = db_conn().execute('SELECT * FROM users WHERE email=?', (email,)).fetchone()
        if not user or not check_password_hash(user['password_hash'], password) or not user['active']:
            flash('Email or password is incorrect, or the account is inactive.', 'error')
            return render_template('login.html')
        session.clear()
        session['user_id'] = user['id']
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    flash('You have signed out.', 'success')
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user())

@app.route('/resources')
def resources():
    return render_template('resources.html')

@app.route('/modules')
def modules():
    return render_template('modules.html')

@app.route('/restricted')
@approved_access_required
def restricted():
    return render_template('restricted.html', user=current_user())

@app.route('/admin')
@admin_required
def admin():
    db = db_conn()
    users = db.execute('SELECT id,full_name,email,role,approved,active,created_at FROM users ORDER BY approved ASC, created_at DESC').fetchall()
    return render_template('admin.html', users=users, roles=sorted(RESTRICTED_ROLES))

@app.route('/admin/user/<int:user_id>', methods=['POST'])
@admin_required
def admin_update_user(user_id):
    role = request.form.get('role', 'public_visitor')
    if role not in ROLES:
        role = 'public_visitor'
    approved = 1 if request.form.get('approved') == '1' else 0
    active = 1 if request.form.get('active') == '1' else 0
    if role == 'administrator' and approved != 1:
        role = 'public_visitor'
    db_conn().execute('UPDATE users SET role=?, approved=?, active=? WHERE id=? AND id != ?',
                      (role, approved, active, user_id, current_user()['id']))
    db_conn().commit()
    flash('Account settings updated.', 'success')
    return redirect(url_for('admin'))

@app.errorhandler(403)
def forbidden(_error):
    return render_template('403.html'), 403

if __name__ == '__main__':
    # Local development only. Use a production WSGI server and HTTPS for public deployment.
    app.run(host='127.0.0.1', port=int(os.environ.get('PORT', '5000')), debug=False)
