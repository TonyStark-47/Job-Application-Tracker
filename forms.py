from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, URL, Email
from datetime import datetime


class JobApplicationForm(FlaskForm):
    job_title = StringField("Job Title", validators=[DataRequired()])
    company = StringField("Company", validators=[DataRequired()])
    status = SelectField(
        "Application Status", 
        choices=[
            ('', 'Select Status'), 
            ('Applied', '📤 Applied'), 
            ('Interviewed', '🗣️ Interviewed'), 
            ('Rejected', '❌ Rejected'), 
            ('Offered', '🎉 Offered'), 
            ('Awaiting Interview', '⏳ Awaiting Interview')
        ], 
        validators=[DataRequired()]
    )
    location = StringField("Location", validators=[DataRequired()])
    date = StringField("Date", validators=[DataRequired()], render_kw={"type": "date"})
    link = StringField("Link", validators=[URL()], default='https://www.')
    submit = SubmitField('Add Job Application!')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if kwargs.get('formdata') is None and kwargs.get('obj') is not None:
            self.submit.label.text = 'Update Job Application!'


class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign Me Up!')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Let Me In!')

class OTPForm(FlaskForm):
    otp = IntegerField('OTP', validators=[DataRequired()])
    submit = SubmitField('Verify')