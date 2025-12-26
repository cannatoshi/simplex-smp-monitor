"""
Django Admin Konfiguration für SimpleX CLI Clients
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import SimplexClient, ClientConnection, TestMessage, DeliveryReceipt


@admin.register(SimplexClient)
class SimplexClientAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'status_badge', 'websocket_port', 
                    'messages_sent', 'messages_received', 'is_running', 'last_active_at']
    list_filter = ['status', 'use_tor', 'created_at']
    search_fields = ['name', 'slug', 'profile_name']
    readonly_fields = ['id', 'container_id', 'created_at', 'updated_at', 'last_active_at']
    filter_horizontal = ['smp_servers']
    
    fieldsets = (
        ('Identifikation', {
            'fields': ('id', 'name', 'slug', 'profile_name')
        }),
        ('Docker', {
            'fields': ('container_id', 'container_name', 'websocket_port', 'data_volume')
        }),
        ('Status', {
            'fields': ('status', 'last_error')
        }),
        ('Konfiguration', {
            'fields': ('smp_servers', 'use_tor')
        }),
        ('Statistiken', {
            'fields': ('messages_sent', 'messages_received', 'messages_failed'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_active_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'created': '#6b7280',   # gray
            'starting': '#f59e0b',  # amber
            'running': '#10b981',   # green
            'stopping': '#f59e0b',  # amber
            'stopped': '#6b7280',   # gray
            'error': '#ef4444',     # red
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 8px; '
            'border-radius: 4px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(ClientConnection)
class ClientConnectionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'status', 'created_at', 'connected_at']
    list_filter = ['status', 'created_at']
    search_fields = ['client_a__name', 'client_b__name']
    readonly_fields = ['id', 'created_at', 'connected_at', 'updated_at']
    
    fieldsets = (
        ('Clients', {
            'fields': ('client_a', 'client_b')
        }),
        ('Verbindung', {
            'fields': ('invitation_link', 'contact_name_on_a', 'contact_name_on_b')
        }),
        ('Status', {
            'fields': ('status', 'last_error')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'connected_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(TestMessage)
class TestMessageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'delivery_status', 'total_latency_ms', 'created_at']
    list_filter = ['delivery_status', 'created_at', 'sender', 'recipient']
    search_fields = ['content', 'correlation_id']
    readonly_fields = ['id', 'correlation_id', 'sent_at', 'server_received_at', 
                       'client_received_at', 'latency_to_server_ms', 
                       'latency_to_client_ms', 'total_latency_ms', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Routing', {
            'fields': ('connection', 'sender', 'recipient')
        }),
        ('Nachricht', {
            'fields': ('content', 'correlation_id')
        }),
        ('Delivery Status', {
            'fields': ('delivery_status', 'error_message')
        }),
        ('Timing', {
            'fields': ('sent_at', 'server_received_at', 'client_received_at',
                       'latency_to_server_ms', 'latency_to_client_ms', 'total_latency_ms'),
            'classes': ('collapse',)
        }),
        ('Referenzen', {
            'fields': ('test_run',),
            'classes': ('collapse',)
        }),
    )


@admin.register(DeliveryReceipt)
class DeliveryReceiptAdmin(admin.ModelAdmin):
    list_display = ['message', 'receipt_type', 'received_at']
    list_filter = ['receipt_type', 'received_at']
    readonly_fields = ['id', 'received_at', 'raw_event']
