from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField
from wtforms.validators import DataRequired

from bumps_flask import rdb


class TokenForm(FlaskForm):
    token = StringField('Enter your token: ', validators=[DataRequired()])
    def validate_token(form, field):
        if not rdb.exists('user_tokens', field.data):
            raise ValidationError('Not a valid token.')


class FitForm(FlaskForm):
    pass


class LineForm(FitForm):
    m = FloatField(label='slope (m): ', validators=[DataRequired()])
    x = FloatField(label='x: ', validators=[DataRequired()])
    b = FloatField(label='y-intercept (b): ', validators=[DataRequired()], default=0.0)


class OptimizerForm(FlaskForm):
    optimizer = SelectField('Fit Optimizer', choices=[
                             ('lm', 'Levenberg Marquardt'),
                             ('newton', 'Quasi-Newton BFGS'),
                             ('de', 'Differential Evolution'),
                             ('dream', 'DREAM'),
                             ('amoeba', 'Nelder-Mead Simplex')
                             ], validators=[DataRequired()], default='lm')
