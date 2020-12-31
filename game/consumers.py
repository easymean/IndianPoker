from channels.generic.websocket import AsyncJsonWebsocketConsumer

# I/O가 왼료된 경우에만 await 함수부분이 실행됨
from game.apis.betting import check_betting, raise_betting, call_betting, is_round_ended, \
    reflect_result_to_points, lose_10_points_when_die
from game.apis.room import user_leave_room, are_both_users_ready, set_game_start, get_round, who_is_next, \
    who_is_winner_loser_and_open_card, increase_order, end_round, init_betting, open_card_after_die
from game.apis.user import find_user, get_user_nickname, set_user_ready, set_user_wait, \
    get_user_card_in_this_round, get_user_point
from game.models import ClientMessage

from utils.exceptions import SocketError, UserDoesNotExist


class GameInfoConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        try:
            user_id = self.scope['user']
            user = find_user(user_id)

            if user == "":
                await self.close(code='User Does Not Exist')
                raise UserDoesNotExist('User Does Not Exist')

            room_id = self.scope['url_route']['kwargs']['room_id']

            await self.channel_layer.group_add(
                user_id,
                self.channel_name
            )

            await self.channel_layer.group_add(
                room_id,
                self.channel_name
            )

            await self.accept()

        except Exception as e:
            print(e)
            await self.close()

    async def disconnect(self, close_code):
        room_id = self.scope['url_route']['kwargs']['room_id']
        user_id = self.scope['user']

        event = {
            'room_id': room_id,
            'sender_id': user_id
        }

        await self.exit_message(event)

    # receive message from websocket
    async def receive_json(self, content):

        message_type = content.get("type", None)
        user_id = self.scope['user']
        room_id = self.scope['url_route']['kwargs']['room_id']

        betting_round = content['round']
        bet = content['bet']

        lower_message_type = message_type.lower()
        parsed_message_type = f'{lower_message_type}.message'

        try:
            if message_type == 'EXIT':
                await self.exit_room(room_id, user_id)
            elif message_type == 'READY':
                await self.set_ready(user_id, room_id)
            elif message_type == 'WAIT':
                await self.set_wait(user_id, room_id)
            elif message_type == 'START':
                await self.start_new_round(room_id)
            elif message_type in ['CHECK']:
                await self.game_check(room_id=room_id, user_id=user_id,
                                      betting_round=betting_round, bet=bet)
            else:
                await self.channel_layer.group_send(
                    room_id,
                    {
                        'type': parsed_message_type,
                        'room_id': room_id,
                        'sender_id': user_id,
                        'round': content['round'],
                        'bet': content['bet']
                    }
                )

        except ValueError as e:
            await self.send_json({"error": e})

    # send message to client
    async def send_message(self, message, message_type):
        await self.send_json(
            {
                'message': message,
                'type': message_type
            }
        )

    async def exit_room(self, room_id, user_id):
        user_leave_room(room_id, user_id)
        await self.channel_layer.group_send(
            room_id, {
                'type': 'exit.message',
                'sender_id': user_id,
                'room_id': room_id
            }
        )

    async def set_ready(self, user_id, room_id):
        set_user_ready(user_id)

        await self.channel_layer.group_send(
            room_id, {
                'type': 'ready.message',
                'sender_id': user_id
            }
        )

        if are_both_users_ready(room_id):
            await self.start_game(room_id)
            await self.start_new_round(room_id)

    async def set_wait(self, user_id, room_id):
        set_user_wait(user_id)
        await self.channel_layer.group_send(
            room_id,{
                'type': 'wait.message',
                'sender_id': user_id
            }
        )

    async def start_game(self, room_id):
        set_game_start(room_id)
        await self.channel_layer.group_send(
            room_id, {
                'type': 'start.message'
            }
        )

    async def end_game(self):
        pass

    async def start_new_round(self, room_id):
        betting_round = get_round(room_id)
        await self.channel_layer.group_send(
            room_id, {
                'type': 'round_message',
                'round': betting_round
            }
        )
        await self.get_next_turn(room_id, betting_round)

    # group 전체에 이번 순서가 누구인지 알려주고 해당하는 개인에게 카드를 보여줌
    async def get_next_turn(self, room_id, betting_round):
        next_turn, opponent = who_is_next(room_id)
        opponent_card = get_user_card_in_this_round(opponent, betting_round)
        increase_order(room_id)
        await self.channel_layer.group_send(
            room_id, {
                'type': 'turn.message',
                'sender_id': next_turn
            }
        )

        await self.channel_layer.group_send(
            next_turn, {
                'type': 'choice.message',
                'next_user': next_turn,
                'opponent_card': opponent_card,
                'room_id': room_id,
                'round': betting_round
            }
        )

    async def game_check(self, room_id, user_id, bet, betting_round):
        round_ended = is_round_ended(room_id)

        increment = check_betting(room_id, user_id, bet)

        await self.channel_layer.group_send(
            room_id, {
                'type': 'check.message',
                'sender_id': user_id,
                'bet': increment
            }
        )

        if round_ended:
            await self.get_game_result(room_id=room_id,
                                       betting_round=betting_round)
        else:
            await self.get_next_turn(room_id, betting_round)

    async def game_bet(self, room_id, user_id, bet, betting_round):
        increment = raise_betting(room_id, user_id, bet)
        await self.channel_layer.group_send(
            room_id, {
                'type': 'check.message',
                'sender_id': user_id,
                'bet': increment,
            }
        )

        await self.get_next_turn(room_id, betting_round)

    async def game_die(self, room_id, user_id, betting_round):
        await self.channel_layer.group_send(
            room_id, {
                'type': 'die.message',
                'sender_id': user_id,
            }
        )
        await self.get_game_result(room_id=room_id,
                                   betting_round=betting_round, loser=user_id)

    async def game_raise(self, room_id, user_id, bet, betting_round):
        increased = raise_betting(room_id, user_id, bet)
        await self.channel_layer.group_send(
            room_id, {
                'type': 'raise.message',
                'sender_id': user_id,
                'bet': increased
            }
        )
        await self.get_next_turn(room_id, betting_round)

    async def game_call(self, room_id, user_id, bet, betting_round):
        increment = call_betting(room_id, user_id, bet)

        await self.channel_layer.group_send(
            room_id, {
                'type': 'call.message',
                'sender_id': user_id,
                'bet': increment
            }
        )

        await self.get_game_result(room_id=room_id,
                                   betting_round=betting_round)

    async def get_game_result(self, room_id, betting_round, loser=None):
        die = False
        if loser is not None:
            die = True
            [(winner, winner_card), (loser, loser_card)] = open_card_after_die(room_id, betting_round, loser)
        else:
            [(winner, winner_card), (loser, loser_card)] = who_is_winner_loser_and_open_card(room_id, betting_round)

        if winner == 'TIE':
            await self.channel_layer.group_send(
                room_id, {
                    'type': 'tie.message',
                    'card': winner_card
                }
            )

        else:
            if die is True:
                lose_10_points_when_die(winner, loser)
            else:
                reflect_result_to_points(room_id, winner, loser)

            winner_point = get_user_point(user_id=winner)
            loser_point = get_user_point(user_id=loser)

            await self.channel_layer.group_send(
                winner, {
                    'type': 'result.message',
                    'winner': winner,
                    'loser': loser,
                    'my_card': winner_card,
                    'opponent_card': loser_card,
                    'my_point': winner_point
                }
            )

            await self.channel_layer.group_send(
                loser, {
                    'type': 'result.message',
                    'winner': winner,
                    'loser': loser,
                    'my_card': loser_card,
                    'opponent_card': winner_card,
                    'my_point': loser_point
                }
            )
            init_betting(room_id)

        end_round(room_id)
        if betting_round < 10:
            await self.start_new_round(room_id)
        else:
            await self.end_game()

    # 방에 입장시 채널 그룹에 조인됩니다.
    async def enter_message(self, event):
        nickname = get_user_nickname(event['sender_id'])

        msg = f'{nickname}님이 입장하셨습니다'
        msg_obj = ClientMessage('ENTER', msg)

        # send message to websocket
        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def exit_message(self, event):

        user_id = event['sender_id']
        room_id = event['room_id']
        nickname = get_user_nickname(user_id)

        # leave room group
        await self.channel_layer.group_discard(
            user_id,
            self.channel_name
        )
        await self.channel_layer.group_discard(
            room_id,
            self.channel_name
        )

        msg = f'{nickname}님이 퇴장하셨습니다'
        msg_obj = ClientMessage('EXIT', msg)
        await self.send_message(msg_obj.to_json(), msg_obj.type)

        await self.close()

    async def wait_message(self, event):
        user_id = event['sender_id']

        nickname = get_user_nickname(user_id)
        msg = f'{nickname}님이 레디를 취소했습니다.'
        msg_obj = ClientMessage('WAIT', msg)
        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def ready_message(self, event):
        user_id = event['sender_id']

        nickname = get_user_nickname(user_id)
        msg = f'{nickname}님이 레디를 눌렀습니다.'
        msg_obj = ClientMessage('READY', msg)
        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def start_message(self, event):
        msg2 = '5초 후에 게임이 시작됩니다.'
        msg_obj2 = ClientMessage('START', msg2)
        await self.send_message(msg_obj2.to_json(), msg_obj2.type)

    async def round_message(self, event):
        this_round = event['round']

        if this_round < 10:
            msg = f'{this_round}라운드 입니다.'
        else:
            msg = '마지막 라운드입니다.'

        msg_obj = ClientMessage('ROUND', msg)
        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def turn_message(self, event):
        next_user = event['sender_id']
        nickname = get_user_nickname(next_user)
        msg = f'{nickname}님 차례입니다.'
        msg_obj = ClientMessage('ORDER', msg)
        msg_obj.this_turn = next_user
        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def choice_message(self, event):
        next_user = event['next_user']
        opponent_card = event['opponent_card']
        this_round = event['round']

        nickname = get_user_nickname(next_user)
        msg = f'{nickname}님 선택해주세요'
        msg_obj = ClientMessage('GAME', msg)
        msg_obj.this_round = this_round
        msg_obj.my_point = get_user_point(next_user)
        msg_obj.set_card_info(me=next_user, opponent_card=opponent_card)
        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def check_message(self, event):
        user_id = event['sender_id']

        nickname = get_user_nickname(user_id)
        msg = f'{nickname}님이 check했습니다.'
        msg_obj = ClientMessage('CHECK', msg)
        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def bet_message(self, event):
        user_id = event['sender_id']
        bet = event['bet']

        nickname = get_user_nickname(user_id)
        msg = f'{nickname}이 {bet}만큼 베팅 금액을 올렸습니다. .'
        msg_obj = ClientMessage('BET', msg)
        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def call_message(self, event):
        user_id = event['sender_id']
        nickname = get_user_nickname(user_id)

        msg = f'{nickname}이 올린 금액을 승낙했습니다.'
        msg_obj = ClientMessage('CALL', msg)
        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def die_message(self, event):
        user_id = event['sender_id']
        nickname = get_user_nickname(user_id)

        msg = f'{nickname}이 포기했습니다.'
        msg_obj = ClientMessage('DIE', msg)
        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def tie_message(self, event):
        card = event['card']
        msg = '무승부입니다.'
        msg_obj = ClientMessage('TIE', msg)
        msg_obj.set_result('TIE', 'TIE', card, card)
        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def result_message(self, event):
        winner = event['winner']
        loser = event['loser']
        my_card = event['my_card']
        opponent_card = event['opponent_card']
        my_point = event['my_point']

        msg = '라운드가 끝났습니다. 결과를 확인해주세요'
        msg_obj = ClientMessage('RESULT', msg)
        msg_obj.set_result(winner, loser, my_card, opponent_card)
        msg_obj.my_point = my_point
        await self.send_message(msg_obj.to_json(), msg_obj.type)
