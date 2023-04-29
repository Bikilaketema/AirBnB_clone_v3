#!/usr/bin/python3
"""A module that contains the places_amenities view for the API.
"""
from flask import jsonify, request
from werkzeug.exceptions import NotFound, MethodNotAllowed
from api.v1.views import app_views
from models import storage, storage_t
from models.amenity import Amenity
from models.place import Place


@app_views.route('/places/<id_place>/amenities', methods=['GET'])
@app_views.route(
    '/places/<id_place>/amenities/<id_amenity>',
    methods=['DELETE', 'POST']
)
def handle_place_amenities(id_place=None, id_amenity=None):
    """The method handler for the places endpoint.
    """
    handler_dict = {
        'GET': get_place_amenities,
        'DELETE': remove_place_amenity,
        'POST': add_place_amenity
    }
    if request.method in handler_dict:
        return handler_dict[request.method](id_place, id_amenity)
    else:
        raise MethodNotAllowed(list(handler_dict.keys()))


def get_place_amenities(id_place=None, id_amenity=None):
    """Gets the amenities of a place with the given id.
    """
    if id_place:
        place = storage.get(Place, id_place)
        if place:
            all_amenities = list(map(lambda x: x.to_dict(), place.amenities))
            return jsonify(all_amenities)
    raise NotFound()


def remove_place_amenity(id_place=None, id_amenity=None):
    """Removes an amenity with a given id from a place with a given id.
    """
    if id_place and id_amenity:
        place = storage.get(Place, id_place)
        if not place:
            raise NotFound()
        amenity = storage.get(Amenity, id_amenity)
        if not amenity:
            raise NotFound()
        place_amenity_link = list(
            filter(lambda x: x.id == id_amenity, place.amenities)
        )
        if not place_amenity_link:
            raise NotFound()
        if storage_t == 'db':
            amenity_place_link = list(
                filter(lambda x: x.id == id_place, amenity.place_amenities)
            )
            if not amenity_place_link:
                raise NotFound()
            place.amenities.remove(amenity)
            place.save()
            return jsonify({}), 200
        else:
            id_amenityx = place.amenity_ids.index(id_amenity)
            place.amenity_ids.pop(id_amenityx)
            place.save()
            return jsonify({}), 200
    raise NotFound()


def add_place_amenity(id_place=None, id_amenity=None):
    """Adds an amenity with a given id to a place with a given id.
    """
    if id_place and id_amenity:
        place = storage.get(Place, id_place)
        if not place:
            raise NotFound()
        amenity = storage.get(Amenity, id_amenity)
        if not amenity:
            raise NotFound()
        if storage_t == 'db':
            place_amenity_link = list(
                filter(lambda x: x.id == id_amenity, place.amenities)
            )
            amenity_place_link = list(
                filter(lambda x: x.id == id_place, amenity.place_amenities)
            )
            if amenity_place_link and place_amenity_link:
                result = amenity.to_dict()
                del result['place_amenities']
                return jsonify(result), 200
            place.amenities.append(amenity)
            place.save()
            result = amenity.to_dict()
            del result['place_amenities']
            return jsonify(result), 201
        else:
            if id_amenity in place.amenity_ids:
                return jsonify(amenity.to_dict()), 200
            place.amenity_ids.push(id_amenity)
            place.save()
            return jsonify(amenity.to_dict()), 201
    raise NotFound()
