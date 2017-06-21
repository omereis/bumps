from setuptools import setup

setup(
    name='bumps_flask',
    packages=['bumps_flask'],
    include_package_date=True,
    install_requires=[
        'flask',
        'flask-redis',
        'flask-restful',
        'requests',
        'Flask-JWT-Extended',
        'bumps'
    ],
)
