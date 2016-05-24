from flask_restful import Resource, abort
from flask import request
from copy import deepcopy

from app.model import ActiveUsers


SRC_FACEBOOK = 'fb'
SRC_SESSION = 'ses'

active_users = ActiveUsers()


class Recipes(Resource):
    @staticmethod
    def post():
        """
        @api {get} /recipes-from-ingredients
        @apiVersion 0.1.0
        @apiName RecipesFromIngredients
        @apiGroup Recipe
        @apiPermission anonymous

        @apiDescription Retrieve a list of recipes which can be cooked
                        using as many of the given ingredients as possible

        @apiParam {String[]}    ingredients                 List of ingredient names which shall be
                                                            used in the recipe.

        @apiSuccess {Object[]}  recipes                     List of possible recipes
        @apiSuccess {String[]}  recipes.ingredients         List of ingredients of the recipe
        @apiSuccess {String}    recipes.image_url           Url of an image of the recipe
        @apiSuccess {String[]}  recipes.missing_ingredients List of ingredients which were
                                                            not included in the search
        @apiSuccess {String}    recipes.recipe_url Original Url of source of the recipe
        """
        data = request.get_json()
        if 'ingredients' not in data:
            abort(404, message='No ingredients specified')

        return data


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
