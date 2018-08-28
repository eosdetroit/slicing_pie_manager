# This file defines command line commands for manage.py

import datetime

from flask import current_app
from flask_script import Command, Option

from slicing_pie_manager import db
from slicing_pie_manager.models.user_models import User, Role


class AddUserRoleCommand(Command):
    """ Initialize the database."""

    option_list = (
        Option('--email', '-e', dest='email'),
        Option('--roles', '-r', dest='roles', nargs="*")
    )


    def run(self, email, roles):
        add_role_to_user(email, roles)
        db.session.commit()


def add_role_to_user(email, roles):
    """ Find existing user or create new user """
    user = User.query.filter(User.email == email).first()
    if user and roles:
        role_objs = Role.query.filter(Role.name.in_(roles)).all()
        user.roles.extend(role_objs)
        db.session.add(user)
    return user

