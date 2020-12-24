from channels.generic.websocket import AsyncJsonWebsocketConsumer

# I/O가 왼료된 경우에만 await 함수부분이 실행됨
from game.models import get_nickname, are_both_users_ready, ClientMessage, exit_room, get_ready, cancel_ready, \
    start_game, get_group_name, check_betting
from utils.exceptions import SocketError


class GameInfoConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'game_{self.room_id}'
        await self.accept()

    async def disconnect(self, close_code):
        pass

    # receive message from websocket
    async def receive_json(self, content):

        message_type = content.get("type", None)
        print(message_type)

        user_id = content['sender_id']

        try:
            if message_type == "ENTER":
                await self.enter_room(user_id)

            elif message_type == "EXIT":
                await self.exit_room(user_id)

            else:
                await self.send_room(message_type, content)

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
    async def enter_room(self, user_id):

        # join group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name,
        )

        # send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game.join',
                'sender_id': user_id,
            }
        )

    async def exit_room(self, user_id):

        nickname = get_nickname(user_id)

        # delete user from database
        exit_room(self.room_id, user_id)

        # leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        msg = f'{nickname}님이 퇴장하셨습니다'
        msg_obj = ClientMessage('EXIT', msg)

        # send message to websocket
        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def send_room(self, message_type, message):

        # parse message choice
        lower_message_type = message_type.lower()
        parsed_message_choice = f'game.{lower_message_type}'

        if message_type in ['READY', 'WAIT', 'START']:

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': parsed_message_choice,
                    'sender_id': message['sender_id'],
                }
            )

        elif message_type in ['CHECK', 'BET', 'DIE']:
            user_id = message['sender_id']
            user_group_name = f'user_{user_id}'

            await self.channel_layer.group_add(
                user_group_name,
                self.channel_name,
            )

            await self.channel_layer.group_send(
                user_group_name,
                {
                    'type': parsed_message_choice,
                    'sender_id': message['sender_id'],
                    'bet': message['bet']
                }
            )

    async def game_join(self, event):
        nickname = get_nickname(event['sender_id'])

        msg = f'{nickname}님이 입장하셨습니다'
        msg_obj = ClientMessage('ENTER', msg)

        # send message to websocket
        await self.send_message(msg_obj.to_json(), msg_obj.type)

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
        bet = event['bet']

        check_betting(self.room_id, user_id, bet)

        nickname = get_nickname(user_id)
        msg = f'{nickname} 님이 check했습니다.'
        msg_obj = ClientMessage('CHECK', msg)

        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def game_bet(self, event):
        user_id = event['sender_id']
        bet = event['bet']
        pass

    async def call_message(self, event):
        pass

    async def raise_message(self, event):
        pass

    async def die_message(self, event):
        pass
