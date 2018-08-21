from setuptools import setup

setup(
    name='slicing_pie_manager',
    packages=['slicing_pie_manager'],
    include_package_data=True,
    install_requires=[
        'flask==1.0.2',
        'Flask-Login==0.4.0',
        'flask_sqlalchemy==2.3.2',
        'Flask-Migrate==2.0.2',
        'Flask-Script==2.0.5',
        'Flask-User==0.6.21',
        'Flask-WTF==0.14.1',
        'flask-seasurf==0.2.2',
        'mysqlclient',
        'uwsgi',
    ],
)