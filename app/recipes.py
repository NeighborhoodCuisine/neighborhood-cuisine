import requests

from app.credentials import access_token


class RecipeProvider:

    base_url = 'https://spoonacular-recipe-food-nutrition-v1.p.mashape.com'
    headers = {
        'X-Mashape-Key': access_token,
        'Accept': 'application/json'
    }
    recipe_list = base_url + '/recipes/findByIngredients'

    @classmethod
    def params(cls, ingredients):
        params = {
            'ingredients': ','.join(ingredients),
            'limitLicense': False,
            'ranking': 2,
            'number': 1000
        }
        return params

    @classmethod
    def best_recipe(cls, ingredients):
        params = cls.params(ingredients)
        recipes = requests.get(cls.base_url + '/recipes/findByIngredients',
                               headers=cls.headers, params=params).json()
        if not recipes:
            return None
        recipes.sort(key=lambda r: r.get('likes'), reverse=True)
        return recipes[0]

    @classmethod
    def recipe_info(cls, _id):
        params = {
            'includeNutrition': False
        }
        summary = cls.recipe_summary(_id)
        return requests.get(cls.base_url + '/recipes/{}/information'.format(_id),
                            headers=cls.headers, params=params).json()

    @classmethod
    def recipe_summary(cls, _id):
        params = {
            'includeNutrition': False
        }
        return requests.get(cls.base_url + '/recipes/{}/summary'.format(_id),
                            headers=cls.headers, params=params).json()

    # TODO: implement recipe API
    @classmethod
    def recipes(cls, _ingredients):
        """
        @api {get} /recipes-from-ingredients
        @apiVersion 0.1.0
        @apiName RecipesFromIngredients
        @apiGroup Recipe
        @apiPermission anonymous

        @apiDescription Retrieve a list of recipes which can be cooked using as many of the given ingredients as possible

        @apiParam {String[]} ingredients List of ingredient names which shall be used in the recipe.

        @apiSuccess {Object[]} recipes                     List of possible recipes
        @apiSuccess {String[]} recipes.ingredients         List of ingredients of the recipe
        @apiSuccess {String}   recipes.image_url           Url of an image of the recipe
        @apiSuccess {String[]} recipes.missing_ingredients List of ingredients which were not included in the search
        @apiSuccess {String}   recipes.recipe_url Original Url of source of the recipe
        """
        pass
