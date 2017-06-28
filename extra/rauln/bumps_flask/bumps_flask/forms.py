from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileField, FileAllowed
from wtforms import StringField, IntegerField, FloatField, SelectField,\
    FormField, DateTimeField, BooleanField
from wtforms.validators import DataRequired

from bumps_flask import rdb


class ContactForm():
    email = StringField('Email address', validators=[], default='me@example.com')

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
            raise ValidationError('Token \"'+field.data+'\" does not exist in the database.')

class UploadForm(FlaskForm):
    script = FileField('', validators=[
        FileRequired(),
        FileAllowed(['xml', 'py'], '.xml or .py only!')])


class StepForm(FlaskForm):
    '''Corresponds to the bumps CLI command --steps'''
    steps = IntegerField(label='steps: ', validators=[DataRequired(message='Missing steps...')], default=100)


class LineForm(FlaskForm):
    '''
    Test form for performing a linear curve fit.
    The idea is to test handling data and running a simple fit
    on the server.
    '''
    x = StringField(label='x: ', validators=[DataRequired(message='Missing x values.')], default='1,2,3,4,5,6')
    y = StringField(label='y: ', validators=[DataRequired(message='Missing y values.')], default='2.1,4.0,6.3,8.03,9.6,11.9')
    dy = StringField(label='dy: ', validators=[DataRequired(message='Missing dy values.')], default='0.05,0.05,0.2,0.05,0.2,0.2')
    m = FloatField(label='slope (m): ', validators=[DataRequired(message='Missing slope value.')], default=2.0)
    b = FloatField(label='y-intercept (b): ', validators=[DataRequired(message='Missing b values.')], default=2.0)


class OptimizerForm(FlaskForm):
    '''Corresponds to the bumps CLI command --fit'''
    optimizer = SelectField('Fit Optimizer', choices=[
                             ('lm', 'Levenberg Marquardt'),
                             ('newton', 'Quasi-Newton BFGS'),
                             ('de', 'Differential Evolution'),
                             ('dream', 'DREAM'),
                             ('amoeba', 'Nelder-Mead Simplex')
                             ], validators=[DataRequired()], default='lm')



class SlurmForm(FlaskForm):
    '''
    Modeled after https://byuhpc.github.io/BYUJobScriptGenerator/
    '''

    limit_node = BooleanField(label='Limit this job to one node?')
    n_cores = IntegerField(label='Number of processor cores across all nodes:', validators=[DataRequired()], default=1)
    n_gpus = IntegerField(label='Number of GPUs: ', validators=[DataRequired()], default=1)
    memory_per_core = IntegerField(label='memory per processor core: ', validators=[DataRequired()], default=1)
    mem_unit = SelectField(choices=[('gb', 'GB'), ('mb', 'MB')], default='gb')
    walltime = DateTimeField(format='%H:%M:%S')
    jobname = StringField(validators=[])

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

    slurm = FormField(SlurmForm)
    # email = FormField(ContactForm)
