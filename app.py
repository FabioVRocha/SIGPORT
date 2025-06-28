from datetime import datetime

from flask import (
    Flask,
    jsonify,
    request,
    abort,
    render_template,
    redirect,
    url_for,
    session,
)

from config import DATABASE_URI, SECRET_KEY
from models import db, User, Entry, Exit, Schedule, Permission
from functools import wraps


def normalize_plate(plate: str) -> str:
    """Return the plate in uppercase without dashes or spaces."""
    return plate.replace("-", "").replace(" ", "").upper()


def find_open_entry(plate: str):
    """Return the most recent open entry for the given plate or None."""
    plate_norm = normalize_plate(plate)
    return (
        Entry.query.filter(
            db.func.replace(
                db.func.replace(db.func.upper(Entry.plate), '-', ''),
                ' ',
                '',
            )
            == plate_norm
        )
        .outerjoin(Exit)
        .filter(Exit.id.is_(None))
        .order_by(Entry.timestamp.desc())
        .first()
    )


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = SECRET_KEY
    db.init_app(app)

    ROUTINE_LABELS = {
        'entries': 'Entrada',
        'exits': 'Saída',
        'schedules': 'Agendar Saída',
        'cadastro': 'Cadastro',
        'access_control': 'Controle de Acesso',
    }

    def login_required(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login_form'))
            return f(*args, **kwargs)
        return wrapper

    def permission_required(routine):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                if session.get('user_type') == 'Administrador':
                    return f(*args, **kwargs)
                if routine not in session.get('permissions', []):
                    abort(403)
                return f(*args, **kwargs)
            return wrapper
        return decorator

    @app.route('/')
    def index():
        return redirect(url_for('login_form'))

    @app.route('/index')
    @login_required
    def main_menu():
        perms = session.get('permissions', [])
        return render_template('index.html', permissions=perms, is_admin=session.get('user_type') == 'Administrador')

    @app.route('/cadastro')
    @login_required
    @permission_required('cadastro')
    def cadastro_menu():
        return render_template('cadastro.html', is_admin=session.get('user_type') == 'Administrador')

    @app.route('/access_control', methods=['GET', 'POST'])
    @login_required
    def access_control_menu():
        if session.get('user_type') != 'Administrador':
            abort(403)
        if request.method == 'POST':
            user_id = int(request.form['user_id'])
            selected = request.form.getlist('permissions')
            Permission.query.filter_by(user_id=user_id).delete()
            for perm in selected:
                db.session.add(Permission(user_id=user_id, routine=perm))
            db.session.commit()
            return redirect(url_for('access_control_menu', user_id=user_id))
        users = User.query.all()
        selected_id = request.args.get('user_id', type=int)
        if not selected_id and users:
            selected_id = users[0].id
        perms = set(p.routine for p in Permission.query.filter_by(user_id=selected_id))
        return render_template('access_control.html', users=users, selected_id=selected_id, user_perms=perms, routines=ROUTINE_LABELS)

    @app.route('/login', methods=['GET'])
    def login_form():
        return render_template('login.html')

    @app.route('/users/new')
    @login_required
    @permission_required('cadastro')
    def user_form():
        return render_template('user_form.html')

    @app.route('/entries/new')
    @login_required
    @permission_required('entries')
    def entry_form():
        return render_template('entry_form.html')

    @app.route('/entries/list')
    @login_required
    @permission_required('entries')
    def entries_list_page():
        entries = Entry.query.order_by(Entry.timestamp.desc()).all()
        return render_template('entries_list.html', entries=entries)

    @app.route('/exits/new')
    @login_required
    @permission_required('exits')
    def exit_lookup():
        return render_template('exit_lookup.html')

    @app.route('/exits/list')
    @login_required
    @permission_required('exits')
    def exits_list_page():
        exits = Exit.query.order_by(Exit.timestamp.desc()).all()
        schedules = Schedule.query.order_by(Schedule.scheduled_for.asc()).all()
        open_for_schedule = {}
        for s in schedules:
            if s.status == 'Pendente':
                entry = s.entry
                if entry is None or entry.exit:
                    entry = find_open_entry(s.plate)
                open_for_schedule[s.id] = entry is not None
            else:
                open_for_schedule[s.id] = False
        return render_template(
            'exit_list.html',
            exits=exits,
            schedules=schedules,
            open_for_schedule=open_for_schedule,
        )

    @app.route('/entries/<int:entry_id>/exit/new')
    @login_required
    @permission_required('exits')
    def exit_form(entry_id):
        entry = Entry.query.get_or_404(entry_id)
        return render_template('exit_form.html', entry=entry)

    @app.route('/schedules/new')
    @login_required
    @permission_required('schedules')
    def schedule_form():
        return render_template('schedule_form.html')

    @app.route('/schedules/<int:schedule_id>/exit/new')
    @login_required
    @permission_required('schedules')
    def schedule_exit_form(schedule_id):
        schedule = Schedule.query.get_or_404(schedule_id)
        # locate a related open entry to avoid submitting the form when none exists
        entry = schedule.entry
        if entry is None or entry.exit:
            entry = find_open_entry(schedule.plate)
        if not entry:
            abort(400, "No corresponding entry available")
        return render_template('schedule_exit_form.html', schedule=schedule)

    @app.route('/users', methods=['POST'])
    @login_required
    @permission_required('cadastro')
    def create_user():
        data = request.get_json() if request.is_json else request.form
        if not data:
            abort(400, 'Missing payload')
        user = User(cpf=data['cpf'], name=data['name'], username=data['username'], type=data.get('type', 'Usuário'))
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
        data = request.get_json() if request.is_json else request.form
        user = User.query.filter_by(username=data['username']).first()
        if user and user.check_password(data['password']):
            session['user_id'] = user.id
            session['user_type'] = user.type
            session['permissions'] = [p.routine for p in user.permissions]
            if request.is_json:
                return jsonify({'message': 'login ok'})
            return redirect(url_for('main_menu'))
        abort(401, 'Invalid credentials')

    @app.route('/entries', methods=['POST'])
    @login_required
    @permission_required('entries')
    def create_entry():
        data = request.get_json() if request.is_json else request.form
        # check if plate already inside
        open_entry = (
            Entry.query.filter_by(plate=data['plate'])
            .outerjoin(Exit)
            .filter(Exit.id.is_(None))
            .first()
        )
        if open_entry:
            abort(400, 'Plate already has an open entry')
        required_fields = ['release', 'activity', 'observation', 'photo_plate', 'photo_driver']
        for field in required_fields:
            if not data.get(field):
                abort(400, f'{field} is required')

        entry = Entry(
            plate=data['plate'],
            driver=data['driver'],
            passenger=data.get('passenger'),
            release=data['release'],
            activity=data['activity'],
            observation=data['observation'],
            photo_plate=data['photo_plate'],
            photo_driver=data['photo_driver'],
            photo_content=data.get('photo_content'),
            photo_document=data.get('photo_document'),
        )
        db.session.add(entry)
        db.session.commit()
        if request.is_json:
            return jsonify({'id': entry.id}), 201
        return redirect(url_for('entries_list_page'))

    @app.route('/entries', methods=['GET'])
    def list_entries():
        entries = Entry.query.all()
        result = []
        for e in entries:
            result.append({'id': e.id, 'timestamp': e.timestamp.isoformat(), 'plate': e.plate, 'driver': e.driver})
        return jsonify(result)

    @app.route('/entries/<int:entry_id>', methods=['DELETE'])
    @login_required
    @permission_required('entries')
    def delete_entry(entry_id):
        entry = Entry.query.get_or_404(entry_id)
        if entry.exit:
            abort(400, 'Cannot delete entry with exit')
        db.session.delete(entry)
        db.session.commit()
        return '', 204

    @app.route('/entries/<int:entry_id>/exit', methods=['POST'])
    @login_required
    @permission_required('exits')
    def create_exit(entry_id):
        entry = Entry.query.get_or_404(entry_id)
        if entry.exit:
            abort(400, 'Exit already registered for this entry')
        data = request.get_json() if request.is_json else request.form
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
    @login_required
    @permission_required('schedules')
    def create_schedule():
        data = request.get_json() if request.is_json else request.form
        schedule = Schedule(
            scheduled_for=datetime.fromisoformat(data['scheduled_for']),
            plate=data['plate'],
            driver=data['driver'],
            activity=data.get('activity'),
            observation=data.get('observation'),
        )
        plate_norm = normalize_plate(schedule.plate)
        open_entry = (
            Entry.query.filter(
                db.func.replace(
                    db.func.replace(db.func.upper(Entry.plate), '-', ''),
                    ' ',
                    '',
                )
                == plate_norm
            )
            .outerjoin(Exit)
            .filter(Exit.id.is_(None))
            .order_by(Entry.timestamp.desc())
            .first()
        )
        if open_entry:
            schedule.entry = open_entry
        db.session.add(schedule)
        db.session.commit()
        if request.is_json:
            return jsonify({'id': schedule.id}), 201
        return redirect(url_for('exits_list_page'))

    @app.route('/schedules', methods=['GET'])
    def list_schedules():
        schedules = Schedule.query.all()
        result = []
        for s in schedules:
            result.append({'id': s.id, 'scheduled_for': s.scheduled_for.isoformat(), 'plate': s.plate, 'driver': s.driver, 'status': s.status})
        return jsonify(result)

    @app.route('/schedules/<int:schedule_id>/create_exit', methods=['POST'])
    @login_required
    @permission_required('exits')
    def schedule_to_exit(schedule_id):
        schedule = Schedule.query.get_or_404(schedule_id)
        if schedule.status == 'Realizado':
            abort(400, 'Schedule already processed')
        data = request.get_json() if request.is_json else request.form
        entry = schedule.entry
        if entry is None or entry.exit:
            entry = find_open_entry(schedule.plate)
        if not entry:            
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
        if request.is_json:
            return jsonify({'exit_id': exit_record.id}), 201
        return redirect(url_for('exits_list_page'))

    return app


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0')