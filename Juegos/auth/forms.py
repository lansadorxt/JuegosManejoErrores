from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="Por favor, ingresa tu correo electrónico."),
        Email(message="El formato del correo es incorrecto.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Por favor, ingresa tu contraseña.")
    ])
    remember_me = BooleanField('Mantener sesión iniciada')
    submit = SubmitField('Ingresar')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message="El correo electrónico es obligatorio."),
        Email(message="El correo ingresado es incorrecto.")
    ])
    username = StringField('Username', validators=[
        DataRequired(message="El nombre de usuario es obligatorio."),
        Length(3, 64, message="El usuario debe tener entre 3 y 64 caracteres.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="La contraseña es obligatoria."),
        EqualTo('password2', message="Las contraseñas no coinciden, es incorrecto.")
    ])
    password2 = PasswordField('Confirmar Password', validators=[
        DataRequired(message="Por favor, confirma tu contraseña.")
    ])
    submit = SubmitField('Registrarse')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Este correo ya está registrado, es incorrecto.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Este nombre de usuario ya existe, es incorrecto.')