#!/usr/bin/python3
"""A module that contains the amenities view for the API.
"""
from flask import jsonify, request
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest
from api.v1.views import app_views
from models import storage
from models.amenity import Amenity


METHODS = ['GET', 'DELETE', 'POST', 'PUT']
'''Methods allowed for the amenities endpoint.'''


@app_views.route('/amenities', methods=METHODS)
@app_views.route('/amenities/<id_amenity>', methods=METHODS)
def handle_amenities(id_amenity=None):
    """The method handler for the amenities endpoint.
    """
    handler_dict = {
        'GET': get_amenities,
        'DELETE': remove_amenity,
        'POST': add_amenity,
        'PUT': update_amenity,
    }
    if request.method in handler_dict:
        return handler_dict[request.method](id_amenity)
    else:
        raise MethodNotAllowed(list(handler_dict.keys()))


def get_amenities(id_amenity=None):
    """Gets the amenity with the given id or all amenities.
    """
    all_amenities = storage.all(Amenity).values()
    if id_amenity:
        result = list(filter(lambda x: x.id == id_amenity, all_amenities))
        if result:
            return jsonify(result[0].to_dict())
        raise NotFound()
    all_amenities = list(map(lambda x: x.to_dict(), all_amenities))
    return jsonify(all_amenities)


def remove_amenity(id_amenity=None):
    """Removes a amenity with the given id.
    """
    all_amenities = storage.all(Amenity).values()
    result = list(filter(lambda x: x.id == id_amenity, all_amenities))
    if result:
        storage.delete(result[0])
        storage.save()
        return jsonify({}), 200
    raise NotFound()


def add_amenity(id_amenity=None):
    """Adds a new amenity.
    """
    a_data = request.get_json()
    if type(a_data) is not dict:
        raise BadRequest(description='Not a JSON')
    if 'name' not in a_data:
        raise BadRequest(description='Missing name')
    new_amenity = Amenity(**a_data)
    new_amenity.save()
    return jsonify(new_amenity.to_dict()), 201


def update_amenity(id_amenity=None):
    """Updates the amenity with the given id.
    """
    x_keys = ('id', 'created_at', 'updated_at')
    all_amenities = storage.all(Amenity).values()
    result = list(filter(lambda x: x.id == id_amenity, all_amenities))
    if result:
        a_data = request.get_json()
        if type(a_data) is not dict:
            raise BadRequest(description='Not a JSON')
        old_amenity = result[0]
        for key, value in a_data.items():
            if key not in x_keys:
                setattr(old_amenity, key, value)
        old_amenity.save()
        return jsonify(old_amenity.to_dict()), 200
    raise NotFound()
