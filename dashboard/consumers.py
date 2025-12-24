import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class DashboardConsumer(AsyncWebsocketConsumer):
    """WebSocket Consumer für Echtzeit-Dashboard Updates"""
    
    async def connect(self):
        self.room_group_name = 'dashboard'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        # Initial stats senden
        await self.send_stats()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        msg_type = data.get('type')
        
        if msg_type == 'get_stats':
            await self.send_stats()
    
    async def send_stats(self):
        stats = await self.get_dashboard_stats()
        await self.send(text_data=json.dumps({
            'type': 'stats_update',
            'data': stats
        }))
    
    @database_sync_to_async
    def get_dashboard_stats(self):
        from servers.models import Server
        from stresstests.models import TestRun
        return {
            'server_count': Server.objects.count(),
            'active_servers': Server.objects.filter(is_active=True).count(),
            'running_tests': TestRun.objects.filter(status='running').count(),
            'total_tests': TestRun.objects.count(),
        }
    
    async def stats_update(self, event):
        """Handler für Broadcast-Updates"""
        await self.send(text_data=json.dumps({
            'type': 'stats_update',
            'data': event['data']
        }))


class TestConsumer(AsyncWebsocketConsumer):
    """WebSocket Consumer für Test-Echtzeit-Updates"""
    
    async def connect(self):
        self.test_id = self.scope['url_route']['kwargs']['test_id']
        self.room_group_name = f'test_{self.test_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
    
    async def test_update(self, event):
        """Handler für Test-Updates"""
        await self.send(text_data=json.dumps({
            'type': 'test_update',
            'data': event['data']
        }))
    
    async def metric_update(self, event):
        """Handler für neue Metriken"""
        await self.send(text_data=json.dumps({
            'type': 'metric',
            'data': event['data']
        }))
