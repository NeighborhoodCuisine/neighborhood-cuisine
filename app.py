from flask import Flask, jsonify
from flask import make_response
from flask_restful import Api

from app.handlers import Session, Match, InitUser, NearByUsers


app = Flask(__name__, static_url_path="")
api = Api(app)


@app.errorhandler(404)
def not_found(_):
    return make_response(jsonify({'error': 'Not found'}), 404)

api.add_resource(Session, '/session')
api.add_resource(Match, '/match')
api.add_resource(InitUser, '/user')
api.add_resource(NearByUsers, '/nearby')


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
