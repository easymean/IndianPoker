import random, logging

from game.apis.common import parse_list_into_str, parse_bytes_into_list, parse_bytes_into_int, parse_bytes_into_str
from utils.exceptions import ParsingException
from utils.redis_client import r

logger = logging.getLogger('apis.user')


def find_user(user_id):
    return r.hvals(user_id)


def delete_user(user_id):
    r.delete(user_id)


def get_user_state(user_id):
    bytes_state = r.hget(user_id, "state")
    return parse_bytes_into_str(bytes_state)


def get_user_nickname(user_id):
    bytes_nickname = r.hget(user_id, "nickname")
    return parse_bytes_into_str(bytes_nickname)


def get_user_point(user_id):
    bytes_point = r.hget(user_id, "point")
    return parse_bytes_into_int(bytes_point)


def set_user_ready(user_id):
    logger.info(f'{user_id}님이 레디를 누르셨습니다.')
    r.hset(user_id, "state", "READY")


def set_user_wait(user_id):
    logger.info(f'{user_id}님이 레디를 취소하셨습니다.')
    r.hset(user_id, "state", "WAIT")


def give_users_cards(user1, user2):
    list1 = []
    list2 = []
    ran_num = random.randint(1, 10)

    for i in range(10):
        while ran_num in list1:
            ran_num = random.randint(1,10)
        list1.append(ran_num)

    for i in range(10):
        while ran_num in list2:
            ran_num = random.randint(1,10)
        list2.append(ran_num)

    list1_str = parse_list_into_str(map(str, list1))
    list2_str = parse_list_into_str(map(str, list2))

    r.hset(user1, "cards", list1_str)
    r.hset(user2, "cards", list2_str)


def get_user_card_in_this_round(user_id, this_round):
    try:
        cards_bytes = r.hget(user_id, "cards")
        parsed_card_list = parse_bytes_into_list(cards_bytes)
        return parsed_card_list[this_round]
    except Exception as e:
        print(e)
