from mongoengine import (
    Document,
    EmbeddedDocument,
    EmbeddedDocumentField,
    StringField,
    BooleanField,
    ListField,
    IntField,
    connect
)

connect('bowlapp_mongodb')

class Player(EmbeddedDocument):
    name = StringField(min_length=1, max_length=25, required=True)
    rolls = ListField(IntField())

class Game(Document):
    finished = BooleanField(default=False)
    players = ListField(EmbeddedDocumentField(Player), required=True)
