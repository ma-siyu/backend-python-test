from . import db
from collections import OrderedDict

class User(db.Model):
    """Model for users."""

    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.VARCHAR(255), unique=True, nullable=False)
    password = db.Column(db.VARCHAR(255), nullable=False)

    @property
    def serialize(self):
        return {'username': self.username, 'id': self.id, 'password': self.password}

    def _repr_(self):
        return '<User: %r>' %self.username



class Todo(db.Model):
    """Model for todos."""

    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    description = db.Column(db.VARCHAR(255), nullable=False)
    todo_status = db.Column(db.Boolean, default=False)

    @property
    def serialize(self):
        od = OrderedDict([('id', self.id), ('user_id', self.user_id), ('description', self.description)])
        return od

    def _repr_(self):
        return '<Todos: %r>' %self.description
