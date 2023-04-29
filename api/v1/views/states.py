#!/usr/bin/python3
"""A module contains the states view for the API.
"""
from flask import jsonify, request
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest
from api.v1.views import app_views
from models import storage
from models.state import State


METHODS = ['GET', 'DELETE', 'POST', 'PUT']
# Methods allowed for the states endpoint.


@app_views.route('/states', methods=METHODS)
@app_views.route('/states/<id_state>', methods=METHODS)
def handle_state(id_state=None):
    """The method handler for the states endpoint.
    """
    handler_dict = {
        'GET': get_state,
        'DELETE': remove_state,
        'POST': add_state,
        'PUT': update_state,
    }
    if request.method in handler_dict:
        return handler_dict[request.method](id_state)
    else:
        raise MethodNotAllowed(list(handler_dict.keys()))


def get_state(id_state=None):
    """Gets the state with the given id or all states.
    """
    all_states = storage.all(State).values()
    if id_state:
        result = list(filter(lambda x: x.id == id_state, all_states))
        if result:
            return jsonify(result[0].to_dict())
        raise NotFound()
    all_states = list(map(lambda x: x.to_dict(), all_states))
    return jsonify(all_states)


def remove_state(id_state=None):
    """Removes a state with the given id.
    """
    all_states = storage.all(State).values()
    result = list(filter(lambda x: x.id == id_state, all_states))
    if result:
        storage.delete(result[0])
        storage.save()
        return jsonify({}), 200
    raise NotFound()


def add_state(id_state=None):
    """Adds a new state.
    """
    a_data = request.get_json()
    if type(a_data) is not dict:
        raise BadRequest(description='Not a JSON')
    if 'name' not in a_data:
        raise BadRequest(description='Missing name')
    new_state = State(**a_data)
    new_state.save()
    return jsonify(new_state.to_dict()), 201


def update_state(id_state=None):
    """Updates the state with the given id.
    """
    x_keys = ('id', 'created_at', 'updated_at')
    all_states = storage.all(State).values()
    result = list(filter(lambda x: x.id == id_state, all_states))
    if result:
        a_data = request.get_json()
        if type(a_data) is not dict:
            raise BadRequest(description='Not a JSON')
        old_state = result[0]
        for key, value in a_data.items():
            if key not in x_keys:
                setattr(old_state, key, value)
        old_state.save()
        return jsonify(old_state.to_dict()), 200
    raise NotFound()
