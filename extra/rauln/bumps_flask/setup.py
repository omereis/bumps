from setuptools import setup

setup(
    name='bumps_flask',
    packages=['bumps_flask'],
    include_package_date=True,
    install_requires=[
        'bumps',
        'flask',
        'Flask-JWT-Extended',
        'flask-redis',
        'flask-restful',
        'Flask-RQ2',
        'Flask-WTF',
        'requests'
    ],
)
