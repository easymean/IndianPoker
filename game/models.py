import uuid

from utils.redis_client import r
from enum import Enum


class RoomState(int, Enum):
    EMPTY = 1
    START = 2


class MessageType(int, Enum):
    ENTER = 1
    EXIT = 2
    CHAT = 3


class User:
    def __init__(self, nickname):
        self.id = uuid.uuid4()
        self.nickname = nickname
        self.ready_state = 0
        self.score = 10

    def __str__(self):
        return str(self.id)

    def make_user(self):
        hash_key = str(self.id)
        field_value = {
            "nickname": self.nickname,
            "ready_state": self.ready_state,
            "score": self.score
        }
        r.hmset(hash_key, field_value)
        r.rpush("user", hash_key);


def delete_user(user_id):
    r.hdel(user_id)
    # *확인: r.lrm("user", user_id*)


def get_nickname(user_id):
    return r.hget(user_id, "nickname")


class Room:
    def __init__(self, name):
        self.id = uuid.uuid4()
        self.name = name
        self.state = RoomState.EMPTY
        self.round = 0
        self.users = ""

    def __str__(self):
        return str(self.id)

    def make_room(self):
        hash_key = str(self.id)
        field_value = {
            "name": self.name,
            "state": self.state,
            "round": self.round,
            "users": self.users
        }
        r.hmset(hash_key, field_value);
        r.rpush("room", hash_key);


def find_room(room_id):
    return r.hvals(room_id)


def get_user_list(room_id):
    return r.hget(room_id, "users")


def get_user_count(room_id):
    user_str = r.hget(room_id, "users")
    return user_str.count(',')


def enter_room(room_id, user_id):
    user_str = str(get_user_list(room_id))
    str_list = [user_str, user_id]
    user_str = ','.join(str_list)
    r.hset(user_id, "users", user_str)


def delete_room(room_id):
    pass


class ClientMessage:
    type = 0
    room_id = ""
    sender_id = ""
    nickname= ""
    message = ""

    def __init__(self, room_id, sender_id, nickname=nickname):
        self.room_id = room_id
        self.sender_id = sender_id
        self.nickname = nickname


class EnterMessage(ClientMessage):
    def __init__(self, room_id, sender_id, nickname):
        super().__init__(room_id, sender_id, nickname)
        self.type = MessageType.ENTER
        self.message = f'{self.nickname}님이 입장하셨습니다.'


class ExitMessage(ClientMessage):
    def __init__(self, room_id, sender_id, nickname):
        super().__init__(room_id, sender_id, nickname)
        self.type = MessageType.EXIT
        self.message = f'{self.nickname}님이 퇴장하셨습니다.'

