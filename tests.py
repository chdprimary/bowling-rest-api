import json

from unittest import TestCase, main
from mongoengine import connect

from api import app, _generate_player_scores
from models import Game, Player

class GamesPathTest(TestCase):
    def setUp(self):
        self.bowl_app = app.test_client()
        db = connect('bowlapp_mongodb')
        db.drop_database('bowlapp_mongodb')

    def test_GET_all_games(self):
        player_names = [
            'someone1',
            'someone2'
        ]
        players = [Player(name=name) for name in player_names]
        game = Game(players=players)
        game.save()

        response = self.bowl_app.get('/games')
        self.assertIn('200', response.status)

        msg = json.loads(response.data)
        self.assertEqual(len(msg), 1)
        self.assertTrue(isinstance(msg, list))
        self.assertIn('someone1', msg[0]['players'])

    def test_POST_valid_game(self):
        pass

    def test_POST_invalid_game(self):
        pass

    def test_nonallowed_method(self):
        msg = ['a', 'b']
        response = self.bowl_app.put('/games', data=json.dumps(msg))
        self.assertIn('405', response.status)

class GamePathTest(TestCase):
    def setUp(self):
        pass

    def test_GET_valid_game(self):
        pass

    def test_GET_invalid_game(self):
        pass

    def test_PUT_roll_to_finished_game(self):
        pass

    def test_PUT_invalid_roll_value(self):
        pass

    def test_PUT_too_large_a_roll_on_frame_second_roll(self):
        pass

    def test_PUT_strike_on_second_roll(self):
        pass

    def test_PUT_valid_roll(self):
        pass

    def test_PUT_final_frame_stuff(self):
        pass

    def test_DELETE_invalid_game(self):
        pass

    def test_DELETE_valid_game(self):
        pass

    def test_nonallowed_method(self):
        pass

class ScoreTests(TestCase):
    def test_scores_are_calculated_correctly(self):
        scores = [10, 0, 10, 0, 10, 0]
        score_info = _generate_player_scores(scores)
        self.assertEqual(score_info['total'], 60)

if __name__ == '__main__':
    main(warnings='ignore')