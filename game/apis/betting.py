from game.apis.common import parse_bytes_into_str
from utils.redis_client import r


def is_round_ended(room_id):
    if r.hexists(room_id, 'last_choice'):
        return True
    else:
        return False


def check_betting(room_id, user_id, bet):
    zset_key = f'{room_id}:betting'
    r.hset(room_id, 'last_choice', 'CHECK')
    increment = r.zincrby(zset_key, bet, user_id)
    r.hset(user_id, 'point', -bet)
    return increment


def call_betting(room_id, user_id, bet):
    zset_key = f'{room_id}:betting'
    r.hset(user_id, 'point', -bet)
    r.hset(room_id, 'last_choice', 'CALL')
    increment = r.zincrby(zset_key, bet, user_id)
    return increment


def raise_betting(room_id, user_id, bet):
    zset_key = f'{room_id}:betting'
    r.hset(user_id, 'point', -bet)
    increment = r.zincrby(zset_key, bet, user_id)

    if r.hexists(room_id, 'last_choice'):
        r.hset(room_id, 'last_choice', 'RAISE')
    else:
        r.hset(room_id, 'last_choice', 'BET')
    return increment


def lose_10_points_when_die(winner, loser):
    r.hincrby(winner, 'point', 10)
    r.hincrby(loser, 'point', 10)


def reflect_result_to_points(room_id, winner, loser):
    zset_key = f'{room_id}:betting'
    pair_list = r.zrange(name=zset_key, start=0, end=-1, withscores=True)
    for (user, score) in pair_list:
        parsed_user = parse_bytes_into_str(user)
        int_score = int(score)
        if parsed_user == loser:
            r.hincrby(winner, 'point', int_score)
        else:
            r.hincrby(loser, 'point', -int_score)
