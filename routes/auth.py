from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from models import db, User

auth_bp = Blueprint('auth', __name__)#Creates a Blueprint called auth.
#blueprint groups all related routes in one group

@auth_bp.route('/register', methods=['GET', 'POST'])#This creates the /register route.
#GET  → Show registration page
#POST → Process registration form
def register():
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
    #If the browser submitted the registration form, the method will be POST.So only then do we process the submitted data.
    
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not username or not email or not password:
        #Checks whether any required field is empty.
            flash('All fields are required.', 'danger')
            return render_template('register.html')
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
            
        # Check if username or email already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        #This is an important SQLAlchemy query.It basically means:Find a user whose username matches OR whose email matches.
        #Equivalent SQL idea:SELECT * FROM users WHERE username = ? OR email = ? LIMIT 1;

        if existing_user:
            flash('Username or Email already registered.', 'danger')
            return render_template('register.html')
            
        try:
            new_user = User(username=username, email=email)
            new_user.set_password(password)#This calls the method you studied in models/user.py : set_password()
            #The database stores the hash, not the original password.
            db.session.add(new_user)
            db.session.commit()#Save the transaction permanently.
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:#If something goes wrong while interacting with the database, execution comes here.
            db.session.rollback()#If a database transaction fails, rollback cancels the pending transaction.
            flash(f'An error occurred: {str(e)}', 'danger')
            
    return render_template('register.html')#If the request was a normal GET request, the registration page is displayed.

@auth_bp.route('/login', methods=['GET', 'POST'])
#GET  → Show login page
#POST → Process login
def login():
    # Redirect if already logged in
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
        
    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email', '').strip()
        password = request.form.get('password', '')
        
        if not username_or_email or not password:
            flash('Please enter both your credentials.', 'danger')
            return render_template('login.html')
            
        # Check by email or username
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Invalid username/email or password.', 'danger')
            
    return render_template('login.html')#If it's a GET request or login failed, the login page is rendered.

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
