from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, SubmitField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class RegisterForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])

    password = PasswordField('Пароль', validators=[
        DataRequired(),
        Length(min=6, message='Пароль должен содержать не менее 6 символов')
    ])

    repeat_password = PasswordField('Повторите пароль', validators=[
        DataRequired(),
        Length(min=6, message='Пароль должен содержать не менее 6 символов'),
        EqualTo('password', message='Пароли должны совпадать')
    ])

    email = EmailField('Почта', validators=[DataRequired(), Email(message='Введите корректный email')])
    submit = SubmitField('Зарегистрироваться')