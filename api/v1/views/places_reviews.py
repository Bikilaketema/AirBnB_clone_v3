#!/usr/bin/python3
"""A module that contains the places_reviews view for the API.
"""
from flask import jsonify, request
from werkzeug.exceptions import NotFound, MethodNotAllowed, BadRequest
from api.v1.views import app_views
from models import storage
from models.place import Place
from models.review import Review
from models.user import User


@app_views.route('/places/<id_place>/reviews', methods=['GET', 'POST'])
@app_views.route('/reviews/<id_review>', methods=['GET', 'DELETE', 'PUT'])
def handle_reviews(id_place=None, id_review=None):
    """The method handler for the reviews endpoint.
    """
    handler_dict = {
        'GET': get_reviews,
        'DELETE': remove_review,
        'POST': add_review,
        'PUT': update_review
    }
    if request.method in handler_dict:
        return handler_dict[request.method](id_place, id_review)
    else:
        raise MethodNotAllowed(list(handler_dict.keys()))


def get_reviews(id_place=None, id_review=None):
    """Gets the review with the given id or all reviews in
       the place with the given id.
    """
    if id_place:
        place = storage.get(Place, id_place)
        if place:
            reviews = []
            for review in place.reviews:
                reviews.append(review.to_dict())
            return jsonify(reviews)
    elif id_review:
        review = storage.get(Review, id_review)
        if review:
            return jsonify(review.to_dict())
    raise NotFound()


def remove_review(id_place=None, id_review=None):
    """Removes a review with the given id.
    """
    review = storage.get(Review, id_review)
    if review:
        storage.delete(review)
        storage.save()
        return jsonify({}), 200
    raise NotFound()


def add_review(id_place=None, id_review=None):
    """Adds a new review.
    """
    place = storage.get(Place, id_place)
    if not place:
        raise NotFound()
    data = request.get_json()
    if type(data) is not dict:
        raise BadRequest(description='Not a JSON')
    if 'id_user' not in data:
        raise BadRequest(description='Missing id_user')
    user = storage.get(User, data['id_user'])
    if not user:
        raise NotFound()
    if 'text' not in data:
        raise BadRequest(description='Missing text')
    data['id_place'] = id_place
    new_review = Review(**data)
    new_review.save()
    return jsonify(new_review.to_dict()), 201


def update_review(id_place=None, id_review=None):
    """Updates the review with the given id.
    """
    x_keys = ('id', 'id_user', 'id_place', 'created_at', 'updated_at')
    if id_review:
        review = storage.get(Review, id_review)
        if review:
            data = request.get_json()
            if type(data) is not dict:
                raise BadRequest(description='Not a JSON')
            for key, value in data.items():
                if key not in x_keys:
                    setattr(review, key, value)
            review.save()
            return jsonify(review.to_dict()), 200
    raise NotFound()
