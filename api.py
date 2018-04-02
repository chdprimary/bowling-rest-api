from flask import Flask, request, Response
from flask_restful import Resource, Api
from mongoengine import DoesNotExist

from models import Game, Player

import json

app = Flask(__name__)
api = Api(app)

def _generate_error_JSON(e):
    msg = {'error': str(e)}
    status = (404 if isinstance(e,DoesNotExist) else 500)
    return Response(
        json.dumps(msg),
        status=status
    )

class GamesPath(Resource):
    # Get all games
    def get(self):
        try:
            games = []
            for game in Game.objects:
                games.append({
                    'id': str(game.id),
                    'finished': game.finished,
                    'players': [str(player.name) for player in game.players],
                })
            return Response(
                json.dumps(games),
                status=200,
                content_type='application/json'
            )
        except Exception as e:
            response = _generate_error_JSON(e)
            return response

    # Create a new game
    # Using POST b/c we are adding a new resource (the game)
    # Returns 201 Created, Location, and resource representation per RFC 7231
    def post(self):
        try:
            player_names = json.loads(request.data)
            player_objs = [Player(name=player_name) for player_name in player_names]
            game = Game(players=player_objs)
            created_game = game.save()
            msg = {
                'id': str(created_game.id),
                'finished': created_game.finished,
                'players': player_names,
            }
            return Response(
                json.dumps(msg),
                status=201,
                content_type='application/json',
                headers={'Location':'/games/{}'.format(created_game.id)}
            )
        except Exception as e:
            response = _generate_error_JSON(e)
            return response

class GamePath(Resource):

    # Get a specific game's data
    def get(self, game_id):
        try:
            found_game = Game.objects.get(id=game_id)
            msg = {
                'id': str(found_game.id),
                'finished': found_game.finished,
                'players': [str(player.name) for player in found_game.players],
            }
            return Response(
                json.dumps(msg),
                status=200,
                content_type='application/json'
            )
        except (DoesNotExist, Exception) as e:
            response = _generate_error_JSON(e)
            return response

    # Send a new roll
    # Using PUT b/c we are updating an existing resource with a new roll
    def put(self, game_id):
        try:
            found_game = Game.objects.get(id=game_id)
            if not found_game.finished:
                roll_score = int(request.data)
                if roll_score >= 0 and roll_score <= 10:
                    msg = {
                        'roll_score': roll_score
                    }
                    return Response(
                        json.dumps(msg),
                        status=200,
                        content_type='application/json'
                    )
        except (DoesNotExist, Exception) as e:
            response = _generate_error_JSON(e)
            return response

    # Delete a game
    def delete(self, game_id):
        try:
            found_game = Game.objects.get(id=game_id)
            found_game.delete()
            return Response(
                status=204
            )
        except (DoesNotExist, Exception) as e:
            response = _generate_error_JSON(e)
            return response

api.add_resource(GamesPath, '/games')
api.add_resource(GamePath, '/games/<string:game_id>')

if __name__ == '__main__':
    app.run(debug=True)