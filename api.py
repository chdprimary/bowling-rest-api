from flask import Flask, request, Response
from flask_restful import Resource, Api

import json

app = Flask(__name__)
api = Api(app)

class Games(Resource):
    # Get all games
    def get(self):
        msg = {'test': 'test'}
        return Response(json.dumps(msg), status=200)

    # Create a new game
    # Using POST b/c we are adding a new resource (the game)
    def post(self):
        pass

class Game(Resource):
    # Get a game's data
    def get(self, game_id):
        pass

    # Send a new roll
    # Using PUT b/c we are updating an existing resource with a new roll
    def put(self, game_id):
        pass

    # Delete a game
    def delete(self, game_id):
        pass

api.add_resource(Games, '/games')
api.add_resource(Game, '/games/<string:game_id')

if __name__ == '__main__':
    app.run(debug=True)