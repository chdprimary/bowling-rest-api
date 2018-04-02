from flask import Flask, request, Response
from flask_restful import Resource, Api
from mongoengine import InvalidQueryError, DoesNotExist

from models import Game, Player

import json

app = Flask(__name__)
api = Api(app)

def _generate_error_JSON(e):
    exception_into_status = {
        'DoesNotExist': 404,
        'InvalidQueryError': 400,
    }
    msg = {'error': str(e)}
    status = exception_into_status.get(type(e).__name__, 500)
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
            }
            players = []
            for player in found_game.players:
                data = {
                    'name': player.name,
                    'rolls': [roll for roll in player.rolls],
                    'roll_count': len(player.rolls),
                }
                players.append(data)
            msg['players'] = players
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
            game = Game.objects.get(id=game_id)
            if game.finished:
                raise InvalidQueryError('This game (id: {}) has ended.'.format(game_id))
            roll_score = int(request.data)
            if roll_score < 0 or roll_score > 10:
                raise InvalidQueryError('Number of pins bowled should be between 0 and 10 (inclusive).')

            # iterate players, the first player with the lowest num rolls is current
            # if len(rolls)%2 == 1, they are mid-frame and guaranteed current player
            # mongodb result set order isn't guaranteed to remain same: stackoverflow.com/a/11599283
            curr_max_num_rolls = 21
            curr_player = None
            for player in game.players:
                if len(player.rolls) == 20:
                    if sum(player.rolls[18:]) < 10:
                        continue
                    else:
                        curr_player = player
                        break

                if len(player.rolls) < curr_max_num_rolls:
                    curr_max_num_rolls = len(player.rolls)
                    curr_player = player

                if len(player.rolls) != 21 and len(player.rolls) % 2 == 1:
                    break

            if curr_player is not None:
                if (len(curr_player.rolls) <= 18 and len(curr_player.rolls) % 2 == 1
                    and (curr_player.rolls[-1] + roll_score) > 10):
                        raise InvalidQueryError('Cannot roll {}. Only {} pins remain.' \
                                                .format(roll_score, 10-player.rolls[-1]))
                if len(curr_player.rolls) < 18 and roll_score == 10:
                    curr_player.rolls += [roll_score, 0]
                else:
                    curr_player.rolls += [roll_score]
                curr_player.save()
            else:
                game.finished = True
                game.save()

            return self.get(game_id)
        except (DoesNotExist, InvalidQueryError, Exception) as e:
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