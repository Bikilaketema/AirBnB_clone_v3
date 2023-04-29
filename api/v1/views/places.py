#!/usr/bin/python3
"""A module that contains the places view for the API.
"""
from flask import jsonify, request
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest
from api.v1.views import app_views
from models import storage, storage_t
from models.amenity import Amenity
from models.city import City
from models.place import Place
from models.state import State
from models.user import User


@app_views.route('/cities/<id_city>/places', methods=['GET', 'POST'])
@app_views.route('/places/<id_place>', methods=['GET', 'DELETE', 'PUT'])
def handle_place(id_city=None, id_place=None):
    """The method handler for the places endpoint.
    """
    handler_dict = {
        'GET': get_place,
        'DELETE': remove_place,
        'POST': add_place,
        'PUT': update_place
    }
    if request.method in handler_dict:
        return handler_dict[request.method](id_city, id_place)
    else:
        raise MethodNotAllowed(list(handler_dict.keys()))


def get_place(id_city=None, id_place=None):
    """Gets the place with the given id or all places in
       the city with the given id.
    """
    if id_city:
        city = storage.get(City, id_city)
        if city:
            all_places = []
            if storage_t == 'db':
                all_places = list(city.places)
            else:
                all_places = list(filter(
                    lambda x: x.id_city == id_city,
                    storage.all(Place).values()
                ))
            places = list(map(lambda x: x.to_dict(), all_places))
            return jsonify(places)
    elif id_place:
        place = storage.get(Place, id_place)
        if place:
            return jsonify(place.to_dict())
    raise NotFound()


def remove_place(id_city=None, id_place=None):
    """Removes a place with the given id.
    """
    if id_place:
        place = storage.get(Place, id_place)
        if place:
            storage.delete(place)
            storage.save()
            return jsonify({}), 200
    raise NotFound()


def add_place(id_city=None, id_place=None):
    """Adds a new place.
    """
    city = storage.get(City, id_city)
    if not city:
        raise NotFound()
    data = request.get_json()
    if type(data) is not dict:
        raise BadRequest(description='Not a JSON')
    if 'id_user' not in data:
        raise BadRequest(description='Missing id_user')
    user = storage.get(User, data['id_user'])
    if not user:
        raise NotFound()
    if 'name' not in data:
        raise BadRequest(description='Missing name')
    data['id_city'] = id_city
    new_place = Place(**data)
    new_place.save()
    return jsonify(new_place.to_dict()), 201


def update_place(id_city=None, id_place=None):
    """Updates the place with the given id.
    """
    x_keys = ('id', 'id_user', 'id_city', 'created_at', 'updated_at')
    place = storage.get(Place, id_place)
    if place:
        data = request.get_json()
        if type(data) is not dict:
            raise BadRequest(description='Not a JSON')
        for key, value in data.items():
            if key not in x_keys:
                setattr(place, key, value)
        place.save()
        return jsonify(place.to_dict()), 200
    raise NotFound()


@app_views.route('/places_search', methods=['POST'])
def find_places():
    """Finds places based on a list of State, City, or Amenity ids.
    """
    data = request.get_json()
    if type(data) is not dict:
        raise BadRequest(description='Not a JSON')
    all_places = storage.all(Place).values()
    places = []
    places_id = []
    keys_status = (
        all([
            'states' in data and type(data['states']) is list,
            'states' in data and len(data['states'])
        ]),
        all([
            'cities' in data and type(data['cities']) is list,
            'cities' in data and len(data['cities'])
        ]),
        all([
            'amenities' in data and type(data['amenities']) is list,
            'amenities' in data and len(data['amenities'])
        ])
    )
    if keys_status[0]:
        for id_state in data['states']:
            if not id_state:
                continue
            state = storage.get(State, id_state)
            if not state:
                continue
            for city in state.cities:
                new_places = []
                if storage_t == 'db':
                    new_places = list(
                        filter(lambda x: x.id not in places_id, city.places)
                    )
                else:
                    new_places = []
                    for place in all_places:
                        if place.id in places_id:
                            continue
                        if place.id_city == city.id:
                            new_places.append(place)
                places.extend(new_places)
                places_id.extend(list(map(lambda x: x.id, new_places)))
    if keys_status[1]:
        for id_city in data['cities']:
            if not id_city:
                continue
            city = storage.get(City, id_city)
            if city:
                new_places = []
                if storage_t == 'db':
                    new_places = list(
                        filter(lambda x: x.id not in places_id, city.places)
                    )
                else:
                    new_places = []
                    for place in all_places:
                        if place.id in places_id:
                            continue
                        if place.id_city == city.id:
                            new_places.append(place)
                places.extend(new_places)
    del places_id
    if all([not keys_status[0], not keys_status[1]]) or not data:
        places = all_places
    if keys_status[2]:
        amenity_ids = []
        for id_amenity in data['amenities']:
            if not id_amenity:
                continue
            amenity = storage.get(Amenity, id_amenity)
            if amenity and amenity.id not in amenity_ids:
                amenity_ids.append(amenity.id)
        del_indices = []
        for place in places:
            place_amenities_ids = list(map(lambda x: x.id, place.amenities))
            if not amenity_ids:
                continue
            for id_amenity in amenity_ids:
                if id_amenity not in place_amenities_ids:
                    del_indices.append(place.id)
                    break
        places = list(filter(lambda x: x.id not in del_indices, places))
    result = []
    for place in places:
        _object = place.to_dict()
        if 'amenities' in _object:
            del _object['amenities']
        result.append(_object)
    return jsonify(result)
