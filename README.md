# dependencies
1. Flask-RESTful ```pip install flask-restful```
2. MongoEngine ```pip install mongoengine```
3. MongoDB (default host/port) with a database named "bowlapp_mongodb"

# running locally
After cloning the repo, in the project directory:
1. run ```python api.py```
2. Use curl, insomnia, postman, or another REST client to send requests to ```localhost:5000``` as described below

# actions
* ```GET localhost:5000/games``` - retrieves a list of all games. No request body needed.
```
* RESPONSE
* Codes: 200 OK
* Headers: Content-Type
* Returns a list of all games, finished and unfinished.
```
* ```POST localhost:5000/games``` - creates a new game. 
```
* REQUEST
* required
* Content-Type: application/json
[
  <string:player_name>,
  <string:player_name>,
  ...
]
```
```
* RESPONSE
* Codes: 302 Created
* Headers: Location
* Returns a representation of the created resource.
```
* ```GET localhost:5000/games/:gameid``` - retrieves a specific game, including player score/roll information. No request body. Response code may be 400 Bad Request or 404 Not Found.
* ```PUT localhost:5000/games/:gameid``` - updates the game with a new roll. Use the following request body:
```
* required
<text:roll_score>  # should be integer between 0 and 10, inclusive.
```
* ```DELETE localhost:5000/games/:gameid``` - deletes the specified game resource. Returns no response body.
