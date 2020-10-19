import json
from channels.generic.websocket import AsyncWebsocketConsumer


# I/O가 왼료된 경우에만 await 함수부분이 실행됨
from game.models import EnterMessage, ExitMessage, get_nickname


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
        print("received from websocket")
        text_data_json = json.loads(text_data)
        # message_type = text_data_json['type']
        # sender_id = text_data_json['sender_id']

        # send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'info_message',
                'message': text_data_json
            }
        )

    # receive message from room group
    async def info_message(self, event):

        msg = event['message']

        message_type = msg['type']
        sender_id = msg['sender_id']
        nickname = get_nickname(sender_id)
        room_id = self.room_name

        print("send to websocket")
        if 'ENTER' == message_type:
            info_message = EnterMessage(room_id=room_id, sender_id=sender_id, nickname=nickname)

            # send message to websocket
            await self.send(text_data=json.dumps({
                'message': info_message.message
            }))

        if 'EXIT' == message_type:
            info_message = ExitMessage(room_id=room_id, sender_id=sender_id, nickname=nickname)

            # send message to websocket
            await self.send(text_data=json.dumps({
                'message': info_message.message
            }))
