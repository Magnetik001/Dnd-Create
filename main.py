from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask import Flask, render_template, redirect, url_for,  send_from_directory, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
import json
import re
from data import db_session
from data.users import User
from forms.loginForm import LoginForm
from forms.registerForm import RegisterForm
from data.characters import Character
import os, json, requests
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import make_response

app = Flask(__name__)
app.config["SECRET_KEY"] = 'orHqAlTVurBbiQrs'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
UPLOAD_FOLDER = os.path.join('static', 'uploads', 'avatars')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024
DND_API_CACHE = {}


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    try:
        return db_sess.get(User, int(user_id))
    finally:
        db_sess.close()


@app.route("/")
def index():
    db_sess = db_session.create_session()
    try:
        characters = db_sess.query(Character).filter(
            Character.user_id == current_user.id
        ).all() if current_user.is_authenticated else []

        stats = {
            'total': len(characters),
            'avg_level': 1,
            'total_xp': sum(c.xp or 0 for c in characters)
        }

        levels = []
        for char in characters:
            if char.class_level:
                match = re.search(r'\d+', str(char.class_level))
                if match:
                    levels.append(int(match.group()))

        if levels:
            stats['avg_level'] = round(sum(levels) / len(levels))

        return render_template(
            "index.html",
            user=current_user,
            characters=characters,
            stats=stats
        )
    finally:
        db_sess.close()


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
            login_user(user)
            return redirect(url_for('index'))
        finally:
            db_sess.close()
    return render_template("register.html", title="Регистрация", form=form)


@app.route("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/create", methods=["GET", "POST"])
@login_required
def create_character():
    if request.method == "POST":
        db_sess = db_session.create_session()
        try:
            char = Character(user_id=current_user.id)
            char.char_name = request.form.get("char_name") or "Безымянный герой"
            char.race = request.form.get("race")
            char.class_level = request.form.get("class_level")
            char.background = request.form.get("background")
            char.alignment = request.form.get("alignment")
            char.xp = int(request.form.get("xp") or 0)

            char.str_score = int(request.form.get("str_score")
                                 or 10)
            char.dex_score = int(request.form.get("dex_score")
                                 or 10)
            char.con_score = int(request.form.get("con_score")
                                 or 10)
            char.int_score = int(request.form.get("int_score")
                                 or 10)
            char.wis_score = int(request.form.get("wis_score")
                                 or 10)
            char.cha_score = int(request.form.get("cha_score")
                                 or 10)

            char.ac = int(request.form.get("ac")
                          or 10)
            char.speed = int(request.form.get("speed")
                             or 30)
            char.prof_bonus = int(request.form.get("prof_bonus")
                                  or 2)
            char.hp_current = int(request.form.get("hp_current")
                                  or 10)
            char.hp_max = int(request.form.get("hp_max")
                              or 10)
            char.hp_temp = int(request.form.get("hp_temp")
                               or 0)

            attacks = []
            for i in range(1, 4):
                name = request.form.get(f"atk{i}_name")
                bonus = request.form.get(f"atk{i}_bonus")
                dmg = request.form.get(f"atk{i}_dmg")
                if name or bonus or dmg:
                    attacks.append({"name": name, "bonus": bonus, "dmg": dmg})
            char.attacks = attacks

            char.features = request.form.get("features_traits")
            char.equipment = request.form.get("equipment")
            char.personality_traits = request.form.get("personality_traits")
            char.ideals = request.form.get("ideals")
            char.bonds = request.form.get("bonds")
            char.flaws = request.form.get("flaws")

            db_sess.add(char)
            db_sess.commit()
            return redirect(url_for('index'))
        finally:
            db_sess.close()

    return render_template("character_sheet.html")


@app.route("/character/<int:char_id>", methods=["GET", "POST"])
@login_required
def edit_character(char_id):
    db_sess = db_session.create_session()
    try:
        char = db_sess.query(Character).filter(
            Character.id == char_id,
            Character.user_id == current_user.id
        ).first()

        if not char:
            return redirect(url_for('index'))

        if request.method == "POST":
            char.char_name = request.form.get("char_name") or "Безымянный герой"
            char.race = request.form.get("race")
            char.class_level = request.form.get("class_level")
            char.background = request.form.get("background")
            char.alignment = request.form.get("alignment")
            char.xp = int(request.form.get("xp") or 0)

            char.str_score = int(request.form.get("str_score")
                                 or 10)
            char.dex_score = int(request.form.get("dex_score")
                                 or 10)
            char.con_score = int(request.form.get("con_score")
                                 or 10)
            char.int_score = int(request.form.get("int_score")
                                 or 10)
            char.wis_score = int(request.form.get("wis_score")
                                 or 10)
            char.cha_score = int(request.form.get("cha_score")
                                 or 10)

            char.ac = int(request.form.get("ac")
                          or 10)
            char.speed = int(request.form.get("speed")
                             or 30)
            char.prof_bonus = int(request.form.get("prof_bonus")
                                  or 2)
            char.hp_current = int(request.form.get("hp_current")
                                  or 10)
            char.hp_max = int(request.form.get("hp_max")
                              or 10)
            char.hp_temp = int(request.form.get("hp_temp")
                               or 0)

            attacks = []
            for i in range(1, 4):
                name = request.form.get(f"atk{i}_name")
                bonus = request.form.get(f"atk{i}_bonus")
                dmg = request.form.get(f"atk{i}_dmg")
                if name or bonus or dmg:
                    attacks.append({"name": name, "bonus": bonus, "dmg": dmg})
            char.attacks = attacks

            char.features = request.form.get("features_traits")
            char.equipment = request.form.get("equipment")
            char.personality_traits = request.form.get("personality_traits")
            char.ideals = request.form.get("ideals")
            char.bonds = request.form.get("bonds")
            char.flaws = request.form.get("flaws")

            db_sess.commit()
            return redirect(url_for('index'))

        return render_template("character_sheet.html", character=char)
    finally:
        db_sess.close()


@app.route("/character/<int:char_id>/delete", methods=["POST"])
@login_required
def delete_character(char_id):
    db_sess = db_session.create_session()
    try:
        char = db_sess.query(Character).filter(
            Character.id == char_id,
            Character.user_id == current_user.id
        ).first()
        if char:
            db_sess.delete(char)
            db_sess.commit()
    finally:
        db_sess.close()
    return redirect(url_for('index'))


@app.route('/export/<int:char_id>', methods=['GET'])
@login_required
def export_character(char_id):
    db_sess = db_session.create_session()
    try:
        char = db_sess.query(Character).filter(
            Character.id == char_id, Character.user_id == current_user.id
        ).first()
        if not char:
            return redirect(url_for('index'))

        data = {c.name: getattr(char, c.name)
                for c in char.__table__.columns}
        json_str = json.dumps(data, ensure_ascii=False, indent=2, default=str)
        response = jsonify(json.loads(json_str))
        response.headers["Content-Disposition"] = f"attachment; filename={char.char_name}_sheet.json"
        return response
    finally:
        db_sess.close()


@app.route('/api/characters', methods=['GET'])
@login_required
def api_get_characters():
    db_sess = db_session.create_session()
    try:
        chars = (db_sess.query(Character)
                 .filter(Character.user_id == current_user.id).all())
        return jsonify([{c.name: getattr(ch, c.name) for c in ch.__table__.columns} for ch in chars])
    finally:
        db_sess.close()


@app.route('/api/characters/<int:char_id>', methods=['GET'])
@login_required
def api_get_character(char_id):
    db_sess = db_session.create_session()
    try:
        char = db_sess.query(Character).filter(
            Character.id == char_id, Character.user_id == current_user.id
        ).first()
        if not char:
            return jsonify({"error": "Character not found"}), 404
        return jsonify({c.name: getattr(char, c.name) for c in char.__table__.columns})
    finally:
        db_sess.close()


@app.route('/api/dnd/races', methods=['GET'])
def api_dnd_races():
    if 'races' in DND_API_CACHE and (datetime.now() - DND_API_CACHE['time']).seconds < 3600:
        return jsonify(DND_API_CACHE['data'])
    try:
        resp = requests.get('https://www.dnd5eapi.co/api/races', timeout=5)
        resp.raise_for_status()
        DND_API_CACHE['data'] = resp.json()
        DND_API_CACHE['time'] = datetime.now()
        return jsonify(resp.json())
    except requests.RequestException as e:
        return jsonify({"error": f"Внешний API недоступен: {str(e)}"}), 502


if __name__ == "__main__":
    db_session.global_init("db/busyness.db")
    app.run(port=8080, host="127.0.0.1", debug=True)