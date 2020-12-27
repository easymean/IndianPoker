from utils.redis_client import r


def check_betting(room_id, user_id, bet):
    z_name = f'{room_id}:betting'
    r.zincrby(z_name, bet, user_id)

    last_choice = r.hget(room_id, 'last_choice').decode()

    if last_choice == 'CHECK':
        return True
    else:
        r.hset(room_id, 'last_choice', 'CHECK')
        r.hincrby(room_id, 'order', 1)
        return False


def call_betting(room_id, user_id):
    pass


def raise_betting(room_id, user_id, increment):
    z_name = f'{room_id}:betting'
    increased = r.zincrby(z_name, {user_id: increment})
    r.hincrby(room_id, 'order', 1)
    return increased


def die(room_id, user_id, this_round):
    pass