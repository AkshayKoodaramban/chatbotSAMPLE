from flask import Flask, render_template, request, session, redirect, url_for, flash
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from functools import wraps

# Import application modules
from src.core.config import Config
from src.controller.system_controller import SystemController
from src.sqldb.admin_auth import AdminAuthManager
from src.api.api import api_blueprint  # Import the API blueprint

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'default-secret-key-for-development')
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER

# Initialize controllers
system_controller = SystemController()
admin_auth = AdminAuthManager()

# Register API blueprint
app.register_blueprint(api_blueprint)

# Helper: Check if admin is logged in
def is_admin_logged_in():
    return session.get('admin_logged_in') is True

# Helper: Require admin login decorator
def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_admin_logged_in():
            return redirect(url_for('admin_login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=5)
    now = datetime.utcnow()
    last_activity = session.get('last_activity')
    if last_activity:
        last_activity_dt = datetime.strptime(last_activity, "%Y-%m-%d %H:%M:%S")
        if now - last_activity_dt > timedelta(minutes=5):
            session.clear()
            if request.endpoint and request.endpoint.startswith('admin'):
                return redirect(url_for('admin_login'))
    session['last_activity'] = now.strftime("%Y-%m-%d %H:%M:%S")

# Web Routes (not API routes)
@app.route('/')
def index():
    """Render the main page for users"""
    return render_template('index.html')

@app.route('/admin')
@admin_login_required
def admin():
    """Render the admin page (admin only)"""
    return render_template('admin.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin sign-in page"""
    if is_admin_logged_in():
        return redirect(url_for('admin'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        if admin_auth.verify_admin(username, password):
            session['admin_logged_in'] = True
            session['admin_username'] = username
            return redirect(url_for('admin'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('admin_login.html')

@app.route('/admin/signup', methods=['GET', 'POST'])
def admin_signup():
    """Admin sign-up page"""
    if is_admin_logged_in():
        return redirect(url_for('admin'))
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        serial_key = request.form.get('serial_key', '').strip()
        # Validate serial key
        if serial_key != Config.ADMIN_SERIAL_KEY:
            flash('Invalid software serial key.', 'danger')
            return render_template('admin_signup.html')
        # Register admin
        success, msg = admin_auth.register_admin(username, password)
        if success:
            flash('Admin account created. Please sign in.', 'success')
            return redirect(url_for('admin_login'))
        else:
            flash(msg, 'danger')
    return render_template('admin_signup.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.clear()
    return redirect(url_for('admin_login'))

# Initialize the application
if __name__ == '__main__':
    # Create required directories if they don't exist
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.VECTORDB_PATH, exist_ok=True)
    
    # Initialize the system
    system_controller.initialize()
    
    # Run the Flask app
    app.run(debug=Config.DEBUG, host=Config.HOST, port=Config.PORT)
