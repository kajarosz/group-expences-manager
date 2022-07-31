from flask import Blueprint, jsonify, request, render_template, flash, redirect, url_for
from werkzeug.exceptions import HTTPException
from .exceptions import RoutingException, RequestException, GeneralException, DatabaseQueryException
from flask_login import login_required, current_user
from main import db
from .models import Expence, participants_table, Group, Currency, Expence, User

views = Blueprint('views', __name__)


# Error handler for custom exceptions
@views.errorhandler(GeneralException)
def exception_raised(e):
    return jsonify(e.message), e.status_code


# Generic HTTP error handler
@views.errorhandler(HTTPException)
def generic_http_error(e):
    return jsonify(error=str(e)), e.code


# home
@views.route('/home', methods=['GET'])
def home():
    return render_template('home.html', title="home", user=current_user)


# groups
@views.route('/groups', methods=['GET'])
@login_required
def groups():
    owned_groups = current_user.owned_groups
    shared_groups = Group.query.join(participants_table).join(User).filter(participants_table.c.user_id == current_user.id).filter(Group.owner != current_user.id).all()
    return render_template('groups.html', title="groups", owned_groups=owned_groups, shared_groups=shared_groups, user=current_user)


# add new group
@views.route('/groups/add-new', methods=['GET', 'POST'])
@login_required
def groups_add_new():
    if request.method == 'POST':
        try:
            group_name = request.form.get('name')
        except:
            message = 'Group name is missing.'
            raise RequestException(message)
        if len(group_name) <= 200:
            owned_groups = current_user.owned_groups
            if not group_name in owned_groups:
                currency = request.form.get('currency')
                new_group = Group(name=group_name, currency=currency, owner=current_user.id)
                new_group.participants.append(current_user)
                db.session.add(new_group)
                db.session.commit()
                flash(f'Group named {group_name} was created!', category='success')
                return redirect(url_for('views.groups'))
            else:
                flash(f'You already own group named {group_name}')
        else:
            flash('This group name is too long', category='error')
    currency_list = [attr for attr in dir(Currency) if not callable(
        getattr(Currency, attr)) and not attr.startswith("__")]
    return render_template('groups_add_new.html', title="groups_add_new", user=current_user, currency_list=currency_list)


# group detail
@views.route('/groups/<int:id>', methods=['GET', 'POST'])
@login_required
def group_expences(id):
    group = Group.query.get(id)
    if request.method == 'POST':
        if request.form['submit_button'] == 'expence':
            try:
                name = request.form.get('name')
                amount = request.form.get('amount')
            except:
                message = 'Expence details are missing.'
                raise RequestException(message)
            if len(name) <= 200:
                if not isinstance(amount, int):
                    debtors = group.participants
                    new_expence = Expence(name=name, amount=amount, expence_group=id, payer=current_user.id)
                    for debtor in debtors:
                        new_expence.debtors.append(debtor)
                    db.session.add(new_expence)
                    db.session.commit()
                    flash(f'New expence was added to {group.name}', category='success')
                else:
                    flash('Expence amount must be a number.', category='error') 
            else:
                flash('Expence name is too long.', category='error')
        elif request.form['submit_button'] == 'participant':
            try:
                login = request.form.get('login')
                email = request.form.get('email')
            except:
                message = 'Participant details are missing.'
                raise RequestException(message)
            if login:
                existing_user = User.query.filter_by(login = login).first()
                if existing_user:
                    group.participants.append(existing_user)
                    db.session.commit()
                    flash('New participant added', category='success') 
                else:
                    flash('This user does not exist.', category='error')
            elif email:
                existing_user = User.query.filter_by(email = email).first()
                if existing_user:
                    group.participants.append(existing_user)
                    db.session.commit()
                    flash('New participant added', category='success') 
                else:
                    flash('User with this e-mail does not exist.', category='error') 
    expences = group.expences_list
    participants = User.query.join(participants_table).join(Group).filter(participants_table.c.group_id == id).all()
    return render_template('group_expences.html', title="group_expences", user=current_user, group=group, expences=expences, participants=participants)


# add new custom expence
@views.route('/groups/<int:id>/expence/add-new', methods=['GET', 'POST'])
@login_required
def expence_add_new(id):
    group = Group.query.get(id)
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            amount = request.form.get('amount')
            payer_id = int(request.form.get('payer'))
            debtors = request.form.get('debtors')
        except:
            message = 'Expence details are missing.'
            raise RequestException(message)
        if len(name) <= 200:
                if not isinstance(amount, int):
                    new_expence = Expence(name=name, amount=amount, expence_group=id, payer=payer_id)
                    print(debtors)
                    for debtor in debtors:
                        user = User.query.get(int(debtor))
                        new_expence.debtors.append(user)
                    db.session.add(new_expence)
                    db.session.commit()
                    flash(f'New expence was added to {group.name}', category='success')
                else:
                    flash('Expence amount must be a number.', category='error') 
        else:
            flash('Expence name is too long.', category='error')
    participants = User.query.join(participants_table).join(Group).filter(participants_table.c.group_id == id).all()
    return render_template('expence_add_new.html', title="expence_add_new", user=current_user, group=group, participants=participants)