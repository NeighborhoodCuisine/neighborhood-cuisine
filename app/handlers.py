from flask_restful import Resource
from flask import request
from copy import deepcopy

from app.model import ActiveUsers


SRC_FACEBOOK = 'fb'
SRC_SESSION = 'ses'

active_users = ActiveUsers()


class InitUser(Resource):
    @staticmethod
    def put():
        data = request.get_json()
        print(data)
        Match.cache = None
        active_users.add_user(data, SRC_FACEBOOK)


class Session(Resource):
    @staticmethod
    def put():
        data = request.get_json()
        print(data)
        Match.cache = None
        active_users.add_user(data, SRC_SESSION)


class Match(Resource):
    cache = None

    @classmethod
    def post(cls):
        user = request.get_json()['id']
        if cls.cache is None:
            cls.cache = active_users.get_best_permutation()
        data = deepcopy(cls.cache)
        if user in [u.identifier for u in data['group']]:
            active_users.enrich_missing_ingredients(data)
            active_users.enrich_user_data(data)
            print(data['group'])
            return data
        else:
            return {}


class NearByUsers(Resource):
    @staticmethod
    def post():
        data = request.get_json()
        user = data['id']
        count = active_users.find_nearby(user)
        return {
            'count': count
        }
