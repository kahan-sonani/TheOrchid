import json

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from app.models import CallLog


class TOAConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        phone = self.scope['url_route']['kwargs']['phone']
        self.room_name = phone
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)
        await self.close(close_code)

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        data['type'] = 'call_message'
        # notify caller that callee accepted the call or not
        if data['code'] == '1' or data['code'] == '2':
            log = await get_call_log(data)
            if data['code'] == 1:
                log.rejected = False
            else:
                log.rejected = True
            log.missed = False
            await sync_to_async(log.save)()
            await self.channel_layer.group_send(data['caller_phone'], data)
            # notify callee for the incoming call
        elif data['code'] == '3':
            await self.channel_layer.group_send(data['callee_phone'], data)
        elif data['code'] == '5':
            # notify callee about call timeout
            if 'closeModal' in data.keys() and not data['closeModal']:
                log = await get_call_log(data)
                log.missed = True
                log.rejected = False
                await sync_to_async(log.save)()
            await self.channel_layer.group_send(data['callee_phone'], data)
        elif data['code'] == '6':
            await self.channel_layer.group_send(data['other_user_phone'], data)
        elif data['code'] == '7':
            await self.channel_layer.group_send(data['other_user_phone'], data)

    async def call_message(self, event):
        await self.send(text_data=json.dumps(event))


@sync_to_async
def get_call_log(data):
    return CallLog.objects.filter(caller__mobileno=data['caller_phone']).order_by('-time')[0]
