from channels.generic.websocket import AsyncJsonWebsocketConsumer

# I/O가 왼료된 경우에만 await 함수부분이 실행됨
from game.methods.betting import check_betting, raise_betting
from game.models import get_nickname, are_both_users_ready, ClientMessage, exit_room, get_ready, cancel_ready, \
    start_game, get_user_list, find_user, get_user_group_name, get_room_group_name

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
            room_id: room_id,
            user_id: user_id
        }
        #await self.game_exit(event)

        await self.close(close_code)

    # receive message from websocket
    async def receive_json(self, content):

        message_type = content.get("type", None)
        user_id = self.scope['user']
        room_id = self.scope['url_route']['kwargs']['room_id']

        lower_message_type = message_type.lower()
        parsed_message_type = f'game.{lower_message_type}'

        try:
            if message_type in ['ENTER', 'EXIT', 'READY', 'WAIT']:
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': parsed_message_type,
                        'room_id': room_id,
                        'sender_id': user_id,
                    }
                )
            else:
                await self.channel_layer.group_send(
                    room_id,
                    {
                        'type': parsed_message_type,
                        'room_id': room_id,
                        'sender_id': user_id,
                        'bet': content['bet']
                    }
                )

        except ValueError as e:
            await self.send_json({"error": e.code})

    # send message to client
    async def send_message(self, message, message_type):
        await self.send_json(
            {
                'message': message,
                'type': message_type
            }
        )

    # 방에 입장시 채널 그룹에 조인됩니다.
    async def game_enter(self, event):
        nickname = get_nickname(event['sender_id'])

        msg = f'{nickname}님이 입장하셨습니다'
        msg_obj = ClientMessage('ENTER', msg)

        # send message to websocket
        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def game_exit(self, event):

        user_id = event['sender_id']
        room_id = event['room_id']
        nickname = get_nickname(user_id)

        # leave room group
        await self.channel_layer.group_discard(
            user_id,
            self.channel_name
        )
        await self.channel_layer.group_discard(
            room_id,
            self.channel_name
        )

        exit_room(room_id, user_id)

        msg = f'{nickname}님이 퇴장하셨습니다'
        msg_obj = ClientMessage('EXIT', msg)
        await self.send_message(msg_obj.to_json(), msg_obj.type)

        await self.close()

    async def game_ready(self, event):
        user_id = event['sender_id']
        get_ready(user_id)

        nickname = get_nickname(user_id)
        msg = f'{nickname}님이 레디를 눌렀습니다.'
        msg_obj = ClientMessage('READY', msg)
        await self.send_message(msg_obj.to_json(), msg_obj.type)

        if are_both_users_ready(self.room_id):
            msg2 = '5초 후에 게임이 시작됩니다.'
            msg_obj2 = ClientMessage('START', msg2)
            await self.send_message(msg_obj2.to_json(), msg_obj2.type)

    async def game_start(self, event):
        user_id = event['sender_id']

        start_game(self.room_id)

        nickname = get_nickname(user_id)
        msg = f'{nickname}님 차례입니다. 베팅해주세요.'
        msg_obj = ClientMessage('GAME', msg)

        msg_obj.start_game(room_id=self.room_id, me=user_id)

        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def game_wait(self, event):
        user_id = event['sender_id']
        cancel_ready(user_id)

        nickname = get_nickname(user_id)
        msg = f'{nickname}님이 레디를 취소했습니다.'
        msg_obj = ClientMessage('WAIT', msg)
        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def game_check(self, event):
        user_id = event['sender_id']
        room_id = event['room_id']
        bet = event['bet']

        check_betting(room_id, user_id, bet)

        nickname = get_nickname(user_id)
        msg = f'{nickname}님이 check했습니다.'
        msg_obj = ClientMessage('CHECK', msg)

        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def game_bet(self, event):
        user_id = event['sender_id']
        room_id = event['room_id']
        bet = event['bet']

        nickname = get_nickname(user_id)
        increment = raise_betting(room_id, user_id, bet)

        msg = f'{nickname}이 {increment}만큼 판돈을 올렸습니다.'
        msg_obj = ClientMessage('BET', msg)
        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def call_message(self, event):

        user_id = event['sender_id']
        room_id = event['room_id']
        bet = event['bet']

        nickname = get_nickname(user_id)
        check_betting(room_id, user_id, bet)

        msg = f'{nickname}이 올린 금액을 승낙했습니다.'
        msg_obj = ClientMessage('CALL', msg)
        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def raise_message(self, event):
        pass

    async def die_message(self, event):
        pass
