import uuid, random, json

from utils.exceptions import InvalidMethod
from utils.redis_client import r
from enum import Enum


class UserState(int, Enum):
    WAIT = 0
    READY = 1


class RoomState(int, Enum):
    READY = 1
    START = 2


class MessageType(int, Enum):
    # THIS IS ABOUT CLIENT ACTION
    ENTER = 1
    EXIT = 2
    CHAT = 3
    # THIS IS ABOUT CLIENT STATE
    READY = 4
    WAIT = 5
    # THIS IS ABOUT GAME STATE
    START = 6
    GAME = 7


class GameState(int, Enum):
    pass


# 리스트를 string으로 파싱
def parse_list_into_str(given_list):
    return ','.join(given_list)


def parse_str_into_list(given_str):
    parsed_list = []
    for ele in given_str.split(','):
        parsed_list.append(ele)

    return parsed_list


class User:
    def __init__(self, nickname):
        self.id = uuid.uuid4()
        self.nickname = nickname
        self.ready_state = UserState.WAIT
        self.score = 10
        self.cards = ""

    def __str__(self):
        return str(self.id)

    def make_user(self):
        hash_key = str(self.id)
        field_value = {
            "nickname": self.nickname,
            "ready_state": self.ready_state,
            "score": self.score,
        }
        r.hmset(hash_key, field_value)
        r.rpush("user", hash_key)


def find_user(user_id):
    return r.hvals(user_id)


def delete_user(user_id):
    r.hdel(user_id)


def check_user_state(user_id):
    return r.hget(user_id, "ready_state")


def get_nickname(user_id):
    nickname = r.hget(user_id, "nickname")
    return nickname.decode("UTF-8")


def get_ready(user_id):
    r.hset(user_id, "ready_state", UserState.READY)


def cancel_ready(user_id):
    r.hset(user_id, "ready_state", UserState.WAIT)


def give_cards(user1, user2):
    list1 = []
    list2 = []
    ran_num = random.randint(1, 10)

    for i in range(10):
        while ran_num in list1:
            ran_num = random.randint(1,10)
        list1.append(ran_num)

    for i in range(20):
        while ran_num in list2:
            ran_num = random.randint(1,10)
        list2.append(ran_num)

    list1_str = parse_list_into_str(list1)
    list2_str = parse_list_into_str(list2)

    r.hset(user1, "cards", list1_str)
    r.hset(user2, "cards", list2_str)


def get_cards_list(user_id):
    cards_str = r.hget(user_id, "cards")
    return parse_str_into_list(cards_str)


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
        r.hmset(hash_key, field_value)
        r.rpush("room", hash_key)


def find_room(room_id):
    return r.hvals(room_id)


def delete_room(room_id):
    r.hdel(room_id)


# 방에 있는 유저들이 list로 리턴
def get_user_list(room_id):
    users_str = str(r.hget(room_id, "users"))
    return parse_str_into_list(users_str)


def get_user_count(room_id):
    user_list = get_user_list(room_id)
    return len(user_list)


def check_room_state(room_id):
    return r.hget(room_id, "state")


def are_both_users_ready(room_id):
    user_list = get_user_list(room_id)
    for user in user_list:
        if check_user_state(user) != UserState.READY:
            return False

    return True


def start_game(room_id):
    if check_room_state(room_id) == RoomState.START:
        raise InvalidMethod("이미 시작 상태입니다.")
    r.hset(room_id, "state", RoomState.START)

    user_list = get_user_list(room_id)
    give_cards(user_list[0], user_list[1])


def enter_room(room_id, user_id):

    if get_user_count(room_id) == 2:
        raise InvalidMethod("방이 가득 찼습니다.")

    user_list = get_user_list(room_id)
    user_list.append(user_id)

    user_str = parse_list_into_str(user_list)

    r.hset(room_id, "users", user_str)


def exit_room(room_id, user_id):
    delete_user(user_id)

    user_list = get_user_list(room_id)
    user_list.remove(user_id)

    # 남아 있는 유저가 없으면 방을 삭제한다
    if len(user_list) == 0:
        delete_room(room_id)
    else:
        user_str = parse_list_into_str(user_list)
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