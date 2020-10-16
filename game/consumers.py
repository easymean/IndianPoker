import json
from channels.generic.websocket import AsyncWebsocketConsumer


# I/O가 왼료된 경우에만 await 함수부분이 실행됨
from game.models import InfoMessage


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
        type = text_data_json['type']
        sender_id = text_data_json['sender_id']

        # send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': type,
                'room_id': self.room_name,
                'sender_id': sender_id
            }
        )

    # receive message from room group
    async def info_message(self, event):
        type = event['type']

        room_id = self.room_name
        sender_id = self.sender_id

        info_message = InfoMessage(room_id=room_id, sender_id=sender_id)

        if 'ENTER' == type:
            info_message.enter_room()

        # send message to websocket
        await self.send(text_data=json.dumps({
            'message': info_message['message']
        }))