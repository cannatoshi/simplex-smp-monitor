"""
Chutney Django Admin Configuration

Admin-Interface für:
- TorNetwork Management
- TorNode Übersicht
- TrafficCapture Analyse
- CircuitEvent Monitoring
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import TorNetwork, TorNode, TrafficCapture, CircuitEvent


class TorNodeInline(admin.TabularInline):
    """Inline-Anzeige der Nodes in TorNetwork"""
    model = TorNode
    extra = 0
    fields = ['name', 'node_type', 'status', 'control_port', 'or_port', 'fingerprint']
    readonly_fields = ['fingerprint', 'status']
    show_change_link = True


@admin.register(TorNetwork)
class TorNetworkAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'template', 'status_badge', 'total_nodes',
        'running_nodes_count', 'consensus_valid', 'created_at'
    ]
    list_filter = ['status', 'template', 'consensus_valid', 'capture_enabled']
    search_fields = ['name', 'slug', 'description']
    readonly_fields = [
        'id', 'slug', 'docker_network_name', 'container_prefix',
        'bootstrap_progress', 'consensus_valid', 'consensus_valid_after',
        'consensus_fresh_until', 'consensus_valid_until',
        'total_circuits_created', 'total_bytes_transferred', 'total_cells_processed',
        'created_at', 'updated_at', 'started_at', 'stopped_at'
    ]
    
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'name', 'slug', 'description')
        }),
        ('Network Topology', {
            'fields': (
                'template',
                ('num_directory_authorities', 'num_guard_relays'),
                ('num_middle_relays', 'num_exit_relays'),
                ('num_clients', 'num_hidden_services'),
            )
        }),
        ('Port Configuration', {
            'fields': (
                ('base_control_port', 'base_socks_port'),
                ('base_or_port', 'base_dir_port'),
            ),
            'classes': ('collapse',)
        }),
        ('Tor Network Options', {
            'fields': (
                'testing_tor_network', 'voting_interval', 'assume_reachable'
            ),
            'classes': ('collapse',)
        }),
        ('Traffic Capture', {
            'fields': (
                'capture_enabled', 'capture_filter',
                ('max_capture_size_mb', 'capture_rotate_interval'),
            )
        }),
        ('Docker', {
            'fields': ('docker_network_name', 'container_prefix'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': (
                'status', 'status_message', 'bootstrap_progress',
            )
        }),
        ('Consensus', {
            'fields': (
                'consensus_valid',
                ('consensus_valid_after', 'consensus_fresh_until', 'consensus_valid_until'),
            ),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': (
                'total_circuits_created', 'total_bytes_transferred', 'total_cells_processed',
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                ('created_at', 'updated_at'),
                ('started_at', 'stopped_at'),
            ),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [TorNodeInline]
    
    def status_badge(self, obj):
        """Farbige Status-Anzeige"""
        colors = {
            'not_created': '#6b7280',
            'creating': '#3b82f6',
            'bootstrapping': '#f59e0b',
            'running': '#10b981',
            'stopping': '#f59e0b',
            'stopped': '#ef4444',
            'error': '#dc2626',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 10px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(TorNode)
class TorNodeAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'network', 'node_type_badge', 'status_badge',
        'control_port', 'or_port', 'fingerprint_short', 'is_running'
    ]
    list_filter = ['status', 'node_type', 'network', 'capture_enabled']
    search_fields = ['name', 'nickname', 'fingerprint', 'network__name']
    readonly_fields = [
        'id', 'container_id', 'container_name', 'fingerprint', 'v3_identity',
        'onion_address', 'flags', 'bootstrap_progress',
        'bytes_read', 'bytes_written', 'circuits_created', 'circuits_active',
        'bandwidth_rate', 'bandwidth_burst',
        'created_at', 'updated_at', 'started_at', 'last_seen'
    ]
    
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'network', 'name', 'node_type', 'index', 'nickname')
        }),
        ('Docker', {
            'fields': ('container_id', 'container_name')
        }),
        ('Network Ports', {
            'fields': (
                ('control_port', 'socks_port'),
                ('or_port', 'dir_port'),
            )
        }),
        ('Tor Identity', {
            'fields': ('fingerprint', 'v3_identity', 'flags')
        }),
        ('Hidden Service', {
            'fields': ('onion_address', 'hs_port', 'hs_target_port'),
            'classes': ('collapse',)
        }),
        ('Traffic Capture', {
            'fields': ('capture_enabled', 'capture_interface', 'capture_file_path')
        }),
        ('Status', {
            'fields': ('status', 'status_message', 'bootstrap_progress')
        }),
        ('Statistics', {
            'fields': (
                ('bytes_read', 'bytes_written'),
                ('circuits_created', 'circuits_active'),
                ('bandwidth_rate', 'bandwidth_burst'),
            )
        }),
        ('Timestamps', {
            'fields': (
                ('created_at', 'updated_at'),
                ('started_at', 'last_seen'),
            )
        }),
    )
    
    def node_type_badge(self, obj):
        """Farbige Node-Typ Anzeige"""
        colors = {
            'da': '#7c3aed',      # Purple for DA
            'guard': '#3b82f6',   # Blue for Guard
            'middle': '#6b7280',  # Gray for Middle
            'exit': '#f59e0b',    # Orange for Exit
            'client': '#10b981',  # Green for Client
            'hs': '#ec4899',      # Pink for Hidden Service
        }
        color = colors.get(obj.node_type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 10px; font-size: 11px;">{} {}</span>',
            color, obj.node_type_icon, obj.get_node_type_display()
        )
    node_type_badge.short_description = 'Type'
    
    def status_badge(self, obj):
        """Farbige Status-Anzeige"""
        colors = {
            'not_created': '#6b7280',
            'created': '#3b82f6',
            'starting': '#f59e0b',
            'bootstrapping': '#f59e0b',
            'running': '#10b981',
            'stopping': '#f59e0b',
            'stopped': '#ef4444',
            'error': '#dc2626',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 10px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def fingerprint_short(self, obj):
        """Gekürzte Fingerprint-Anzeige"""
        if obj.fingerprint:
            return f"{obj.fingerprint[:8]}..."
        return "-"
    fingerprint_short.short_description = 'Fingerprint'


@admin.register(TrafficCapture)
class TrafficCaptureAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'node', 'capture_type', 'status_badge',
        'packet_count', 'file_size_mb', 'duration_seconds', 'started_at'
    ]
    list_filter = ['status', 'capture_type', 'node__network', 'node__node_type']
    search_fields = ['name', 'node__name', 'node__network__name']
    readonly_fields = [
        'id', 'file_size_bytes', 'file_hash_sha256',
        'packet_count', 'bytes_captured', 'packets_dropped',
        'unique_flows', 'tor_cells_detected',
        'first_packet_time', 'last_packet_time', 'avg_inter_packet_delay_ms',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Identification', {
            'fields': ('id', 'node', 'name', 'capture_type')
        }),
        ('Configuration', {
            'fields': ('filter_expression', 'interface')
        }),
        ('File', {
            'fields': ('file_path', 'file_size_bytes', 'file_hash_sha256')
        }),
        ('Time Range', {
            'fields': (
                ('started_at', 'stopped_at'),
                'duration_seconds',
            )
        }),
        ('Statistics', {
            'fields': (
                ('packet_count', 'bytes_captured', 'packets_dropped'),
                ('unique_flows', 'tor_cells_detected'),
            )
        }),
        ('Timing Analysis', {
            'fields': (
                ('first_packet_time', 'last_packet_time'),
                'avg_inter_packet_delay_ms',
            )
        }),
        ('Analysis', {
            'fields': ('status', 'analysis_notes', 'related_circuit_id')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def status_badge(self, obj):
        """Farbige Status-Anzeige"""
        colors = {
            'recording': '#ef4444',
            'completed': '#10b981',
            'analyzing': '#f59e0b',
            'analyzed': '#3b82f6',
            'error': '#dc2626',
            'deleted': '#6b7280',
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 10px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'


@admin.register(CircuitEvent)
class CircuitEventAdmin(admin.ModelAdmin):
    list_display = [
        'circuit_id', 'event_type_badge', 'purpose', 'path_display_short',
        'build_time_ms', 'event_time', 'source_node'
    ]
    list_filter = ['event_type', 'purpose', 'network', 'source_node']
    search_fields = ['circuit_id', 'status', 'reason', 'network__name']
    readonly_fields = [
        'id', 'path', 'path_length', 'raw_event', 'created_at'
    ]
    date_hierarchy = 'event_time'
    
    fieldsets = (
        ('Event', {
            'fields': ('id', 'network', 'circuit_id', 'event_type', 'purpose')
        }),
        ('Path', {
            'fields': ('path', 'path_length')
        }),
        ('Status', {
            'fields': ('status', 'reason', 'remote_reason')
        }),
        ('Timing', {
            'fields': ('event_time', 'build_time_ms')
        }),
        ('Source', {
            'fields': ('source_node',)
        }),
        ('Raw Data', {
            'fields': ('raw_event',),
            'classes': ('collapse',)
        }),
    )
    
    def event_type_badge(self, obj):
        """Farbige Event-Typ Anzeige"""
        colors = {
            'launched': '#3b82f6',
            'built': '#10b981',
            'extended': '#6b7280',
            'failed': '#ef4444',
            'closed': '#f59e0b',
        }
        color = colors.get(obj.event_type, '#6b7280')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 10px; font-size: 11px;">{}</span>',
            color, obj.get_event_type_display()
        )
    event_type_badge.short_description = 'Event'
    
    def path_display_short(self, obj):
        """Gekürzte Pfad-Anzeige"""
        display = obj.path_display
        if len(display) > 40:
            return f"{display[:40]}..."
        return display
    path_display_short.short_description = 'Path'