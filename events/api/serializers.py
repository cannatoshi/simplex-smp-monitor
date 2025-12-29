"""
Events API - Serializers
"""
from rest_framework import serializers
from events.models import EventLog


class EventLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventLog
        fields = ['id', 'level', 'source', 'message', 'details', 'created_at']
