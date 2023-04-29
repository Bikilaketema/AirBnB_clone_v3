#!/usr/bin/python3
"""A module that contains the users view for the API.
"""
from flask import jsonify, request
from werkzeug.exceptions import NotFound, BadRequest
from api.v1.views import app_views
from models import storage
from models.user import User


@app_views.route('/users', methods=['GET'])
@app_views.route('/users/<id_user>', methods=['GET'])
def get_user(id_user=None):
    """Gets the user with the given id or all users.
    """
    if id_user:
        user = storage.get(User, id_user)
        if user:
            _object = user.to_dict()
            if 'places' in _object:
                del _object['places']
            if 'reviews' in _object:
                del _object['reviews']
            return jsonify(_object)
        raise NotFound()
    a_users = storage.all(User).values()
    users = []
    for user in a_users:
        _object = user.to_dict()
        if 'places' in _object:
            del _object['places']
        if 'reviews' in _object:
            del _object['reviews']
        users.append(_object)
    return jsonify(users)


@app_views.route('/users/<id_user>', methods=['DELETE'])
def remove_user(id_user):
    """Removes a user with the given id.
    """
    user = storage.get(User, id_user)
    if user:
        storage.delete(user)
        storage.save()
        return jsonify({}), 200
    raise NotFound()


@app_views.route('/users', methods=['POST'])
def add_user():
    """Adds a new user.
    """
    a_data = {}
    try:
        a_data = request.get_json()
    except Exception:
        a_data = None
    if type(a_data) is not dict:
        raise BadRequest(description='Not a JSON')
    if 'email' not in a_data:
        raise BadRequest(description='Missing email')
    if 'password' not in a_data:
        raise BadRequest(description='Missing password')
    user = User(**a_data)
    user.save()
    _object = user.to_dict()
    if 'places' in _object:
        del _object['places']
    if 'reviews' in _object:
        del _object['reviews']
    return jsonify(_object), 201


@app_views.route('/users/<id_user>', methods=['PUT'])
def update_user(id_user):
    """Updates the user with the given id.
    """
    x_keys = ('id', 'email', 'created_at', 'updated_at')
    user = storage.get(User, id_user)
    if user:
        a_data = {}
        try:
            a_data = request.get_json()
        except Exception:
            a_data = None
        if type(a_data) is not dict:
            raise BadRequest(description='Not a JSON')
        for key, value in a_data.items():
            if key not in x_keys:
                setattr(user, key, value)
        user.save()
        _object = user.to_dict()
        if 'places' in _object:
            del _object['places']
        if 'reviews' in _object:
            del _object['reviews']
        return jsonify(_object), 200
    raise NotFound()
