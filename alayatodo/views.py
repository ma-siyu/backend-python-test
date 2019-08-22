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
from .recaptcha import recaptcha
from .login import login_check


@app.route('/')
def home():
    with app.open_resource('../README.md', mode='r') as f:
        readme = "".join(l.decode('utf-8') for l in f)
        return render_template('index.html', readme=readme)


@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
@recaptcha
def login_POST():
    username = request.form.get('username')
    password = request.form.get('password')
    user = db.session.query(User). \
           filter(User.username == username). \
           filter(User.password == password).first()

    if user and request.recaptcha_is_valid:
        session['user'] = user.serialize
        session['logged_in'] = True
        response = make_response(redirect('/todo'))
    else:
        response = make_response(redirect('/login'))
        if not user:
            flash("Username or password is wrong. Please try again.")

    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user', None)
    return redirect('/')


@app.route('/todo/<id>', methods=['GET'])
@app.route('/todo/<id>/', methods=['GET'])
@login_check
def todo(id):
    todo = db.session.query(Todo). \
           filter(Todo.user_id == session['user']['id']). \
           filter(Todo.id == id).first()
    if todo is None:
        flash("Did not find todo with this id.")
        return redirect('/todo')
    completed = todo.todo_status
    print(completed)
    return render_template('todo.html', todo=todo, completed=completed)


@app.route('/todo', methods=['GET'])
@app.route('/todo/', methods=['GET'])
@login_check
def todos():
    todos = db.session.query(Todo). \
            filter(Todo.user_id == session['user']['id']). \
            filter(Todo.todo_status == False).all()
    if len(todos) <= 5:
        return render_template('todos.html', todos=todos)
    else:
        return redirect('/todo/page/')



@app.route('/todo', methods=['POST'])
@app.route('/todo/', methods=['POST'])
@login_check
def todos_POST():
    description = request.form.get('description', '')
    if not description.strip():
        flash("Cannot add a todo with no description.")
        response = make_response(redirect('/todo'))
    else:
        todo = Todo(user_id=session['user']['id'],  \
               description=description, todo_status=False)
        db.session.add(todo)
        db.session.commit()
        flash("Added a new todo successfully.")

        # If has multiple pages, redirect to last page after addition
        count = db.session.query(Todo). \
                filter(Todo.user_id == session['user']['id']). \
                filter(Todo.todo_status == False).count()
        if count > 5:
            # Page number is the ceiling division of todos count
            response = make_response(redirect( \
                       url_for('todo_paginated', page=(count+4)//5)))
        else:
            response = make_response(redirect('/todo'))
        response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response



@app.route('/todo/<id>', methods=['POST'])
@login_check
def todo_delete(id):
    todo = db.session.query(Todo). \
           filter(Todo.user_id == session['user']['id']). \
           filter(Todo.id == id).first()
    if todo:
        db.session.delete(todo)
        db.session.commit()
        flash("Deleted a todo successfully.")
    else:
        flash("Did not find todo with this id.")
    return redirect('/todo')


@app.route('/todo_completed/<id>', methods=['POST'])
@login_check
def todo_completed(id):
    if todo:
        db.session.query(Todo). \
        filter(Todo.user_id == session['user']['id']). \
        filter(Todo.id == id).update({Todo.todo_status: True},  \
        synchronize_session = False)
        db.session.commit()
    else:
        flash("Did not find todo with this id.")
    return redirect('/todo')


@app.route('/todo/<id>/json', methods=['GET'])
@app.route('/todo/<id>/json/', methods=['GET'])
@login_check
def todo_json(id):
    todo = db.session.query(Todo). \
           filter(Todo.user_id == session['user']['id']). \
           filter(Todo.id == id).first()
    if todo:
        json_string = json.dumps(todo.serialize)
        return render_template('json.html', json_string=json_string)
    else:
        flash("Did not find todo with this id.")
        return redirect('/todo')


TODOS_PER_PAGE = 5
@app.route('/todo/page/', defaults={'page': 1}, methods=['GET'])
@app.route('/todo/page/<int:page>', methods=['GET'])
@app.route('/todo/page/<int:page>/', methods=['GET'])
@login_check
def todo_paginated(page):
    count = db.session.query(Todo).count()
    pagination = db.session.query(Todo). \
                 filter(Todo.user_id == session['user']['id']). \
                 filter(Todo.todo_status == False). \
                 paginate(page, TODOS_PER_PAGE, count)

    return render_template('todos.html', pagination=pagination, \
           todos=pagination.items)
