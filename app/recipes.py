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
    def ranking_params(cls, ingredients):
        params = {
            'ingredients': ','.join(ingredients),
            'limitLicense': False,
            'ranking': 2,
            'number': 1000
        }
        return params

    @classmethod
    def best_n_recipes(cls, ingredients, n=100):
        params = cls.ranking_params(ingredients)
        recipes = requests.get(cls.base_url + '/recipes/findByIngredients',
                               headers=cls.headers, params=params).json()
        if not recipes:
            return None
        recipes.sort(key=lambda r: r.get('likes'), reverse=True)
        return recipes[:100]

    @classmethod
    def full_recipe(cls, _id):
        summary = cls.recipe_summary(_id)
        information = cls.recipe_information(_id)
        summary.update(information)
        return summary

    @classmethod
    def recipe_information(cls, _id):
        required = ['summary']
        params = {
            'includeNutrition': False
        }
        res = requests.get(cls.base_url + '/recipes/{}/information'.format(_id),
                           readers=cls.headers, params=params).json()
        return {key: res[key] for key in required}

    @classmethod
    def recipe_summary(cls, _id):
        required = ['id', 'extendedIngredients', 'title', 'image']
        params = {
            'includeNutrition': False
        }
        res = requests.get(cls.base_url + '/recipes/{}/summary'.format(_id),
                           headers=cls.headers, params=params).json()
        return {key: res[key] for key in required}
