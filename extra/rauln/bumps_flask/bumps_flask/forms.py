from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

from bumps_flask import redis_dummy  # DEBUG


class TokenForm(FlaskForm):
    token = StringField('Enter your token: ', validators=[DataRequired()])
    def validate_token(form, field):
        if field.data not in redis_dummy:
            raise ValidationError('Not a valid token.')
