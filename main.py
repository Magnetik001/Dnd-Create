from flask_login import LoginManager, login_user, logout_user, current_user
from flask import Flask, render_template, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from data import db_session
from data.users import User
from forms.loginForm import LoginForm
from forms.registerForm import RegisterForm

app = Flask(__name__)
app.config["SECRET_KEY"] = 'orHqAlTVurBbiQrs'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    try:
        return db_sess.get(User, int(user_id))
    finally:
        db_sess.close()


@app.route("/")
def index():
    return render_template("index.html", user=current_user)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        try:
            user = db_sess.query(User).filter(User.login == form.login.data).first()

            if user and check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect("/")

            return render_template('login.html', message="Неправильный логин или пароль", form=form)
        finally:
            db_sess.close()
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        try:
            existing_user = db_sess.query(User).filter(
                (User.login == form.login.data) | (User.email == form.email.data)
            ).first()

            if existing_user:
                return render_template("register.html", title="Регистрация", form=form,
                                       message="Пользователь с таким логином или почтой уже существует")

            user = User()
            user.login = form.login.data
            user.email = form.email.data
            user.password = generate_password_hash(form.password.data)

            db_sess.add(user)
            db_sess.commit()

            return redirect(url_for('index'))
        finally:
            db_sess.close()

    return render_template("register.html", title="Регистрация", form=form)


@app.route("/profile")
def profile():
    return "profile"


@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")


@app.route("/create_character")
def create_character():
    return render_template("character_sheet.html")


if __name__ == "__main__":
    db_session.global_init("db/busyness.db")
    app.run(port=8080, host="127.0.0.1", debug=True)