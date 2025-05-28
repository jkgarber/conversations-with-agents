from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from incontext.auth import login_required
from incontext.db import get_db

bp = Blueprint('agents', __name__, url_prefix='/agents')

@bp.route('/')
# @login_required
def index():
    db = get_db()
    agents = db.execute(
        'SELECT a.id, model, name, role, instructions, created, creator_id, username'
        ' FROM agents a JOIN users u ON a.creator_id = u.id'
        ' ORDER BY created DESC'
    ).fetchall()
    return render_template('agents/index.html', agents=agents)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        model = request.form['model']
        name = request.form['name']
        role = request.form['role']
        instructions = request.form['instructions']
        error = None

        if not model or not name or not role or not instructions:
            error = 'Model, name, role, and instructions are all required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO agents (model, name, role, instructions, creator_id)'
                ' VALUES (?, ?, ?, ?, ?)',
                (model, name, role, instructions, g.user['id'])
            )
            db.commit()
            return redirect(url_for('agents.index'))

    return render_template('agents/create.html')

def get_agent(id, check_creator=True): # The check_author parameter means this function is also useful for getting the context in general, not just for the update view e.g. displaying a single context on a "view context" page.
    agent = get_db().execute(
        'SELECT a.id, model, name, role, instructions, created, creator_id, username'
        ' FROM agents a JOIN users u ON a.creator_id = u.id'
        ' WHERE a.id = ?',
        (id,)
    ).fetchone()

    if agent is None:
        abort(404, f"Agent id {id} doesn't exist.") # abort() will raise a special exception that returns an HTTP status code. It takes an optional message to show with the error. 404 means "Not Found".

    if check_creator and agent['creator_id'] != g.user['id']:
        abort(403) # 403 means Forbidden. 401 means "Unauthorized" but you redirect to the login page instead of returning that status.

    return agent

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update(id): # id corresponds to the <int:id> in the route. Flask will capture the "id" from the url, ensure it's an int, and pass it as the id argument. To generate a URL to the update page, `url_for()` needs to be passed the `id` such as `url_for('context.update', id=context['id']).
    agent = get_agent(id)

    if request.method == 'POST':
        model = request.form['model']
        name = request.form['name']
        role = request.form['role']
        instructions = request.form['instructions']
        error = None

        if not model or not name or not role or not instructions:
            error = 'Model, name, role, and instructions are all required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE agents SET model = ?, name = ?, role = ?, instructions = ?'
                ' WHERE id = ?',
                (model, name, role, instructions, id)
            )
            db.commit()
            return redirect(url_for('agents.index'))
    
    return render_template('agents/update.html', agent=agent)

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete(id):
    get_agent(id)
    db = get_db()
    db.execute('DELETE FROM agents WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('agents.index'))
