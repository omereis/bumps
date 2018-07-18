from setuptools import setup

setup(
    name='bumps_flask',
    packages=['bumps_flask'],
    include_package_date=True,
    install_requires=[
        'flask',
        'Flask-JWT-Extended',
        'Flask-Redis',
        'Flask-RESTful',
        'Flask-WTF',
        'mpld3',
        'requests',
        'WTForms'
    ],
)
