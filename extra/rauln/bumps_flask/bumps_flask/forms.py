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


#################### Translating form data to CLI commands for bumps itself ####################
#################### Problem setup forms

class ParsForm(FlaskForm):
    '''Corresponds to the bumps CLI command --pars'''
    pass


class ShakeForm(FlaskForm):
    '''Corresponds to the bumps CLI command --shake'''
    pass


class SimulateForm(FlaskForm):
    '''Corresponds to the bumps CLI command --simulate'''
    pass


class SimRandomForm(FlaskForm):
    '''Corresponds to the bumps CLI command --simrandom'''
    pass


class NoiseForm(FlaskForm):
    '''Corresponds to the bumps CLI command --noise'''
    pass


class SeedForm(FlaskForm):
    '''Corresponds to the bumps CLI command --seed'''
    pass

####################
#################### Stopping condition forms


class StepForm(FlaskForm):
    '''Corresponds to the bumps CLI command --steps'''
    steps = IntegerField(
        label='steps: ',
        validators=[DataRequired(message='Missing steps...')],
        default=100)

class SampleForm(FlaskForm):
    '''Corresponds to the bumps CLI command --sample'''
    pass


class FTolForm(FlaskForm):
    '''Corresponds to the bumps CLI command --ftol'''
    pass


class XTolForm(FlaskForm):
    '''Corresponds to the bumps CLI command --xtol'''
    pass


class TimeForm(FlaskForm):
    '''Corresponds to the bumps CLI command --time'''
    pass

####################
#################### Optimizer control forms

class OptimizerForm(FlaskForm):
    '''Corresponds to the bumps CLI command --fit'''
    fitter = SelectField('Fit Optimizer', choices=[
        ('lm', 'Levenberg Marquardt'),
        ('newton', 'Quasi-Newton BFGS'),
        ('de', 'Differential Evolution'),
        ('dream', 'DREAM'),
        ('amoeba', 'Nelder-Mead Simplex'),
        ('pt', 'Parallel Tempering'),
        ('ps', 'Particle Swarm'),
        ('rl', 'Random Lines')
    ], validators=[DataRequired()], default='amoeba')


class PopForm(FlaskForm):
    '''Corresponds to the bumps CLI command --pop'''
    pass


class InitForm(FlaskForm):
    '''Corresponds to the bumps CLI command --init'''
    pass


class BurnForm(FlaskForm):
    '''Corresponds to the bumps CLI command --burn'''
    pass


class ThinForm(FlaskForm):
    '''Corresponds to the bumps CLI command --thin'''
    pass


class CRForm(FlaskForm):
    '''Corresponds to the bumps CLI command --CR'''
    pass


class FForm(FlaskForm):
    '''Corresponds to the bumps CLI command --F'''
    pass


class RadiusForm(FlaskForm):
    '''Corresponds to the bumps CLI command --radius'''
    pass


class NTForm(FlaskForm):
    '''Corresponds to the bumps CLI command --nT'''
    pass


class TMinForm(FlaskForm):
    '''Corresponds to the bumps CLI command --Tmin'''
    pass


class TMaxForm(FlaskForm):
    '''Corresponds to the bumps CLI command --Tmax'''
    pass


class StartsForm(FlaskForm):
    '''Corresponds to the bumps CLI command --starts'''
    starts = IntegerField(
        label='starts: ',
        validators=[Optional()]
    )


class Keep_BestForm(FlaskForm):
    '''Corresponds to the bumps CLI command --keep_best'''
    pass

####################
#################### Execution control forms

class ResumeFitForm(FlaskForm):
    '''Corresponds to the bumps CLI command --resume'''
    pass


class StepMonForm(FlaskForm):
    '''Corresponds to the bumps CLI command --stepmon'''
    pass

####################
#################### Output control forms

class CovarianceForm(FlaskForm):
    '''Corresponds to the bumps CLI command --cov'''
    pass


class PlotForm(FlaskForm):
    '''Corresponds to the bumps CLI command --plot'''
    plot = SelectField(
        choices=[('')]
    )

####################
#################### Bumps control forms

class ChiForm(FlaskForm):
    '''Corresponds to the bumps CLI command --chisq'''
    BooleanField(label='Show chi squared and exit? Use this to test model for syntax errors)')

####################
####################


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

    TODO: Fix the Generic Resource (GRES) problem, working with slurm.conf
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
    slurm = FormField(SlurmForm)
    line = FormField(LineForm)
    steps = FormField(StepForm)
    optimizer = FormField(OptimizerForm)
    upload = FormField(UploadForm)
    email = StringField(
        label='Email address',
        validators=[Optional()])
