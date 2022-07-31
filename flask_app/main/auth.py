from flask import Blueprint, jsonify, request, render_template, flash, redirect, url_for
from werkzeug.exceptions import HTTPException
from .exceptions import RoutingException, RequestException, GeneralException, DatabaseQueryException
from flask_login import login_user, login_required, logout_user, current_user
from sqlalchemy.sql import exists
from main import db
from .models import User
from .utilities import is_email_valid, is_pass_valid, hash_md5

auth = Blueprint('auth', __name__)

max_login = 20
min_login = 4


# Error handler for custom exceptions
@auth.errorhandler(GeneralException)
def exception_raised(e):
    return jsonify(e.message), e.status_code

# Generic HTTP error handler
@auth.errorhandler(HTTPException)
def generic_http_error(e):
    return jsonify(error=str(e)), e.code

# register
@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        login_valid, email_valid, password_valid = False, False, False
        try:
            login = request.form.get('login')
            email = request.form.get('email')
            password = request.form.get('password')
        except:
            message = 'Some keys are missing. Please provide following keys: login, email and password'
            raise RequestException(message)
        if login:
            if max_login >= len(login) >= min_login:
                if not db.session.query(exists().where(User.login == login)).scalar():
                    login_valid = True
                else:
                    flash('Login is already taken.', category='error')
            else:
                flash('Login must be at least 4 characters long.', category='error')
        else:
            flash('Login is missing', category='error')
        if email:
            if not db.session.query(exists().where(User.email == email)).scalar():
                if is_email_valid(email):
                    email_valid = True
                else:
                    flash('E-mail is invalid.', category='error')
            else:
                flash('E-mail is already taken.', category='error')
        else:
            flash('E-mail is missing.', category='error')
        if password:
            if is_pass_valid(password):
                password_valid = True
                hashed_password = hash_md5(password)
            else:
                flash('Password is not safe enough.', category='error')
        else:
            flash('Password is missing.', category='error')
        if login_valid and email_valid and password_valid:
            valid_user = User(login=login, email=email, hashed_password=hashed_password)
            db.session.add(valid_user)
            db.session.commit()
            login_user(valid_user, remember=True)
            return redirect(url_for('views.home'))
    return render_template('register.html', title="register", user=current_user)

# login
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            login = request.form.get('login')
            password = request.form.get('password')
        except:
            message = 'Some keys are missing. Please provide following keys: login, email and password'
            raise RequestException(message)
        if len(login) > 0:
            existing_user = User.query.filter_by(login = login).first()
            if existing_user:
                if len(password) > 0:
                    hashed_password = hash_md5(password)
                    if hashed_password == existing_user.hashed_password:
                        login_user(existing_user, remember=True)
                        return redirect(url_for('views.home'))
                    else:
                        flash('Incorrect password.', category='error')
                else:
                    flash('Password is missing!', category='error')
            else:
                flash('This login does not exist in database.', category='error')
        else:
            flash('Login is missing!', category='error')
    return render_template('login.html', title="login", user=current_user)

# logout
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('views.home'))