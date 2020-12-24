import json
from channels.generic.websocket import AsyncWebsocketConsumer

# I/O가 왼료된 경우에만 await 함수부분이 실행됨
from game.models import get_nickname, are_both_users_ready, ClientMessage, exit_room, get_ready, cancel_ready, \
    start_game


class GameInfoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'game_{self.room_name}'

        # join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # receive message from websocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json['type']
        sender_id = text_data_json['sender_id']
        bet = text_data_json['bet']
        nickname = get_nickname(sender_id)

        # 타입에 따라 메세지 파싱
        lower_message_type = message_type.lower()
        str_list = [lower_message_type, "message"]
        parsed_type = '_'.join(str_list)

        # send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': parsed_type,
                'sender_id': sender_id,
                'nickname': nickname,
                'bet': bet,
            }
        )

    async def send_message(self, message, message_type):
        await self.send(
            text_data=json.dumps({
                'message': message,
                'type': message_type
            })
        )

    # receive message from room group
    async def enter_message(self, event):
        nickname = event['nickname']

        msg = f'{nickname}님이 입장하셨습니다'
        msg_obj = ClientMessage('ENTER', msg)

        # send message to websocket
        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def exit_message(self, event):
        sender_id = event['sender_id']
        nickname = event['nickname']

        # delete user from database
        exit_room(self.room_name, sender_id)

        msg = f'{nickname}님이 퇴장하셨습니다'
        msg_obj = ClientMessage('EXIT', msg)

        # send message to websocket
        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def ready_message(self, event):
        sender_id = event['sender_id']
        nickname = event['nickname']
        get_ready(sender_id)

        msg = f'{nickname}님이 레디를 눌렀습니다.'
        msg_obj = ClientMessage('READY', msg)
        await self.send_message(msg_obj.to_json(), msg_obj.type)

        if are_both_users_ready(self.room_name):
            msg2 = '5초 후에 게임이 시작됩니다.'
            msg_obj2 = ClientMessage('START', msg2)
            await self.send_message(msg_obj2.to_json(), msg_obj2.type)

    async def start_message(self, event):
        sender_id = event['sender_id']
        nickname = event['nickname']

        start_game(self.room_name)

        msg = f'{nickname}님 차례입니다. 베팅해주세요.'
        msg_obj = ClientMessage('GAME', msg)
        msg_obj.start_game(room_id=self.room_name, me=sender_id)

        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def wait_message(self, event):
        sender_id = event['sender_id']
        nickname = event['nickname']
        cancel_ready(sender_id)

        msg = f'{nickname}님이 레디를 취소했습니다.'
        msg_obj = ClientMessage('WAIT', msg)

        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def check_message(self, event):
        sender_id = event['sender_id']
        nickname = event['nickname']
        bet = event['bet']

        msg_obj = ClientMessage()
        pass

    async def bet_message(self, event):
        sender_id = event['sender_id']
        nickname = event['nickname']
        bet = event['bet']
        pass

    async def call_message(self, event):
        pass

    async def raise_message(self, event):
        pass

    async def die_message(self, event):
        pass
