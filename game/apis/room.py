from game.apis.common import parse_bytes_into_list, parse_list_into_str, parse_bytes_into_int
from game.apis.user import check_user_state, give_users_cards, delete_user, get_user_card_in_this_round
from game.models import UserState, RoomState
from utils.exceptions import InvalidMethod
from utils.redis_client import r


def get_room_group_name(room_id):
    return f'game_{room_id}'


def find_room(room_id):
    return r.hvals(room_id)


def delete_room(room_id):
    r.delete(room_id)


def is_user_in_room(room_id):
    if r.hexists(room_id, "users"):
        return True
    else:
        return False


def get_user_list(room_id):
    users_str = r.hget(room_id, "users")
    return parse_bytes_into_list(users_str)


def get_user_count(room_id):
    user_list = get_user_list(room_id)
    return len(user_list)


def check_room_state(room_id):
    return r.hget(room_id, "state").decode()


def are_both_users_ready(room_id):
    user_list = get_user_list(room_id)
    for user in user_list:
        if check_user_state(user) != UserState.READY:
            print(check_user_state(user))
            return False
    return True


def set_game_start(room_id):
    if check_room_state(room_id) == RoomState.START:
        raise InvalidMethod("이미 시작 상태입니다.")

    r.hset(room_id, "state", "START")
    r.hset(room_id, 'round', 0)
    r.hset(room_id, 'order', 0)

    user_list = get_user_list(room_id)
    give_users_cards(user_list[0], user_list[1])
    print('set game start')


def end_game(room_id):
    if check_room_state(room_id) != RoomState.START:
        raise InvalidMethod('게임이 시작되지 않았습니다.')

    r.hset(room_id, 'state', 'READY')
    r.hset(room_id, 'round', 0)
    r.hset(room_id, 'order', 0)


def init_betting(room_id):
    zset_key = f'{room_id}:betting'
    r.delete(zset_key)


def end_round(room_id):
    r.hdel(room_id, 'last_choice')
    r.hincrby(room_id, 'round', 1)


def get_round(room_id):
    bytes_round = r.hget(room_id, 'round')
    return parse_bytes_into_int(bytes_round)


def get_order(room_id):
    bytes_order = r.hget(room_id, 'order')
    return parse_bytes_into_int(bytes_order)


def increase_order(room_id):
    r.hincrby(room_id, 'order', 1)


def user_enter_room(room_id, user_id):
    if is_user_in_room(room_id):

        user_list = get_user_list(room_id)

        if user_id in user_list:
            print("이미 존재하는 사용자입니다.")
            return

        if get_user_count(room_id) == 2:
            raise InvalidMethod("방이 가득 찼습니다.")

        user_list.append(user_id)
        user_str = parse_list_into_str(user_list)
        r.hset(room_id, "users", user_str)

    else:
        r.hset(room_id, "users", user_id)


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


def who_is_next(room_id):
    user_list = get_user_list(room_id)
    order = get_order(room_id)

    next_user = user_list[order % 2]
    opponent = user_list[(order+1) % 2]
    return next_user, opponent


def open_card_after_die(room_id, this_round, loser):
    user_list = get_user_list(room_id)
    winner = ''
    for user in user_list:
        if user != loser:
            winner = user

    winner_card = get_user_card_in_this_round(user_id=winner, this_round=this_round)
    loser_card = get_user_card_in_this_round(user_id=loser, this_round=this_round)
    return [(winner, winner_card), (loser, loser_card)]


def who_is_winner_loser_and_open_card(room_id, this_round):

    user_list = get_user_list(room_id)

    card_list = []
    for user in user_list:
        card = get_user_card_in_this_round(user, this_round)
        card_list.append(card)

    if card_list[0] < card_list[1]:
        return [(user_list[1], card_list[1]), (user_list[0], card_list[0])]
    elif card_list[0] > card_list[1]:
        return [(user_list[0], card_list[0]), (user_list[1], card_list[1])]
    else:
        return [('TIE', card_list[0]), ('TIE', card_list[1])]
