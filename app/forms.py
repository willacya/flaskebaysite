from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, \
    TextAreaField, IntegerField, DecimalField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, \
    Length
from flask_babel import _, lazy_gettext as _l
from app.models import User


class LoginForm(FlaskForm):
    username = StringField(_l("Username"),validators=[DataRequired()])
    password = PasswordField(validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))


class RegistrationForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Register'))

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(_('Please use a different username.'))

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(_('Please use a different email address.'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Request Password Reset'))


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')


class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))

class EbayForm(FlaskForm):
    keyword = StringField(_l("I'm looking for..."), validators=[DataRequired()])
    minAmount = IntegerField(_l("Min"))
    maxAmount = IntegerField(_l("Max"), validators=[DataRequired()])
    submit = SubmitField(_l('Add'))


class SearchSettingsForm(FlaskForm):
    deadline = DecimalField(_l("Email Notification Period (in hours)?"))
    driveTime = DecimalField(_l("Drive time for Collection Only (in hours)?"), validators=[DataRequired()])
    location = StringField(_l("Postcode for Collection Only"), validators=[DataRequired()])
    submit2 = SubmitField(_l('Change'))

class WeddingForm(FlaskForm):
    code = StringField(_l(''), validators=[DataRequired()])
    submit = SubmitField(_l('RSVP'))


