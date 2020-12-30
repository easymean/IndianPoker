from game.apis.common import parse_bytes_into_str
from utils.redis_client import r


def if_round_ended(room_id):
    if r.hexists(room_id, 'last_choice'):
        return True
    else:
        r.hset(room_id, 'last_choice', 'CHECK')
        return False


def check_betting(room_id, user_id, bet):
    z_name = f'{room_id}:betting'
    increment = r.zincrby(z_name, bet, user_id)
    r.hset(user_id, 'point', -bet)
    return increment


def call_betting(room_id, user_id, bet):
    z_name = f'{room_id}:betting'
    r.hset(user_id, 'point', -bet)
    r.hset(room_id, 'last_choice', 'CALL')
    increment = r.zincrby(z_name, bet, user_id)
    return increment


def raise_betting(room_id, user_id, bet):
    z_name = f'{room_id}:betting'
    r.hset(user_id, 'point', -bet)
    increased = r.zincrby(z_name, bet, user_id)

    if r.hexists(room_id, 'last_choice'):
        r.hset(room_id, 'last_choice', 'RAISE')
    else:
        r.hset(room_id, 'last_choice', 'BET')
    return increased


# 포기한 플레이어 카드가 10이면 5포인트를 잃는다.
def loose_when_die(winner, loser):
    r.hincrby(winner, 'point', 10)
    r.hincrby(loser, 'point', 10)


def total_up_points(room_id, winner, loser):
    z_name = f'{room_id}:betting'
    pair_list = r.zrange(name=z_name, start=0, end=-1, withscores=True)
    for (v, s) in pair_list:
        parsed_v = parse_bytes_into_str(v)
        int_s = int(s)
        if parsed_v == loser:
            r.hincrby(winner, 'point', int_s)
        else:
            r.hincrby(loser, 'point', -int_s)
