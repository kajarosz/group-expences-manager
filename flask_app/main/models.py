from flask_login import UserMixin
from datetime import datetime
from main import db
import enum


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    login = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    hashed_password = db.Column(db.String(200), unique=False, nullable=False)
    owned_groups = db.relationship('Group', backref='users', lazy=False)
    paid_expences = db.relationship('Expence', backref='users', lazy=False)

    def __str__(self):
        return self.login


class Currency(enum.Enum):
    PLN = 'polish zloty'
    GBP = 'british pound'
    EUR = 'euro'


participants_table = db.Table('participants',
                              db.Column('group_id', db.Integer, db.ForeignKey(
                                  'groups.id'), primary_key=True),
                              db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True))


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(200), unique=False, nullable=False)
    currency = db.Column(
        db.Enum(Currency), default=Currency.PLN, nullable=False)
    is_closed = db.Column(db.Boolean, default=False)
    owner = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    participants = db.relationship('User', secondary=participants_table, lazy='subquery',
                                   backref=db.backref('groups', lazy=True))
    expences_list = db.relationship('Expence', backref='groups', lazy=False)

    def __str__(self):
        return self.name


debtors_table = db.Table('debtors',
                         db.Column('expence_id', db.Integer, db.ForeignKey(
                             'expences.id'), primary_key=True),
                         db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True))


class Expence(db.Model):
    __tablename__ = 'expences'
    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False)
    name = db.Column(db.String(200), unique=False, nullable=False)
    amount = db.Column(db.Integer, unique=False, nullable=False)
    expence_group = db.Column(db.ForeignKey('groups.id'), nullable=False)
    payer = db.Column(db.ForeignKey('users.id'), nullable=False)
    debtors = db.relationship('User', secondary=debtors_table, lazy='subquery',
                              backref=db.backref('expences', lazy=True))
    timestamp = db.Column(db.DateTime(timezone=False),
                          default=datetime.utcnow())

    def __str__(self):
        return self.name
