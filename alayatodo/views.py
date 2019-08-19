from alayatodo import app
from flask import (
    g,
    redirect,
    render_template,
    request,
    session,
    flash,
    url_for,
    make_response
    )
import json
from collections import OrderedDict
from .models import db, User, Todo


@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l.decode('utf-8') for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')

    user = db.session.query(User).filter(User.username == username).filter(User.password == password).first()

    if user:
        session['user'] = user.serialize
        session['logged_in'] = True
        response = make_response(redirect('/todo'))
    else:
        response = make_response(redirect('/login'))
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>', methods=['GET'])
def todo(id):
    if not session.get('logged_in'):
        return redirect('/login')
    todo = db.session.query(Todo).get(id)
    if todo is None:
        flash("Did not find todo with this id.")
        return redirect('/todo')
    return render_template('todo.html', todo=todo)


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
def todos():
    if not session.get('logged_in'):
        return redirect('/login')
    todos = db.session.query(Todo).filter(Todo.user_id == session['user']['id']).filter(Todo.todo_status == False).all()
    if len(todos) <= 5:
        return render_template('todos.html', todos=todos)
    else:
        return redirect('/todo/page/')



@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
def todos_POST():
    if not session.get('logged_in'):
        return redirect('/login')
    description = request.form.get('description', '')
    if not description.strip():
        flash("Cannot add a todo with no description.")
    else:
        todo = Todo(user_id=session['user']['id'], description=description, todo_status=False)
        db.session.add(todo)
        db.session.commit()
        flash("Added a new todo successfully.")

        # If has multiple pages, redirect to last page after addition
        count = db.session.query(Todo).filter(Todo.user_id == session['user']['id']).filter(Todo.todo_status == False).count()
        if count > 5:
            # Page number is the ceiling division of todos count
            response = make_response(redirect(url_for('todo_paginated', page=(count+4)//5)))
        else:
            response = make_response(redirect('/todo'))
        response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response



@app.route('/todo/<id>', methods=['POST'])
def todo_delete(id):
    if not session.get('logged_in'):
        return redirect('/login')
    todo = db.session.query(Todo).get(id)
    db.session.delete(todo)
    db.session.commit()
    flash("Deleted a todo successfully.")
    return redirect('/todo')


@app.route('/todo_completed/<id>', methods=['POST'])
def todo_completed(id):
    if not session.get('logged_in'):
        return redirect('/login')
    db.session.query(Todo).filter(Todo.id == id).update({Todo.todo_status: True}, synchronize_session = False)
    db.session.commit()
    return redirect('/todo')


@app.route('/todo/<id>/json', methods=['GET'])
def todo_json(id):
    if not session.get('logged_in'):
        return redirect('/login')
    todo = db.session.query(Todo).get(id)
    json_string = json.dumps(todo.serialize)
    return render_template('json.html', json_string=json_string)


TODOS_PER_PAGE = 5
@app.route('/todo/page/', defaults={'page': 1}, methods=['GET'])
@app.route('/todo/page/<int:page>', methods=['GET'])
def todo_paginated(page):
    if not session.get('logged_in'):
        return redirect('/login')

    count = db.session.query(Todo).count()
    pagination = db.session.query(Todo).filter(Todo.user_id == session['user']['id']).filter(Todo.todo_status == False).paginate(page, TODOS_PER_PAGE, count)

    return render_template('todos.html', pagination=pagination, todos=pagination.items)
