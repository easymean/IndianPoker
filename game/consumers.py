import json
from channels.generic.websocket import AsyncWebsocketConsumer


# I/O가 왼료된 경우에만 await 함수부분이 실행됨
from game.models import EnterMessage, ExitMessage, get_nickname, exit_room, ReadyMessage, get_ready, cancel_ready, \
    WaitMessage


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

        lower_message_type = message_type.lower()
        str_list = [lower_message_type, "message"]

        parsed_type = '_'.join(str_list)

        # send message to room group
        await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': parsed_type,
                    'sender_id': sender_id
                }
        )

    # receive message from room group
    async def enter_message(self, event):
        sender_id = event['sender_id']
        nickname = get_nickname(sender_id)

        info_message = EnterMessage(room_id=self.room_name, sender_id=sender_id, nickname=nickname)

        # send message to websocket
        await self.send(text_data=json.dumps({
            'message': info_message.message
        }))

    async def exit_message(self, event):
        sender_id = event['sender_id']
        nickname = get_nickname(sender_id)

        info_message = ExitMessage(room_id=self.room_name, sender_id=sender_id, nickname=nickname)

        # delete user from database
        exit_room(self.room_name, sender_id)

        # send message to websocket
        await self.send(text_data=json.dumps({
            'message': info_message.message
        }))

    async def ready_message(self, event):
        sender_id = event['sender_id']
        nickname = get_nickname(sender_id)

        info_message = ReadyMessage(room_id=self.room_name, sender_id=sender_id, nickname=nickname)

        get_ready(user_id=sender_id)

        await self.send(text_data=json.dumps({
            'message': info_message.message
        }))

    async def wait_message(self, event):
        sender_id = event['sender_id']
        nickname = get_nickname(sender_id)

        info_message = WaitMessage(room_id=self.room_name, sender_id=sender_id, nickname=nickname)

        cancel_ready(user_id=sender_id)

        await self.send(text_data=json.dumps({
            'message': info_message.message
        }))

