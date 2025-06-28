from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Entry(db.Model):
    __tablename__ = 'entries'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    plate = db.Column(db.String(20), nullable=False)
    driver = db.Column(db.String(120), nullable=False)
    passenger = db.Column(db.String(120))
    release = db.Column(db.String(120), nullable=False)
    activity = db.Column(db.String(120), nullable=False)
    observation = db.Column(db.Text, nullable=False)
    photo_plate = db.Column(db.Text, nullable=False)
    photo_driver = db.Column(db.Text, nullable=False)
    photo_content = db.Column(db.Text)
    photo_document = db.Column(db.Text)

    exit = db.relationship('Exit', uselist=False, back_populates='entry')


class Exit(db.Model):
    __tablename__ = 'exits'

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    entry_id = db.Column(db.Integer, db.ForeignKey('entries.id'), unique=True, nullable=False)
    plate = db.Column(db.String(20), nullable=False)
    driver = db.Column(db.String(120), nullable=False)
    passenger = db.Column(db.String(120))
    release = db.Column(db.String(120))
    activity = db.Column(db.String(120))
    observation = db.Column(db.Text)
    photo_plate = db.Column(db.Text)
    photo_driver = db.Column(db.Text)
    photo_content = db.Column(db.Text)
    photo_document = db.Column(db.Text)

    entry = db.relationship('Entry', back_populates='exit')


class Schedule(db.Model):
    __tablename__ = 'schedules'

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    scheduled_for = db.Column(db.DateTime, nullable=False)
    plate = db.Column(db.String(20), nullable=False)
    driver = db.Column(db.String(120), nullable=False)
    activity = db.Column(db.String(120))
    status = db.Column(db.String(20), default='Pendente', nullable=False)
    observation = db.Column(db.Text)