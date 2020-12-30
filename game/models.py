import uuid, json

from utils.redis_client import r
from enum import Enum


class UserState(str, Enum):
    WAIT = "WAIT"
    READY = "READY"


class RoomState(str, Enum):
    READY = "READY"
    START = "START"


class ClientMessageType(str, Enum):
    # THIS IS ABOUT CLIENT ACTION
    ENTER = "ENTER"
    EXIT = "EXIT"
    CHAT = "CHAT"
    # THIS IS ABOUT CLIENT STATE
    READY = "READY"
    WAIT = "WAIT"


class ServerMessageType(str, Enum):
    GAME = 'GAME'


class User:
    def __init__(self, nickname):
        self.id = uuid.uuid4()
        self.nickname = nickname
        self.state = 'WAIT'
        self.point = 30
        self.cards = ""

    def __str__(self):
        return str(self.id)

    def make_user(self):
        hash_key = str(self.id)
        field_value = {
            "nickname": self.nickname,
            "state": self.state,
            "point": self.point,
        }
        r.hmset(hash_key, field_value)
        r.rpush("user", hash_key)


class Room:
    def __init__(self, name):
        self.id = uuid.uuid4()
        self.name = name
        self.state = 'READY'
        self.round = 0
        self.order = -1
        self.users = ''

    def __str__(self):
        return str(self.id)

    def make_room(self):
        hash_key = str(self.id)
        field_value = {
            'name': self.name,
            'state': self.state,
            'round': self.round,
            'order': self.order,
        }
        r.hmset(hash_key, field_value)
        r.rpush('room', hash_key)


class ClientMessage:
    type = 0
    opponent_card = 0
    opponent_bet = 1
    my_point = 10
    this_round = 0
    this_turn = ""
    result = {}
    last_choice = ""
    message = ""

    def __init__(self, message_type, message):
        self.type = message_type
        self.opponent_card = 0
        self.opponent_bet = 1
        self.this_turn = ""
        self.result = {
            "winner": "",
            "loser": "",
            "my_card": 0,
            "opponent_card": 0,
        }
        self.round_status = -1
        self.message = message

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4, ensure_ascii=False)

    def set_result(self, winner, loser, my_card, opponent_card, my_point):
        self.result['winner'] = winner
        self.result['loser'] = loser
        self.result['my_card'] = my_card
        self.result['opponent_card'] = opponent_card
        self.my_point = my_point

    def set_card_info(self, opponent_card, me):
        self.this_turn = me
        self.opponent_card = opponent_card




