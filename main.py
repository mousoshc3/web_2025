from flask import Flask, jsonify
from data import db_session
from data.users import User
from flask import render_template
from forms.user import RegisterForm, LoginForm, QuestionForm, AdminForm
from data.answers import Answers
from data.questions import Questions
from flask import redirect, request, abort
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from data import db_session, news_api
from flask import make_response
import datetime
import requests



a = {i:x for i, x in enumerate(['Да', 'Нет', 'Возможно'])}
b = {x:i for i, x in enumerate(['Да', 'Нет', 'Возможно'])}
ANSWERS_DICT = a | b

# f = [x.decode('utf-8').split('$$$$$') for x in open('proffesions.txt', 'rb').readlines()]
# a = {key:value[:-2] if '\r' in value else value for key, value in f}
# b = {value:key for key, value in a.items()}
# QUESTIONS_DICT = a | b

SEARCH_DICT = {
    'Никнейм':'name',
    'Почта':'email',
    'Дата создания':'created_date',
    'Класс':'user_class',
    'Права':'special_rights',
    'Анкета':'completed',
    'Начато':0,
    'Завершено':1
}


convert_prof_id = {
    'аппаратчик производства': 497,
    'инженер по качеству': 415,
    'инженер-химик': 1398,
    'метролог': 185,
    'техник-технолог в химической и биохимической промышленности': 1920,
    'начальник сектора освоения скважин': 673,
    'инженер по бурению': 381
}


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def get_results(result, question):
    professions_keys = set()
    for quest in question.split('|'):
        for elem in quest.split('$$$$$')[1].split(';'):
            professions_keys.add(elem)
    sl = {key:0 for key in professions_keys}
    for i, value in enumerate(result):
        for elem in question.split('|')[i].split('$$$$$')[1].split(';'):
            sl[elem] += int(value)
    return sl


def get_the_univesities(id, num=1):
    sp_univ = []
    start_ind = 0
    request_str = requests.get(f'https://vuzopedia.ru/professii/{id}/vuzy').content.decode('utf-8')
    for i in range(num):
        try:
            a_name = request_str.index('<div class="itemVuzTitle">', start_ind) + 47
            b_name = request_str.index('</div>', a_name) - 17
            name = request_str[a_name:b_name]

            a_img = request_str.index('<img', a_name - 500) + 36
            b_img = request_str.index('data-src', a_img) - 2
            img = request_str[a_img:b_img]

            sp_univ.append((name, img))
            start_ind = b_name + 200
        except Exception:
            return sp_univ
    return sp_univ


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            user_class=form.user_class.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        answers = Answers(
            answer='',
            user_id=max([int(us.id) for us in db_sess.query(User).all()])
        )
        db_sess.add(answers)
        db_sess.commit()
        return redirect('/login')
    return render_template("register.html", form=form, title='Регистрация')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.email == form.email.data).first()
    if form.validate_on_submit():
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            if user.special_rights == 1:
                return redirect('/admin_panel')
            return redirect("/question")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/register")


@app.route('/back')
@login_required
def back():
    db_sess = db_session.create_session()
    answer = db_sess.query(Answers).filter(current_user.get_id() == Answers.user_id).first()
    if answer.completed:
        return redirect('/results')
    if answer.current_question > 1:
        answer.current_question -=1
        answer.answer = answer.answer[:-1]
        db_sess.commit()
    return redirect("/question")


@app.route('/question', methods=['GET', 'POST'])
@login_required
def answer_question():
    form = QuestionForm()
    db_sess = db_session.create_session()
    answer = db_sess.query(Answers).filter(current_user.get_id() == Answers.user_id).first()
    if answer.completed == 1:
        return redirect('/results')
    if form.validate_on_submit():
        answer.current_question += 1
        answer.answer += form.choces_button.data
        db_sess.commit()
        if answer.current_question == len(db_sess.query(Questions).first().questions.split('|')) + 1:
            answer.completed = True
            answer.completed_date = datetime.datetime.now()
            db_sess.commit()
            return redirect('/results')
        return redirect('/question')
    text = [x.split('$$$$$') for x in db_sess.query(Questions).first().questions.split('|')]
    return render_template('form.html', form=form, question=answer.current_question, text=text[answer.current_question-1][0], title='Вопросы')


@app.route('/results', methods=['GET', 'POST'])
@login_required
def results():
    sp =[]
    db_sess = db_session.create_session()
    res = get_results(db_sess.query(Answers).filter(current_user.get_id() == Answers.user_id).first().answer, db_sess.query(Questions).first().questions)
    res = sorted(res.items(), key=lambda x: x[1], reverse=True)[:3]
    for elem in res:
        sp.append((elem[0], get_the_univesities(convert_prof_id[elem[0]], num=3)))
    print(sp)
    return render_template('results.html', title='Результат тестирования', universities=sp)


@app.route('/admin_panel', methods=['GET', 'POST'])
@login_required
def admin_panel():
    if current_user.is_authenticated:
        form = AdminForm()
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(current_user.get_id() == User.id).first()
        if user.special_rights == 0:
            return redirect('/question')
        sp = []
        for elem in db_sess.query(User).all():
            sp.append((elem, db_sess.query(Answers).filter(elem.id == Answers.user_id).first()))
        if form.validate_on_submit():
            if form.search_field.data:
                sp = []
                category = form.search_choose.data
                text = form.search_field.data
                if category in ('Никнейм', 'Почта', 'Дата создания', 'Класс', 'Права'):
                    b = eval(f"User.{SEARCH_DICT[category]}.like('%{text}%')")
                    for elem in db_sess.query(User).filter(b).all():
                        sp.append((elem, db_sess.query(Answers).filter(elem.id == Answers.user_id).first()))
                else:
                    for elem in db_sess.query(Answers).filter(Answers.completed == SEARCH_DICT[text]).all():
                        sp.append((db_sess.query(User).filter(User.id == elem.user_id).first(), elem))
        return render_template('admin panel.html', form=form, users=sp, title='Админская панель', lenght=len(sp))


@app.route('/new_form', methods=['GET', 'POST'])
@login_required
def new_form():
    return render_template('new_form.html')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


def main():
    db_session.global_init("db/users.db")
    # ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    # db_sess = db_session.create_session()
    # q = '|'.join(open('questions.txt', 'rb').read().decode('utf-8').split('\r\n'))
    # questions = Questions(theme='Профориентация', questions=q, short_description='Тестовая профориентационная анкета по востребованным проффесиям в ХМАО-Югре')
    # db_sess.add(questions)
    # db_sess.commit()
    # user = User(
    #     name='admin',
    #     email='admin@mail.ru',
    #     special_rights=1
    # )
    # user.set_password('admin_123')
    # db_sess.add(user)
    # db_sess.commit()
    # ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
    app.run(port=800)





if __name__ == '__main__':
    main()
