#!/usr/bin/python3
"""A module that contains the cities view for the API.
"""
from flask import jsonify, request
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest
from api.v1.views import app_views
from models import storage, storage_t
from models.city import City
from models.place import Place
from models.review import Review
from models.state import State


@app_views.route('/states/<id_state>/cities', methods=['GET', 'POST'])
@app_views.route('/cities/<id_city>', methods=['GET', 'DELETE', 'PUT'])
def handle_cities(id_state=None, id_city=None):
    """The method handler for the cities endpoint.
    """
    handler_dict = {
        'GET': get_cities,
        'DELETE': remove_city,
        'POST': add_city,
        'PUT': update_city,
    }
    if request.method in handler_dict:
        return handler_dict[request.method](id_state, id_city)
    else:
        raise MethodNotAllowed(list(handler_dict.keys()))


def get_cities(id_state=None, id_city=None):
    """Gets the city with the given id or all cities in
       the state with the given id.
    """
    if id_state:
        state = storage.get(State, id_state)
        if state:
            cities = list(map(lambda x: x.to_dict(), state.cities))
            return jsonify(cities)
    elif id_city:
        city = storage.get(City, id_city)
        if city:
            return jsonify(city.to_dict())
    raise NotFound()


def remove_city(id_state=None, id_city=None):
    """Removes a city with the given id.
    """
    if id_city:
        city = storage.get(City, id_city)
        if city:
            storage.delete(city)
            if storage_t != "db":
                for place in storage.all(Place).values():
                    if place.id_city == id_city:
                        for review in storage.all(Review).values():
                            if review.id_place == place.id:
                                storage.delete(review)
                        storage.delete(place)
            storage.save()
            return jsonify({}), 200
    raise NotFound()


def add_city(id_state=None, id_city=None):
    """Adds a new city.
    """
    state = storage.get(State, id_state)
    if not state:
        raise NotFound()
    data = request.get_json()
    if type(data) is not dict:
        raise BadRequest(description='Not a JSON')
    if 'name' not in data:
        raise BadRequest(description='Missing name')
    data['id_state'] = id_state
    city = City(**data)
    city.save()
    return jsonify(city.to_dict()), 201


def update_city(id_state=None, id_city=None):
    """Updates the city with the given id.
    """
    x_keys = ('id', 'id_state', 'created_at', 'updated_at')
    if id_city:
        city = storage.get(City, id_city)
        if city:
            data = request.get_json()
            if type(data) is not dict:
                raise BadRequest(description='Not a JSON')
            for key, value in data.items():
                if key not in x_keys:
                    setattr(city, key, value)
            city.save()
            return jsonify(city.to_dict()), 200
    raise NotFound()
