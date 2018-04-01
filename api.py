from flask import Flask, request, Response
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class Games(Resource):
    def get(self):
        return Response({'test': 'test'}, status=200)

class Game(Resource):
    pass

api.add_resource(Games, '/games')
api.add_resource(Game, '/games/<string:game_id')

if __name__ == '__main__':
    app.run(debug=True)