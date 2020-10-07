import uuid

from utils.redis_client import r
from enum import Enum


class RoomState(int, Enum):
    EMPTY = 1
    READY = 2
    START = 3

class User:
    def __init__(self, nickname):
        self.id = uuid.uuid4()
        self.nickname = nickname
        self.ready_state = 0
        self.score = 10

    def __str__(self):
        return str(self.id)

    def make_user(self):
        hash_name = str(self.id)
        key_value = {
            "nickname": self.nickname,
            "ready_state": self.ready_state,
            "score": self.score
        }
        r.hmset(hash_name, key_value)
        r.rpush("user", hash_name);


class Room:

    def __init__(self, name, group_name, id=None):
        self.id = uuid.uuid4()
        self.name = name
        self.group_name = group_name
        self.state = RoomState.EMPTY
        self.round = 0

    def __str__(self):
        return str(self.id)

    def make_room(self):
        hash_name = str(self.id)
        key_value = {
            "name": self.name,
            "group_name": self.group_name,
            "state": self.state,
            "round": self.round,
        }
        r.hmset(hash_name, key_value);
        r.rpush("room", hash_name);

