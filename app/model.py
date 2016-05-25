from itertools import combinations
import grequests
import copy

from app.recipes import RecipeProvider
from app.utils import distance, contains


MIN_GUESTS = 3
MAX_GUESTS = 8


class ActiveUsers:
    def __init__(self):
        self.users = []

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.users)

    def add_user(self, data, source):
        for user in self.users:
            if user.merge(data, source):
                return

        self.users.append(User(data, source))

    def get_user(self, _id):
        for user in self.users:
            if user.identifier == _id:
                return user

    def remove_user(self, identifier):
        for user in self.users:
            if user.name == identifier:
                self.users.remove(user)
                break

    def find_nearby(self, user, radius=1000.):
        user = self.get_user(user)
        if user is None:
            return
        return len([u for u in self.users if u.identifier != user and
                    distance(u.location, user.location) <= radius])

    @classmethod
    def _joined_ingredients(cls, users):
        ingredients = [u.ingredients for u in users]
        ingredients = [i for u in ingredients for i in u]
        ingredients = [i.lower() for i in ingredients]
        return list(set(ingredients))

    def joined_ingredients(self):
        return self._joined_ingredients([u for u in self.users if u.active])

    @classmethod
    def _get_combinations(cls, users):
        subsets = []
        for i in range(MIN_GUESTS, MAX_GUESTS+1):
            subsets.append([l for l in combinations(users, i)])
        return [s for sub in subsets for s in sub if sub]

    @classmethod
    def _filter_combinations(cls, sets):
        return [l for l in sets if len(l) <= max(u.max_guests for u in l)]

    @classmethod
    def _find_recipes(cls, subsets):
        ingredients = [g['ingredients'] for g in subsets]
        fetch_list = (grequests.get(
            RecipeProvider.recipe_list, headers=RecipeProvider.headers,
            params=RecipeProvider.params(ing)) for ing in ingredients)
        recipes = grequests.map(fetch_list, size=50)
        recipes = [r.json() for r in recipes]
        for recipe_list in recipes:
            recipe_list.sort(key=lambda r: r.get('likes'), reverse=True)
        return [r[0] for r in recipes]

    @classmethod
    def _calculate_ingredients(cls, subsets):
        options = []
        for group in subsets:
            ingredients = cls._joined_ingredients(group)
            options.append({
                'group': group,
                'ingredients': ingredients
            })

        result = cls._find_recipes(options)

        for i, group in enumerate(options):
            group['recipe'] = result[i]

        return options

    @classmethod
    def _enrich_recipe(cls, recipe):
        info = RecipeProvider.recipe_information(recipe['id'])
        summary = RecipeProvider.recipe_summary(recipe['id'])
        recipe.update(info)
        recipe.update(summary)

    @classmethod
    def enrich_user_data(cls, data):
        users = copy.deepcopy(data['group'])
        data['group'] = []
        guests = 0
        host = None
        for user in users:
            if user.max_guests > guests:
                guests = user.max_guests
                host = user
            data['group'].append({
                'id': user.identifier,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'image': user.image_url,
                'brings': user.ingredients,
                'fb_link': user.fb_link
            })
        if host is None:
            return
        data['host'] = {
            'position': {
                'lat': user.location[0],
                'lon': user.location[0]
            },
            'first_name': user.first_name,
            'last_name': user.last_name
        }

    @classmethod
    def enrich_missing_ingredients(cls, data):
        ingredients = data['ingredients']
        required = data['recipe']['extendedIngredients']
        missing = []
        for ing in required:
            if not contains(ingredients, ing['name']):
                missing.append(ing['name'])
        data['missing'] = missing

    def get_best_permutation(self):
        users = [u for u in self.users if u.active]
        subsets = self._get_combinations(users)
        subsets = self._filter_combinations(subsets)
        possible_groups = self._calculate_ingredients(subsets)
        possible_groups.sort(key=lambda r: r['recipe'].get('likes'),
                             reverse=True)
        if possible_groups:
            best = possible_groups[0]
            self._enrich_recipe(best['recipe'])
            return best
        else:
            return {
                'group': []
            }


class User:

    def __init__(self, data, source):
        assert data.get('id') is not None
        self.identifier = data.get('id')
        self.active = False
        self._set_initial()
        self._set_dispatch(data, source)

    def _set_initial(self):
        self.email = ''
        self.first_name = ''
        self.last_name = ''
        self.fb_link = ''
        self.image_url = ''
        self.fb_token = ''
        self.max_guests = 0
        self.location = [52.505573, 13.393538]

    def _set_session(self, data):
        if data.get('location'):
            self.location = [data['location'].get('lat', 0),
                             data['location'].get('lon', 0)]
        self.cuisine = data.get('cuisine', '')
        self.max_guests = data.get('max_guests', 0)
        self.ingredients = data.get('ingredients', [])
        self.active = True

    def _set_facebook(self, data):
        self.email = data.get('email') or self.email
        self.first_name = data.get('first_name') or self.first_name
        self.last_name = data.get('last_name') or self.last_name
        self.fb_link = data.get('fb_link') or self.fb_link
        self.image_url = data.get('image_link') or self.image_url
        self.fb_token = data.get('fb_token') or self.fb_token
        self.location = [data.get('location').get('lat'),
                         data.get('location').get('lon', 0)]

    def _set_dispatch(self, data, source):
        if source == 'fb':
            self._set_facebook(data)
        elif source == 'ses':
            self._set_session(data)
        else:
            raise Exception('Invalid source')

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.identifier

    def merge(self, data, source):
        if self.identifier != data.get('id'):
            return False
        else:
            self._set_dispatch(data, source)
            return True
