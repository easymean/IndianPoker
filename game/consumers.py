import json
from channels.generic.websocket import AsyncWebsocketConsumer

# I/O가 왼료된 경우에만 await 함수부분이 실행됨
from game.models import get_nickname, are_both_users_ready, GameMessage


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

    async def send_message(self, message, type):
        await self.send(
            text_data=json.dumps({
                'message': message,
                'type': type
            })
        )

    # receive message from room group
    async def enter_message(self, event):
        nickname = event['nickname']

        msg_obj = GameMessage()
        msg_obj.send_enter_message(nickname=nickname)
        # send message to websocket
        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def exit_message(self, event):
        sender_id = event['sender_id']
        nickname = event['nickname']

        msg_obj = GameMessage()
        msg_obj.send_exit_message(nickname, self.room_name, sender_id)

        # send message to websocket
        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def ready_message(self, event):
        sender_id = event['sender_id']
        nickname = event['nickname']

        msg_obj = GameMessage()
        msg_obj.send_ready_message(nickname=nickname, user_id=sender_id)
        await self.send_message(msg_obj.to_json(), msg_obj.type)

        if are_both_users_ready(self.room_name):
            msg_obj.send_start_message()
            await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def start_message(self, event):
        sender_id = event['sender_id']
        nickname = event['nickname']

        msg_obj = GameMessage()
        msg_obj.start_game(room_id=self.room_name, me=sender_id, my_nickname=nickname)
        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def wait_message(self, event):
        sender_id = event['sender_id']
        nickname = event['nickname']

        msg_obj = GameMessage()
        msg_obj.send_wait_message(nickname, sender_id)

        await self.send_message(msg_obj.to_json(), msg_obj.type)

    async def check_message(self, event):
        sender_id = event['sender_id']
        nickname = event['nickname']
        # bet = event['bet']
        pass

    async def bet_message(self, event):
        sender_id = event['sender_id']
        nickname = event['nickname']
        # bet = event['bet']
        pass

    async def call_message(self, event):
        pass

    async def raise_message(self, event):
        pass

    async def die_message(self, event):
        pass
