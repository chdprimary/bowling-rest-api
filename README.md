# dependencies
1. Flask-RESTful ```pip install flask-restful```
2. MongoEngine ```pip install mongoengine```
3. MongoDB (default host/port) with a database named "bowlapp_mongodb"

# running locally
After cloning the repo, in the project directory:
1. run ```python api.py```
2. Use curl, insomnia, postman, paw, or another REST client to send requests to ```localhost:5000``` as described below

# actions
* ```GET localhost:5000/games``` - retrieves a list of all games. No request body needed.
```
* RESPONSE
* Codes: 200 OK
* Returns a list of all games in the database, finished and unfinished.
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
* ```GET localhost:5000/games/:gameid``` - retrieves a specific game. No request body needed.
```
* RESPONSE
* Codes: 400 Bad Request, 404 Not Found
* Returns a representation of the specified game, including player roll & score information.
```
* ```PUT localhost:5000/games/:gameid``` - updates the game with a new roll. 
```
* REQUEST
* required
<text:roll_score>  # should be plain integer between 0 and 10, inclusive.
```
```
* RESPONSE
* Codes: 400 Bad Request, 404 Not Found
* Updates game with a new roll. The roll will be allocated to the next player automatically. Returns result of a call to GET /games/:gameid.
```
* ```DELETE localhost:5000/games/:gameid``` - deletes the specified game resource. No request body needed.
```
* RESPONSE
* Codes: 204 No Content
* Response body is empty when successful. 
```
