from utils.redis_client import r


def check_betting(room_id, user_id, bet):
    z_name = f'{room_id}:betting'
    r.zincrby(z_name, bet, user_id)


def raise_betting(room_id, user_id, increment):
    z_name = f'{room_id}:betting'
    increased = r.zincrby(z_name, {user_id: increment})
    return increased
