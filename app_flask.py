import os
import secrets
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
            
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        user_exists = User.query.filter((User.username == username) | (User.email == email)).first()
        if user_exists:
            flash('Username or email already exists')
        else:
            new_user = User(username=username, email=email)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created! Please login.')
            return redirect(url_for('login'))
            
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- Admin Routes ---
def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not getattr(current_user, 'is_admin', False):
            flash('Access denied: Admins only.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/admin')
@login_required
@admin_required
def admin():
    users = User.query.all()
    return render_template('admin.html', users=users)

@app.route('/admin/add', methods=['POST'])
@login_required
@admin_required
def admin_add_user():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    is_admin = True if request.form.get('is_admin') else False
    
    if User.query.filter((User.username == username) | (User.email == email)).first():
        flash('Username or Email already exists')
    else:
        new_user = User(username=username, email=email, is_admin=is_admin)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash(f'User {username} added successfully')
    
    return redirect(url_for('admin'))

@app.route('/admin/edit/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def admin_edit_user(user_id):
    user = User.query.get_or_404(user_id)
    user.username = request.form.get('username')
    user.email = request.form.get('email')
    user.is_admin = True if request.form.get('is_admin') else False
    
    password = request.form.get('password')
    if password:
        user.set_password(password)
    
    db.session.commit()
    flash(f'User {user.username} updated')
    return redirect(url_for('admin'))

@app.route('/admin/delete/<int:user_id>')
@login_required
@admin_required
def admin_delete_user(user_id):
    if user_id == current_user.id:
        flash('You cannot delete your own admin account!')
        return redirect(url_for('admin'))
        
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} deleted')
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(port=5001, debug=True)
