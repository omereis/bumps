from setuptools import setup

setup(
    name='bumps_flask',
    packages=['bumps_flask'],
    include_package_date=True,
    install_requires=[
        'flask',
        'flask_redis',
        'flask_restful',
        'requests'
    ],
)
