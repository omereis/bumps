from datetime import time
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileField, FileAllowed
from wtforms import StringField, IntegerField, FloatField, SelectField,\
    FormField, BooleanField
from wtforms.validators import DataRequired, Optional
from wtforms_components import TimeField

from . import rdb


# Consider that --remote is implied, -- parallel, notify, queue and time
# are

class TokenForm(FlaskForm):
    '''
    Form which handles user login validation at the landing page
    and anywhere else.
    '''

    token = StringField('Enter your token: ', validators=[DataRequired()])

    def validate_token(form, field):
        '''
        Validation consists of checking whether or not the submitted
        value corresponds to an existing database token
        '''
        if not rdb.sismember('users', field.data):
            raise ValidationError(
                'Token \"' + field.data + '\" does not exist in the database.')


class UploadForm(FlaskForm):
    script = FileField('', validators=[
        FileRequired(),
        FileAllowed(['xml', 'py'], '.xml or .py only!')])


# Forms for translating to CLI commands for bumps itself
##########
class ChiForm(FlaskForm):
    '''Corresponds to the bumps CLI command --chisq'''
    pass


class StepForm(FlaskForm):
    '''Corresponds to the bumps CLI command --steps'''
    steps = IntegerField(
        label='steps: ',
        validators=[DataRequired(message='Missing steps...')],
        default=100)


class StepMonitorForm(FlaskForm):
    pass


class StartForm(FlaskForm):
    '''Corresponds to the bumps CLI command --starts'''
    starts = IntegerField(
        label='starts: ',
        validators=[Optional()]
    )


class PlotStyleForm(FlaskForm):
    '''Corresponds to the bumps CLI command --plot'''
    pass


class NoiseForm(FlaskForm):
    '''Corresponds to the bumps CLI command --noise'''
    pass


class CovarianceForm(FlaskForm):
    '''Corresponds to the bumps CLI command --cov'''
    pass


class ResumeFitForm(FlaskForm):
    '''Corresponds to the bumps CLI command --resume'''
    pass


# Netwon-Mead specific forms

# Differential Evolution specific forms

# DREAMS specific forms


##########

class OptimizerForm(FlaskForm):
    '''Corresponds to the bumps CLI command --fit'''
    fitter = SelectField('Fit Optimizer', choices=[
        ('lm', 'Levenberg Marquardt'),
        ('newton', 'Quasi-Newton BFGS'),
        ('de', 'Differential Evolution'),
        ('dream', 'DREAM'),
        ('amoeba', 'Nelder-Mead Simplex')
    ], validators=[DataRequired()], default='lm')


class LineForm(FlaskForm):
    '''
    Test form for performing a linear curve fit.
    The idea is to test handling data and running a simple fit
    on the server.
    '''

    x = StringField(
        label='x: ',
        validators=[DataRequired(message='Missing x values.')],
        default='1,2,3,4,5,6')
    y = StringField(
        label='y: ',
        validators=[DataRequired(message='Missing y values.')],
        default='2.1,4.0,6.3,8.03,9.6,11.9')
    dy = StringField(
        label='dy: ',
        validators=[DataRequired(message='Missing dy values.')],
        default='0.05,0.05,0.2,0.05,0.2,0.2')
    m = FloatField(
        label='slope (m): ',
        validators=[DataRequired(message='Missing slope value.')],
        default=2.0)
    b = FloatField(
        label='y-intercept (b): ',
        validators=[DataRequired(message='Missing b values.')],
        default=2.0)


class SlurmForm(FlaskForm):
    '''
    Modeled after https://byuhpc.github.io/BYUJobScriptGenerator/
    '''

    limit_node = BooleanField(label='Limit this job to one node?')
    n_cores = IntegerField(
        label='Number of processor cores across all nodes:',
        validators=[DataRequired()], default=1)
    n_gpus = IntegerField(
        label='Number of GPUs: ',
        validators=[Optional()])
    mem_per_core = IntegerField(
        label='memory per processor core: ',
        validators=[DataRequired()], default=1)

    mem_unit = SelectField(choices=[('G', 'GB'), ('M', 'MB')], default='G')
    walltime = TimeField(default=time(0, 30, 0))
    jobname = StringField(validators=[Optional()])


class FitForm(FlaskForm):
    '''
    Test form for performing a linear curve fit.
    The idea is to test handling data and running a simple fit
    on the server.
    '''
    line = FormField(LineForm)
    steps = FormField(StepForm)
    optimizer = FormField(OptimizerForm)
    # upload = FileField('Model file upload: ', validators=[
    #     FileAllowed(['xml'], 'XML files only!')])

    slurm = FormField(SlurmForm)
    email = StringField(
        label='Email address',
        validators=[Optional()],
        default='me@example.com')
