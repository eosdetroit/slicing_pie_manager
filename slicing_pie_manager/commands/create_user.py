# This file defines command line commands for manage.py

import datetime

from flask import current_app
from flask_script import Command, Option

from slicing_pie_manager import db
from slicing_pie_manager.models.user_models import User, Role


class CreateUserCommand(Command):
    """ Initialize the database."""

    option_list = (
        Option('--email', '-e', dest='email'),
        Option('--fname', '-f', dest='first_name'),
        Option('--lname', '-l', dest='last_name'),
        Option('--password', '-p', dest='password'),
        Option('--roles', '-r', dest='roles', nargs='*')
    )


    def run(self, email, first_name, last_name, password, roles):
        find_or_create_user(email, first_name, last_name, password, roles)
        db.session.commit()


def find_or_create_user(email, first_name, last_name, password, roles=None):
    """ Find existing user or create new user """
    user = User.query.filter(User.email == email).first()
    if not user:
        user = User(email=email,
                    first_name=first_name,
                    last_name=last_name,
                    password=current_app.user_manager.hash_password(password),
                    active=True,
                    confirmed_at=datetime.datetime.utcnow())
        if roles:
            role_objs = Role.query.filter(Role.name.in_(roles)).all()
            user.roles.extend(role_objs)
        db.session.add(user)
    return user

