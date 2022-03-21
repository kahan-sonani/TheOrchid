import json

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from app.models import CallLog, ChannelName


class TOAConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()
        response = {
            'code': '4',
            'channel_name': self.channel_name
        }
        await self.send(text_data=json.dumps(response))

    async def disconnect(self, close_code):
        await delete_channel_name(self)
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
            channel = await get_channel(data)
            data['channel_name'] = channel.channel_name
            await self.channel_layer.send(
                data['channel_name'], data)
            # notify callee for the incoming call
        elif data['code'] == '3':
            await self.channel_layer.send(
                data['channel_name'], data)
        elif data['code'] == '5':
            # notify callee about call timeout
            if not data['closeModal']:
                log = await get_call_log(data)
                log.missed = True
                log.rejected = False
            await sync_to_async(log.save)()
            await self.channel_layer.send(
                data['channel_name'], data)

    async def call_message(self, event):
        await self.send(text_data=json.dumps(event))


@sync_to_async
def get_channel(data):
    return ChannelName.objects.get(phone=data['caller_phone'])


@sync_to_async
def delete_channel_name(consumer):
    ChannelName.objects.filter(channel_name=consumer.channel_name).delete()


@sync_to_async
def get_call_log(data):
    return CallLog.objects.filter(caller__mobileno=data['caller_phone']).order_by('-time')[0]

