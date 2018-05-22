from datetime import time

from flask_wtf import FlaskForm
from flask_wtf.file import FileField

from wtforms import StringField, IntegerField, FloatField, SelectField,\
    FormField, BooleanField, DateTimeField
from wtforms.validators import DataRequired, Optional, Email, ValidationError

from werkzeug.utils import secure_filename

from . import rdb


# Consider that --remote is implied, --parallel, --notify, --queue and
# --time are built-in

class TokenForm(FlaskForm):
    '''
    Form which handles user login validation at the landing page
    and anywhere else.
    '''

    token = StringField(
        'Enter your token: ', validators=[
            DataRequired(
                message='Please enter a token.')])

    def validate_token(form, field):
        '''
        Validation consists of checking whether or not the submitted
        value corresponds to an existing database token
        '''
        if not rdb.exists(str(field.data)):
            raise ValidationError(
                'Token \"' +
                field.data +
                '\" does not exist in the database.')


class UploadForm(FlaskForm):
    script = FileField('Model file: ', validators=[DataRequired()])

    def validate_script(form, field):
        '''
        Validation consists of checking the file extension
        '''
        filename = secure_filename(field.data.filename)
        if not filename.rsplit('.', 1)[1].lower() == 'py':
            raise ValidationError('Only .py files allowed!')


class EmailForm(FlaskForm):
    email = StringField(
        label='Email address: ',
        validators=[
            Email(
                message='Please enter a valid email address.'),
            Optional()])


# Translating form data to CLI commands for bumps itsel
# Problem setup forms

class ParsForm(FlaskForm):
    '''Corresponds to the bumps CLI command --pars'''
    pass


class ShakeForm(FlaskForm):
    '''Corresponds to the bumps CLI command --shake'''
    shake = BooleanField(
        label='Set random initial values for the parameters in the model?')


class SimulateForm(FlaskForm):
    '''Corresponds to the bumps CLI command --simulate'''
    simulate = BooleanField(
        label='Simulate a dataset using the initial problem parameters?')


class SimRandomForm(FlaskForm):
    '''Corresponds to the bumps CLI command --simrandom'''
    simrandom = BooleanField(
        label='Simulate a dataset using random initial parameters?')


class NoiseForm(FlaskForm):
    '''Corresponds to the bumps CLI command --noise'''
    noise = FloatField(
        label='Noise percentage on the simulated data: ',
        default=5.0)


class SeedForm(FlaskForm):
    '''Corresponds to the bumps CLI command --seed'''
    seed = IntegerField(
        label='Set the seed for the random generator in Numpy: ')

####################
# Stopping condition forms


class StepForm(FlaskForm):
    '''Corresponds to the bumps CLI command --steps'''
    steps = IntegerField(
        label='steps: ',
        validators=[Optional()], default=100)


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
# Optimizer control forms


class OptimizerForm(FlaskForm):
    '''Corresponds to the bumps CLI command --fit'''
    fitter = SelectField('Fit Optimizer: ', choices=[
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
    burn = IntegerField(
        label='burn: ',
        validators=[Optional()], default=100)


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
# Execution control forms


class ResumeFitForm(FlaskForm):
    '''Corresponds to the bumps CLI command --resume'''
    pass


####################
# Output control forms


class CovarianceForm(FlaskForm):
    '''Corresponds to the bumps CLI command --cov'''
    pass


class PlotForm(FlaskForm):
    '''Corresponds to the bumps CLI command --plot'''
    plot = SelectField(
        choices=[('linear', 'linear'), ('log', 'logarithmic'),
                 ('residuals', 'residuals')],
        default='log'
    )

####################
# Bumps control forms


class ChiForm(FlaskForm):
    '''Corresponds to the bumps CLI command --chisq'''
    BooleanField(
        label='Show chi squared and exit? (Use this to test model for syntax errors)')

####################
####################


class SlurmForm(FlaskForm):
    '''
    Modeled after https://byuhpc.github.io/BYUJobScriptGenerator/

    TODO: Fix the Generic Resource (GRES) problem, working with slurm.conf
    '''

    limit_node = BooleanField(label='Limit this job to one node?')
    n_cores = IntegerField(
        label='Number of processor cores across all nodes:',
        validators=[DataRequired()], default=2)
    n_gpus = IntegerField(
        label='Number of GPUs: ',
        validators=[Optional()], default=0)
    mem_per_core = IntegerField(
        label='Memory per processor core: ',
        validators=[DataRequired()], default=512)

    mem_unit = SelectField(
        label='Memory Unit', choices=[
            ('G', 'GB'), ('M', 'MB')], default='M')

    # Walltime needs a regex validator or similar
    walltime = DateTimeField(
        label='Walltime (HH:MM:SS)', default=time(
            00, 30, 00), format='%H:%M:%S')
    jobname = StringField(validators=[Optional()])


class FitForm(FlaskForm):
    '''
    Test form for performing a linear curve fit.
    The idea is to test handling data and running a simple fit
    on the server.
    '''
#    print("In FitForm")
    slurm = FormField(SlurmForm)
    steps = FormField(StepForm)
    burn = FormField(BurnForm)
    optimizer = FormField(OptimizerForm)
    upload = FormField(UploadForm)
#    email = FormField(EmailForm)
#    print("Completed FitForm")
