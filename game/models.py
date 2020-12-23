import uuid

from utils.redis_client import r
from enum import Enum


class UserState(int, Enum):
    WAIT = 0
    READY = 1


class RoomState(int, Enum):
    READY = 1
    START = 2


class MessageType(int, Enum):
    ENTER = 1
    EXIT = 2
    CHAT = 3
    READY = 4
    WAIT = 5


class GameState(int, Enum):
    pass


class User:
    def __init__(self, nickname):
        self.id = uuid.uuid4()
        self.nickname = nickname
        self.ready_state = UserState.WAIT
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


def get_nickname(user_id):
    nickname = r.hget(user_id, "nickname")
    return nickname.decode("UTF-8")


def get_ready(user_id):
    r.hset(user_id, "ready_state", UserState.READY)


def cancel_ready(user_id):
    r.hset(user_id, "ready_state", UserState.WAIT)


class Room:
    def __init__(self, name):
        self.id = uuid.uuid4()
        self.name = name
        self.state = RoomState.READY
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


def delete_room(room_id):
    r.hdel(room_id)


def get_user_list(room_id):
    return r.hget(room_id, "users")


def get_user_count(room_id):
    user_str = str(r.hget(room_id, "users"))
    if user_str == "":
        return 0

    return user_str.count(',') + 1


def enter_room(room_id, user_id):

    if get_user_count(room_id) == 2:
        print("방이 가득 차서 입장 불가능합니다.")
        return -1
    else:
        user_str = str(get_user_list(room_id))
        str_list = [user_str, user_id]
        if len(user_str) == 0:
            user_str = user_id
        else:
            user_str = ','.join(str_list)
        r.hset(room_id, "users", user_str)
        return 1


def exit_room(room_id, user_id):
    delete_user(user_id)
    prev_user_str = str(get_user_list(room_id))
    user_str = ""
    for user in prev_user_str.split(','):
        if user != user_id:
            user_str = user

    # 남아 있는 유저가 없으면 방을 삭제한다
    if len(user_str) == 0:
        delete_room(room_id)
    else:
        r.hset(room_id, "users", user_str)


class GameMessage:
    type = 0
    opponent_card = 0
    opponent_bet = 1
    this_turn = ""
    result = {}
    round_status = -1
    msg = ""

    def __init__(self):
        self.type = MessageType.GAME
        self.opponent_card = 0
        self.opponent_bet = 1
        self.this_turn = ""
        self.result = {
            "winner": "",
            "my_card": 0,
            "opponent_card": 0,
        }
        self.round_status = -1
        self.message = ""

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__,
                          sort_keys=True, indent=4, ensure_ascii=False)

    def set_result(self, winner, my_card, opponent_card):
        self.result["winner"] = winner
        self.result["my_card"] = my_card
        self.result["opponent_card"] = opponent_card

    def enter_message(self, nickname):
        self.type = MessageType.ENTER
        self.message = f'{nickname}님이 입장하셨습니다.'

    def exit_message(self, nickname):
        self.type = MessageType.EXIT
        self.message = f'{nickname}님이 퇴장하셨습니다.'

    def ready_message(self, nickname):
        self.type = MessageType.READY
        self.message = f'{nickname}님이 레디를 눌렀습니다.'

    def wait_message(self, nickname):
        self.type = MessageType.WAIT
        self.message = f'{nickname}님이 레디를 취소했습니다.'

    def start_message(self):
        self.type = MessageType.START
        self.message = '5초 후에 게임이 시작됩니다.'

    def start_game(self, room_id, me, my_nickname):
        self.this_turn = me

        user_list = get_user_list(room_id)
        opponent = user_list[0] if user_list[1] == me else user_list[1]

        opponent_cards_list = get_cards_list(opponent)
        self.opponent_card = opponent_cards_list[0]
        self.message = f'{my_nickname}님 차례입니다.'

    def check(self, bet):
        pass

    def bet(self):
        pass

    def call_bet(self):
        pass

    def raise_bet(slef):
        pass

    def die(self):
        pass