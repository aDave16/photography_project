from channels.generic.websocket import AsyncWebsocketConsumer
import json

class CalendarConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'calendar'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # For now, admin/frontend only receive broadcast messages; optionally handle client messages
        try:
            data = json.loads(text_data or '{}')
            # simple echo/backbone - not used by default
            await self.channel_layer.group_send(self.group_name, {
                'type': 'calendar.message',
                'message': data
            })
        except Exception:
            pass

    async def calendar_message(self, event):
        # event['message'] is JSON-serializable
        await self.send(text_data=json.dumps(event.get('message', {})))
