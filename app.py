from datetime import datetime

from flask import Flask, jsonify, request, abort

from config import DATABASE_URI, SECRET_KEY
from models import db, User, Entry, Exit, Schedule


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = SECRET_KEY
    db.init_app(app)

    @app.route('/users', methods=['POST'])
    def create_user():
        data = request.json
        if not data:
            abort(400, 'Missing JSON payload')
        user = User(cpf=data['cpf'], name=data['name'], username=data['username'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        return jsonify({'id': user.id}), 201

    @app.route('/users', methods=['GET'])
    def list_users():
        users = User.query.all()
        return jsonify([{'id': u.id, 'cpf': u.cpf, 'name': u.name, 'username': u.username} for u in users])

    @app.route('/login', methods=['POST'])
    def login():
        data = request.json
        user = User.query.filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            return jsonify({'message': 'login ok'})
        abort(401, 'Invalid credentials')

    @app.route('/entries', methods=['POST'])
    def create_entry():
        data = request.json
        # check if plate already inside
        open_entry = (
            Entry.query.filter_by(plate=data['plate'])
            .outerjoin(Exit)
            .filter(Exit.id.is_(None))
            .first()
        )
        if open_entry:
            abort(400, 'Plate already has an open entry')
        entry = Entry(
            plate=data['plate'],
            driver=data['driver'],
            passenger=data.get('passenger'),
            release=data.get('release'),
            activity=data.get('activity'),
            observation=data.get('observation'),
            photo_plate=data.get('photo_plate'),
            photo_driver=data.get('photo_driver'),
            photo_content=data.get('photo_content'),
            photo_document=data.get('photo_document'),
        )
        db.session.add(entry)
        db.session.commit()
        return jsonify({'id': entry.id}), 201

    @app.route('/entries', methods=['GET'])
    def list_entries():
        entries = Entry.query.all()
        result = []
        for e in entries:
            result.append({'id': e.id, 'timestamp': e.timestamp.isoformat(), 'plate': e.plate, 'driver': e.driver})
        return jsonify(result)

    @app.route('/entries/<int:entry_id>', methods=['DELETE'])
    def delete_entry(entry_id):
        entry = Entry.query.get_or_404(entry_id)
        if entry.exit:
            abort(400, 'Cannot delete entry with exit')
        db.session.delete(entry)
        db.session.commit()
        return '', 204

    @app.route('/entries/<int:entry_id>/exit', methods=['POST'])
    def create_exit(entry_id):
        entry = Entry.query.get_or_404(entry_id)
        if entry.exit:
            abort(400, 'Exit already registered for this entry')
        data = request.json
        exit_record = Exit(
            entry=entry,
            plate=data.get('plate', entry.plate),
            driver=data.get('driver', entry.driver),
            passenger=data.get('passenger', entry.passenger),
            release=data.get('release', entry.release),
            activity=data.get('activity', entry.activity),
            observation=data.get('observation'),
            photo_plate=data.get('photo_plate'),
            photo_driver=data.get('photo_driver'),
            photo_content=data.get('photo_content'),
            photo_document=data.get('photo_document'),
        )
        db.session.add(exit_record)
        db.session.commit()
        return jsonify({'id': exit_record.id}), 201

    @app.route('/exits', methods=['GET'])
    def list_exits():
        exits = Exit.query.all()
        result = []
        for ex in exits:
            result.append({'id': ex.id, 'timestamp': ex.timestamp.isoformat(), 'plate': ex.plate, 'driver': ex.driver})
        return jsonify(result)

    @app.route('/schedules', methods=['POST'])
    def create_schedule():
        data = request.json
        schedule = Schedule(
            scheduled_for=datetime.fromisoformat(data['scheduled_for']),
            plate=data['plate'],
            driver=data['driver'],
            activity=data.get('activity'),
            observation=data.get('observation'),
        )
        db.session.add(schedule)
        db.session.commit()
        return jsonify({'id': schedule.id}), 201

    @app.route('/schedules', methods=['GET'])
    def list_schedules():
        schedules = Schedule.query.all()
        result = []
        for s in schedules:
            result.append({'id': s.id, 'scheduled_for': s.scheduled_for.isoformat(), 'plate': s.plate, 'driver': s.driver, 'status': s.status})
        return jsonify(result)

    @app.route('/schedules/<int:schedule_id>/create_exit', methods=['POST'])
    def schedule_to_exit(schedule_id):
        schedule = Schedule.query.get_or_404(schedule_id)
        if schedule.status == 'Realizado':
            abort(400, 'Schedule already processed')
        data = request.json or {}
        entry = Entry.query.filter_by(plate=schedule.plate, driver=schedule.driver).order_by(Entry.timestamp.desc()).first()
        if not entry or entry.exit:
            abort(400, 'No corresponding entry available')
        exit_record = Exit(
            entry=entry,
            plate=entry.plate,
            driver=entry.driver,
            passenger=data.get('passenger'),
            release=data.get('release'),
            activity=schedule.activity,
            observation=data.get('observation'),
            photo_plate=data.get('photo_plate'),
            photo_driver=data.get('photo_driver'),
            photo_content=data.get('photo_content'),
            photo_document=data.get('photo_document'),
        )
        db.session.add(exit_record)
        schedule.status = 'Realizado'
        db.session.commit()
        return jsonify({'exit_id': exit_record.id}), 201

    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')