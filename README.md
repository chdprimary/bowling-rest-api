# dependencies
1. Flask-RESTful ```pip install flask-restful```
2. MongoEngine ```pip install mongoengine```
3. MongoDB (default host/port) with a database named "bowlapp_mongodb"

# running locally
After cloning the repo, in the project directory:
1. run ```python api.py```
2. Use curl, insomnia, postman, or another REST client to send requests to ```localhost:5000``` as described below

# actions
* ```GET localhost:5000/games``` - retrieves a list of all games.
* ```POST localhost:5000/games``` - creates a new game. Returns a representation of the created resource. Use the following request body:
```
[
  <string:player_name>,
  <string:player_name>,
  ...
]
```
*```GET localhost:5000/games/:gameid``` - retrieves a specific game, including player score/roll information. 
*```PUT localhost:5000/games/:gameid``` - updates the game with a new roll. Use the following request body:
```
<text:roll_score>
```
*```DELETE localhost:5000/games/:gameid``` - deletes the specified game resource. Returns nothing.
