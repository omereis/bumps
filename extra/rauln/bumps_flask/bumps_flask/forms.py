from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileField, FileAllowed
from wtforms import StringField, IntegerField, FloatField, SelectField, FormField
from wtforms.validators import DataRequired

from bumps_flask import rdb

class TokenForm(FlaskForm):
    token = StringField('Enter your token: ', validators=[DataRequired()])

class UploadForm(FlaskForm):
    upload = FileField('', validators=[
        FileRequired(),
        FileAllowed(['xml'], 'XML only!')])


class StepForm(FlaskForm):
    steps = IntegerField(label='steps: ', validators=[DataRequired(message='Missing steps...')], default=100)


class LineForm(FlaskForm):
    x = StringField(label='x: ', validators=[DataRequired(message='Missing x values.')], default='1,2,3,4,5,6')
    y = StringField(label='y: ', validators=[DataRequired(message='Missing y values.')], default='2.1,4.0,6.3,8.03,9.6,11.9')
    dy = StringField(label='dy: ', validators=[DataRequired(message='Missing dy values.')], default='0.05,0.05,0.2,0.05,0.2,0.2')
    m = FloatField(label='slope (m): ', validators=[DataRequired(message='Missing slope value.')], default=2.0)
    b = FloatField(label='y-intercept (b): ', validators=[DataRequired(message='Missing b values.')], default=2.0)


class OptimizerForm(FlaskForm):
    optimizer = SelectField('Fit Optimizer', choices=[
                             ('lm', 'Levenberg Marquardt'),
                             ('newton', 'Quasi-Newton BFGS'),
                             ('de', 'Differential Evolution'),
                             ('dream', 'DREAM'),
                             ('amoeba', 'Nelder-Mead Simplex')
                             ], validators=[DataRequired()], default='lm')

class FitForm(FlaskForm):
    '''
    Test form for performing a linear curve fit.
    The idea is to test handling data and running a simple fit
    on the server.
    '''
    line = FormField(LineForm)
    steps = FormField(StepForm)
    optimizer = FormField(OptimizerForm)
    upload = FileField('Model file upload: ', validators=[
        FileAllowed(['xml'], 'XML files only!')])
        # , FileRequired(message='A proper model field is required.')])
