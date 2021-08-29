from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, InputRequired, NumberRange, EqualTo


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить')
    submit = SubmitField('Вход')


class RegistrationForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Добавить аккаунт')


class DeleteAccountForm(FlaskForm):
    user_id = IntegerField('ID Аккаунта', validators=[InputRequired(), NumberRange(min=0)])

    confirm_delete = BooleanField('Подтверждение удаления', default=False, validators=[DataRequired()])
    submit = SubmitField('Удалить аккаунт')
