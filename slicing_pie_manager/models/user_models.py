# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>, Matt Hogan <matt@twintechlabs.io>
# 
import enum
from datetime import datetime

from flask_user import UserMixin
from flask_user.forms import RegisterForm
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField, SelectField, DateTimeField, validators
from slicing_pie_manager import db


# Define the User data model. Make sure to add the flask_user.UserMixin !!
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)

    # User authentication information (required for Flask-User)
    email = db.Column(db.Unicode(255), nullable=False, server_default=u'', unique=True)
    confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')
    # reset_password_token = db.Column(db.String(100), nullable=False, server_default='')

    # User information
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='0')
    first_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')
    last_name = db.Column(db.Unicode(50), nullable=False, server_default=u'')

    # Relationships
    contributions = db.relationship('Contribution', back_populates='user', lazy=True)
    roles = db.relationship('Role', secondary='users_roles',
                            backref=db.backref('users', lazy='dynamic'))


    def has_role(self, role):
        for item in self.roles:
            if item.name == 'admin':
                return True
        return False

    def role(self):
        print(self.roles)
        for item in self.roles:
            return item.name

    def name(self):
        return self.first_name + " " + self.last_name


class UserInvitation(db.Model):
        __tablename__ = 'user_invites'
        id = db.Column(db.Integer, primary_key=True)
        email = db.Column(db.String(255), nullable=False)
        # save the user of the invitee
        invited_by_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
        # token used for registration page to identify user registering
        token = db.Column(db.String(100), nullable=False, server_default='')


# Define the Role data model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), nullable=False, server_default=u'', unique=True)  # for @roles_accepted()
    label = db.Column(db.Unicode(255), server_default=u'')  # for display purposes


# Define the UserRoles association model
class UsersRoles(db.Model):
    __tablename__ = 'users_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))


# Define the User registration form
# It augments the Flask-User RegisterForm with additional fields
class MyRegisterForm(RegisterForm):
    first_name = StringField('First name', validators=[
        validators.DataRequired('First name is required')])
    last_name = StringField('Last name', validators=[
        validators.DataRequired('Last name is required')])


# Define the User profile form
class UserProfileForm(FlaskForm):
    first_name = StringField('First name', validators=[
        validators.DataRequired('First name is required')])
    last_name = StringField('Last name', validators=[
        validators.DataRequired('Last name is required')])
    submit = SubmitField('Save')


class ContributionStatus(enum.Enum):
    PROPOSED = "Reported"
    APPROVED = "Approved"
    DENIED = "Denied"
    APPEALED = "Appealed"


class Contribution(db.Model):
    __tablename__ = 'contributions'

    id = db.Column(db.Integer, primary_key=True)
    user = db.relationship('User', back_populates='contributions')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task = db.Column(db.Unicode(255), nullable=False)
    work_rate = db.relationship('WorkRate', back_populates='contributions')
    work_rate_id = db.Column(db.Integer, db.ForeignKey('work_rates.id'))
    hours_spent = db.Column(db.Float, default=0.0)
    cash_spent = db.Column(db.Float, default=0.0)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    role = db.relationship('Role')
    status = db.Column(db.String(36), default=ContributionStatus.PROPOSED.value)
    contribution_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class ContributionForm(FlaskForm):
    work_rate = SelectField('Work Category', validators=[
        validators.DataRequired('A work rate category is required.')], coerce=int)
    role = SelectField('Working Group', validators=[
        validators.DataRequired('A working group is required.')], coerce=int)
    task = StringField('Trello Task', validators=[
        validators.DataRequired('A reference to the task is required.'),
        validators.Length(max=255)])
    hours_spent = DecimalField('Hours spent', validators=None, default=0)
    cash_spent = DecimalField('Cash spent', validators=None, default=0)
    contribution_date = DateTimeField(format='%Y-%m-%d %H:%M:%S')
    submit = SubmitField('Create Contribution')


class WorkRate(db.Model):
    __tablename__ = 'work_rates'

    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(80), nullable=False, unique=True)
    slices_per_hour = db.Column(db.Float, nullable=False)
    contributions = db.relationship('Contribution', back_populates='work_rate')


class WorkRateForm(FlaskForm):
    category = StringField('Category Label', validators=[
        validators.DataRequired('A category label is required.'),
        validators.Length(max=80)])
    slices_per_hour = DecimalField('Slices per hour', validators=[
        validators.DataRequired('Slices per hour is required.')])
    submit = SubmitField('Create Work Rate')

