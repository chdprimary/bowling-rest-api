from mongoengine import *

connect('bowlingapp_mongodb')

# Game will track whether finished or not, and players
class Game(Document):
    finished = BooleanField(default=False)
    players = ListField(EmbeddedDocumentField(Player), required=True)

# Supporting 2+ players
# players will each have a list of rolls
# Frames aren't needed if each frame is a constant length of 2
# - strike frame can insert a "buffer" roll of 0 in 2nd slot
class Player(EmbeddedDocument):
    rolls = ListField(IntField(), required=True)