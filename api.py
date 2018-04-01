from flask import Flask, request, Response
from flask_restful import Resource, Api

from models import Game, Player

import json

app = Flask(__name__)
api = Api(app)

class GamesPath(Resource):
    # Get all games
    def get(self):
        games = []
        for game in Game.objects:
            games.append({
                "id": str(game.id),
                "finished": game.finished,
                "players": [str(player.name) for player in game.players],
            })
        return Response(json.dumps(games), status=200)

    # Create a new game
    # Using POST b/c we are adding a new resource (the game)
    # Returns 201 Created, Location, and resource representation per RFC 7231
    def post(self):
        player_names = json.loads(request.data)
        player_objs = [Player(name=player_name) for player_name in player_names]
        game = Game(players=player_objs)
        created_game = game.save()
        msg = {
            "id": str(created_game.id),
            "finished": created_game.finished,
            "players": player_names,
        }
        response = Response(json.dumps(msg), status=201, content_type='application/json')
        response.headers['Location'] = '/games/{}'.format(created_game.id)
        return response

class GamePath(Resource):
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

api.add_resource(GamesPath, '/games')
api.add_resource(GamePath, '/games/<string:game_id>')

if __name__ == '__main__':
    app.run(debug=True)