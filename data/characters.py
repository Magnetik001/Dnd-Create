import sqlalchemy
from sqlalchemy import JSON
from .db_session import SqlAlchemyBase

class Character(SqlAlchemyBase):
    __tablename__ = "characters"

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=False)

    char_name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    race = sqlalchemy.Column(sqlalchemy.String)
    class_level = sqlalchemy.Column(sqlalchemy.String)
    background = sqlalchemy.Column(sqlalchemy.String)
    alignment = sqlalchemy.Column(sqlalchemy.String)
    xp = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    str_score = sqlalchemy.Column(sqlalchemy.Integer, default=10)
    dex_score = sqlalchemy.Column(sqlalchemy.Integer, default=10)
    con_score = sqlalchemy.Column(sqlalchemy.Integer, default=10)
    int_score = sqlalchemy.Column(sqlalchemy.Integer, default=10)
    wis_score = sqlalchemy.Column(sqlalchemy.Integer, default=10)
    cha_score = sqlalchemy.Column(sqlalchemy.Integer, default=10)

    ac = sqlalchemy.Column(sqlalchemy.Integer)
    speed = sqlalchemy.Column(sqlalchemy.Integer, default=30)
    prof_bonus = sqlalchemy.Column(sqlalchemy.Integer, default=2)
    hp_current = sqlalchemy.Column(sqlalchemy.Integer, default=10)
    hp_max = sqlalchemy.Column(sqlalchemy.Integer, default=10)
    hp_temp = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    attacks = sqlalchemy.Column(JSON, default=list)
    features = sqlalchemy.Column(sqlalchemy.Text)
    equipment = sqlalchemy.Column(sqlalchemy.Text)
    coins = sqlalchemy.Column(JSON, default={"copper": 0, "silver": 0, "electrum": 0, "gold": 0, "platinum": 0})

    personality_traits = sqlalchemy.Column(sqlalchemy.Text)
    ideals = sqlalchemy.Column(sqlalchemy.Text)
    bonds = sqlalchemy.Column(sqlalchemy.Text)
    flaws = sqlalchemy.Column(sqlalchemy.Text)

    created_at = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.func.now())
    updated_at = sqlalchemy.Column(sqlalchemy.DateTime, default=sqlalchemy.func.now(), onupdate=sqlalchemy.func.now())

    owner = sqlalchemy.orm.relationship("User", back_populates="characters")