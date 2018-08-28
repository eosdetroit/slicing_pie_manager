"""This file sets up a command line manager.

Use "python manage.py" for a list of available commands.
Use "python manage.py runserver" to start the development web server on localhost:5000.
Use "python manage.py runserver --help" for additional runserver options.
"""

from flask_migrate import MigrateCommand
from flask_script import Manager

from slicing_pie_manager import create_app
from slicing_pie_manager.commands import InitDbCommand, CreateUserCommand, CreateRoleCommand, AddUserRoleCommand


# Setup Flask-Script with command line commands
manager = Manager(create_app)
manager.add_command('db', MigrateCommand)
manager.add_command('init_db', InitDbCommand)
manager.add_command('create_user', CreateUserCommand)
manager.add_command('create_role', CreateRoleCommand)
manager.add_command('add_user_role', AddUserRoleCommand)


if __name__ == "__main__":
    # python manage.py                      # shows available commands
    # python manage.py runserver --help     # shows available runserver options
    manager.run()
