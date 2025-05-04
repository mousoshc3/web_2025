from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, EmailField, BooleanField, SelectField, \
    RadioField
from wtforms.validators import DataRequired


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    user_class = SelectField('Класс', choices=['10', '11'], default='10')
    submit = SubmitField('Создать аккаунт')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class QuestionForm(FlaskForm):
    choces_button = RadioField(choices=[(2, 'Да'), (0, 'Нет'), (1, 'Возможно')])
    submit = SubmitField('Сохранить')
    back = SubmitField('Вернуться')


class AdminForm(FlaskForm):
    search_choose = SelectField('Фильтр', choices=['Никнейм', 'Почта', 'Дата создания', 'Класс', 'Права', 'Анкета'], default='Почта')
    search_field = StringField('Поиск')
    submit = SubmitField('Найти')


class NewForm(FlaskForm):
    theme = StringField('Тема анкеты')
    short_description = StringField('Краткое описание')
