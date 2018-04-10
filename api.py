import json

from flask import Flask, request, Response
from flask_restful import Resource, Api
from mongoengine import InvalidQueryError, DoesNotExist

from models import Game, Player

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

def _generate_player_scores(rolls):
    frame_scores = []

    for idx, val in enumerate(rolls):
        # if final frame has strike or spare, add additional points
        if idx > 18 and (rolls[18] == 10 or sum(rolls[18:20]) == 10):
            frame_scores[9] += val
            continue

        # if frame's first roll
        if idx % 2 == 0:
            frame_score = val

            # add additional points if strike
            if val == 10:
                # skip over filler 0 for 1st resolving roll
                if idx + 2 <= len(rolls) - 1:
                    frame_score += rolls[idx+2]

                # get 2nd resolving roll based on if 1st was strike or not
                if idx + 3 <= len(rolls) - 1 and rolls[idx+2] != 10:
                    frame_score += rolls[idx+3]
                elif idx + 4 <= len(rolls) - 1 and rolls[idx+2] == 10:
                    # if 1st resolving roll was strike, skip another filler 0
                    frame_score += rolls[idx+4]

            frame_scores.append(frame_score)
        else:
            # frame score is 1st roll + 2nd roll
            frame_score = frame_scores[-1] + val

            # add additional points if spare
            # 2nd roll must not be filler 0 from earlier strike
            if val != 0 and frame_score == 10:
                # get next roll if exists
                if idx + 1 < len(rolls) - 1:
                    frame_score += rolls[idx+1]

            frame_scores[-1] = frame_score

    return {
        "frame_scores": frame_scores,
        "total": sum(frame_scores),
    }

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
            if len(player_names) < 1 or len(player_names) > 5:
                raise InvalidQueryError('Number of players must be between 1 and 5, inclusive.')
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
        except (InvalidQueryError, Exception) as e:
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
                    'scores': _generate_player_scores(player.rolls),
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

            # find the 'current player' to attribute the roll to
            curr_max_num_rolls = 21
            curr_player = None
            for player in game.players:
                # if have 20 rolls and strike or spare in final frame, this is fill ball
                if len(player.rolls) == 20:
                    if sum(player.rolls[18:]) < 10:
                        continue
                    else:
                        curr_player = player
                        break

                # player with the lowest number of rolls is the current player
                if len(player.rolls) < curr_max_num_rolls:
                    curr_max_num_rolls = len(player.rolls)
                    curr_player = player

                # if mid-frame (and not final frame), guaranteed to be current player
                if len(player.rolls) != 21 and len(player.rolls) % 2 == 1:
                    break

            if curr_player is not None:
                # if 2nd frame roll, make sure total <= 10 (unless final frame)
                if (len(curr_player.rolls) <= 18 and len(curr_player.rolls) % 2 == 1
                    and (curr_player.rolls[-1] + roll_score) > 10):
                        raise InvalidQueryError('Cannot roll {}. Only {} pins are standing.' \
                                                .format(roll_score, 10-curr_player.rolls[-1]))
                # if score is 10 and not final frame and not 2nd frame roll, add strike & filler 0
                # else add score normally
                if (len(curr_player.rolls) < 18 and len(curr_player.rolls) % 2 == 0
                    and roll_score == 10):
                        curr_player.rolls += [10, 0]
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

# Big Lebowski Easter Egg
class DudePath(Resource):
    def get(self):
        msg = {
            'quotes': [
                'The Dude abides.',
                'Well, that\'s just, like, your opinion, man.',
                'You are entering a world of pain.',
            ]
        }
        return Response(
            json.dumps(msg),
            status=200,
            content_type='application/json'
        )

api.add_resource(GamesPath, '/games')
api.add_resource(GamePath, '/games/<string:game_id>')
api.add_resource(DudePath, '/thedude')

if __name__ == '__main__':
    app.run(debug=True)