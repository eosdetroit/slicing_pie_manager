# This file defines command line commands for manage.py
#
# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

import datetime

from flask import current_app
from flask_script import Command, Option

from slicing_pie_manager import db
from slicing_pie_manager.models.user_models import User, Role


class CreateRoleCommand(Command):
    """ Create a new role."""

    option_list = (
        Option('--name', '-n', dest='name'),
        Option('--label', '-l', dest='label'),
    )
    def run(self, name, label):
        find_or_create_role(name, label)
        db.session.commit()


def find_or_create_role(name, label):
    """ Find existing role or create new role """
    role = Role.query.filter(Role.name == name).first()
    if not role:
        role = Role(name=name, label=label)
        db.session.add(role)
    return role

