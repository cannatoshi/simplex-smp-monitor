"""
SimpleX SMP Monitor by cannatoshi
GitHub: https://github.com/cannatoshi/simplex-smp-monitor
Licensed under AGPL-3.0

API Views for SimpleX CLI Clients

Contains ViewSets and API endpoints for:
- SimplexClient CRUD + actions (start, stop, restart, logs)
- ClientConnection management
- TestMessage listing and deletion
- Latency history with pagination
- Latency statistics for graphs
- Reset actions (messages, counters, latency, all)
"""
import logging
from datetime import timedelta

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from django.db.models import Sum, Q, Avg, Min, Max, Count
from django.utils import timezone

from clients.models import SimplexClient, ClientConnection, TestMessage, ClientTestRun as TestRun
from .serializers import (
    SimplexClientListSerializer,
    SimplexClientDetailSerializer,
    SimplexClientCreateUpdateSerializer,
    ClientConnectionSerializer,
    TestMessageSerializer,
    LatencyHistorySerializer,
    LatencyStatsSerializer,
    ClientStatsSerializer,
)

logger = logging.getLogger(__name__)


# =============================================================================
# PAGINATION
# =============================================================================

class LatencyHistoryPagination(PageNumberPagination):
    """
    Pagination for latency history.
    
    - Default: 50 items per page
    - Max: 100 items per page
    - Supports page_size query param
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 100


# =============================================================================
# CLIENT VIEWSET
# =============================================================================

class SimplexClientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SimpleX CLI Clients.
    
    Provides CRUD operations plus custom actions:
    - start: Start the Docker container
    - stop: Stop the Docker container
    - restart: Restart the Docker container
    - logs: Get container logs
    - connections: List client connections
    - latency-history: Paginated latency history for modal
    - latency-stats: Statistics and time series for graphs
    - latency-recent: Last 15 latencies for mini graph
    - reset-messages: Delete all messages and reset counters
    - reset-counters: Recalculate counters from database
    - reset-latency: Clear latency data only
    - reset-all: Full reset (delete all + reset counters)
    """
    queryset = SimplexClient.objects.all()
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SimplexClientListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return SimplexClientCreateUpdateSerializer
        return SimplexClientDetailSerializer
    
    def get_queryset(self):
        queryset = SimplexClient.objects.all().order_by('name')
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset
    
    # =========================================================================
    # GLOBAL STATS (for dashboard and forms)
    # =========================================================================
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get global client statistics including available ports"""
        stats = {
            'total': SimplexClient.objects.count(),
            'running': SimplexClient.objects.filter(status=SimplexClient.Status.RUNNING).count(),
            'stopped': SimplexClient.objects.filter(status=SimplexClient.Status.STOPPED).count(),
            'error': SimplexClient.objects.filter(status=SimplexClient.Status.ERROR).count(),
            'total_messages_sent': SimplexClient.objects.aggregate(total=Sum('messages_sent'))['total'] or 0,
            'total_messages_received': SimplexClient.objects.aggregate(total=Sum('messages_received'))['total'] or 0,
        }
        
        # Available ports (first 10 free ports)
        used_ports = set(SimplexClient.objects.values_list('websocket_port', flat=True))
        stats['available_ports'] = [p for p in range(3031, 3081) if p not in used_ports][:10]
        
        return Response(stats)
    
    def perform_destroy(self, instance):
        """Delete client and its Docker container"""
        try:
            from clients.services.docker_manager import get_docker_manager
            docker_manager = get_docker_manager()
            docker_manager.delete_container(instance, remove_volume=False)
        except Exception:
            pass
        instance.delete()
    
    # =========================================================================
    # CONTAINER ACTIONS
    # =========================================================================
    
    @action(detail=True, methods=['post'])
    def start(self, request, id=None):
        """Start the Docker container for this client"""
        client = self.get_object()
        if client.status == SimplexClient.Status.RUNNING:
            return Response(
                {'error': f'{client.name} is already running.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            from clients.services.docker_manager import get_docker_manager
            docker_manager = get_docker_manager()
            docker_manager.start_container(client)
            client.start()
            return Response({
                'success': True,
                'status': client.status,
                'message': f'{client.name} started successfully.'
            })
        except Exception as e:
            logger.exception(f'Failed to start client {client.name}')
            client.set_error(str(e))
            return Response(
                {'error': 'Failed to start client'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def stop(self, request, id=None):
        """Stop the Docker container for this client"""
        client = self.get_object()
        if client.status != SimplexClient.Status.RUNNING:
            return Response(
                {'error': f'{client.name} is not running.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            from clients.services.docker_manager import get_docker_manager
            docker_manager = get_docker_manager()
            docker_manager.stop_container(client)
            client.stop()
            return Response({
                'success': True,
                'status': client.status,
                'message': f'{client.name} stopped successfully.'
            })
        except Exception as e:
            logger.exception(f'Failed to stop client {client.name}')
            client.set_error(str(e))
            return Response(
                {'error': 'Failed to stop client'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def restart(self, request, id=None):
        """Restart the Docker container for this client"""
        client = self.get_object()
        try:
            from clients.services.docker_manager import get_docker_manager
            docker_manager = get_docker_manager()
            docker_manager.restart_container(client)
            client.start()
            return Response({
                'success': True,
                'status': client.status,
                'message': f'{client.name} restarted successfully.'
            })
        except Exception as e:
            logger.exception(f'Failed to restart client {client.name}')
            client.set_error(str(e))
            return Response(
                {'error': 'Failed to restart client'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def logs(self, request, id=None):
        """Get container logs for this client"""
        client = self.get_object()
        tail = int(request.query_params.get('tail', 50))
        try:
            from clients.services.docker_manager import get_docker_manager
            docker_manager = get_docker_manager()
            logs = docker_manager.get_container_logs(client, tail=tail) or ''
            return Response({
                'logs': logs[:50000],
                'status': client.status
            })
        except Exception as e:
            logger.exception(f'Failed to get logs for client {client.name}')
            return Response({
                'logs': '[Error fetching logs]',
                'status': client.status
            })
    
    @action(detail=True, methods=['get'])
    def connections(self, request, id=None):
        """List all connections for this client"""
        client = self.get_object()
        connections = ClientConnection.objects.filter(
            Q(client_a=client) | Q(client_b=client)
        ).select_related('client_a', 'client_b')
        serializer = ClientConnectionSerializer(connections, many=True)
        return Response(serializer.data)
    
    # =========================================================================
    # LATENCY ENDPOINTS
    # =========================================================================
    
    @action(detail=True, methods=['get'], url_path='latency-history')
    def latency_history(self, request, id=None):
        """
        Get paginated latency history for the modal.
        
        Query Parameters:
        - page: Page number (default: 1)
        - page_size: Items per page (default: 50, max: 100)
        - sort: Sort field with optional - prefix for descending
          Options: created_at, total_latency_ms, sender__name, 
                   recipient__name, delivery_status
        - status: Filter by delivery_status (delivered, sent, failed, sending)
        - date_from: Filter messages after this date (ISO format)
        - date_to: Filter messages before this date (ISO format)
        """
        client = self.get_object()
        
        # Base queryset - messages where client is sender OR recipient
        queryset = TestMessage.objects.filter(
            Q(sender=client) | Q(recipient=client)
        ).select_related('sender', 'recipient')
        
        # Filter by delivery status
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(delivery_status=status_filter)
        
        # Filter by date range
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        # Sorting
        sort = request.query_params.get('sort', '-created_at')
        valid_sorts = [
            'created_at', '-created_at',
            'total_latency_ms', '-total_latency_ms',
            'sent_at', '-sent_at',
            'sender__name', '-sender__name',
            'recipient__name', '-recipient__name',
            'delivery_status', '-delivery_status',
        ]
        if sort in valid_sorts:
            queryset = queryset.order_by(sort)
        else:
            queryset = queryset.order_by('-created_at')
        
        # Paginate
        paginator = LatencyHistoryPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = LatencyHistorySerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = LatencyHistorySerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='latency-stats')
    def latency_stats(self, request, id=None):
        """
        Get latency statistics and time series data for graphs.
        
        Query Parameters:
        - range: Time range - 24h, 7d, 30d, all (default: 24h)
        
        Returns:
        - Aggregate stats (avg, min, max)
        - Message counts by status
        - Time series data for graph visualization
        """
        client = self.get_object()
        time_range = request.query_params.get('range', '24h')
        
        # Calculate cutoff time based on range
        now = timezone.now()
        if time_range == '24h':
            cutoff = now - timedelta(hours=24)
        elif time_range == '7d':
            cutoff = now - timedelta(days=7)
        elif time_range == '30d':
            cutoff = now - timedelta(days=30)
        else:  # 'all'
            cutoff = None
        
        # Base queryset
        queryset = TestMessage.objects.filter(
            Q(sender=client) | Q(recipient=client)
        )
        
        if cutoff:
            queryset = queryset.filter(created_at__gte=cutoff)
        
        # Aggregate statistics
        stats = queryset.aggregate(
            avg_latency=Avg('total_latency_ms'),
            min_latency=Min('total_latency_ms'),
            max_latency=Max('total_latency_ms'),
            total_messages=Count('id'),
        )
        
        # Count by delivery status
        status_counts = queryset.values('delivery_status').annotate(count=Count('id'))
        delivered_count = 0
        failed_count = 0
        pending_count = 0
        
        for sc in status_counts:
            if sc['delivery_status'] == 'delivered':
                delivered_count = sc['count']
            elif sc['delivery_status'] == 'failed':
                failed_count = sc['count']
            elif sc['delivery_status'] in ['sending', 'sent']:
                pending_count += sc['count']
        
        # Time series data for graph (only delivered with latency)
        time_series_query = queryset.filter(
            total_latency_ms__isnull=False,
            delivery_status='delivered'
        ).order_by('created_at').values(
            'id', 'created_at', 'total_latency_ms',
            'sender__profile_name', 'recipient__profile_name'
        )
        
        # Limit to 500 points for performance
        time_series = list(time_series_query[:500])
        
        # Format time series for frontend
        formatted_series = []
        for item in time_series:
            formatted_series.append({
                'timestamp': item['created_at'].isoformat(),
                'latency': item['total_latency_ms'],
                'message_id': str(item['id']),
                'sender_profile': item['sender__profile_name'],
                'recipient_profile': item['recipient__profile_name'],
            })
        
        response_data = {
            'avg_latency': round(stats['avg_latency'], 2) if stats['avg_latency'] else 0,
            'min_latency': stats['min_latency'],
            'max_latency': stats['max_latency'],
            'total_messages': stats['total_messages'],
            'delivered_count': delivered_count,
            'failed_count': failed_count,
            'pending_count': pending_count,
            'time_series': formatted_series,
            'time_range': time_range,
        }
        
        return Response(response_data)
    
    @action(detail=True, methods=['get'], url_path='latency-recent')
    def latency_recent(self, request, id=None):
        """
        Get the 15 most recent latency values for the mini graph on the card.
        
        Returns latencies in chronological order (oldest first) for proper
        graph rendering.
        """
        client = self.get_object()
        
        # Get last 15 delivered messages with latency
        messages = TestMessage.objects.filter(
            Q(sender=client) | Q(recipient=client),
            total_latency_ms__isnull=False,
            delivery_status='delivered'
        ).order_by('-created_at')[:15]
        
        # Return in chronological order (oldest first for graph)
        data = []
        for msg in reversed(list(messages)):
            data.append({
                'latency': msg.total_latency_ms,
                'timestamp': msg.created_at.isoformat(),
            })
        
        return Response({
            'data': data,
            'count': len(data),
        })
    
    # =========================================================================
    # RESET ACTIONS
    # =========================================================================
    
    @action(detail=True, methods=['post'], url_path='reset-messages')
    def reset_messages(self, request, id=None):
        """
        Delete all TestMessages for this client and reset counters.
        
        This deletes messages where the client is sender OR recipient,
        and resets all message counters to zero.
        """
        client = self.get_object()
        
        # Count and delete messages
        messages = TestMessage.objects.filter(
            Q(sender=client) | Q(recipient=client)
        )
        count = messages.count()
        messages.delete()
        
        # Reset counters
        client.messages_sent = 0
        client.messages_received = 0
        client.messages_failed = 0
        client.save(update_fields=['messages_sent', 'messages_received', 'messages_failed'])
        
        logger.info(f'Reset messages for {client.name}: deleted {count} messages')
        
        return Response({
            'success': True,
            'message': f'Deleted {count} messages and reset counters.',
            'deleted_count': count,
            'reset_values': {
                'messages_sent': 0,
                'messages_received': 0,
                'messages_failed': 0,
            }
        })
    
    @action(detail=True, methods=['post'], url_path='reset-counters')
    def reset_counters(self, request, id=None):
        """
        Recalculate message counters from the database.
        
        Useful when counters are out of sync with actual messages.
        Does NOT delete any messages.
        """
        client = self.get_object()
        
        # Calculate actual counts from database
        sent_count = TestMessage.objects.filter(sender=client).count()
        received_count = TestMessage.objects.filter(recipient=client).count()
        failed_count = TestMessage.objects.filter(
            sender=client,
            delivery_status='failed'
        ).count()
        
        # Update counters
        client.messages_sent = sent_count
        client.messages_received = received_count
        client.messages_failed = failed_count
        client.save(update_fields=['messages_sent', 'messages_received', 'messages_failed'])
        
        logger.info(
            f'Recalculated counters for {client.name}: '
            f'sent={sent_count}, received={received_count}, failed={failed_count}'
        )
        
        return Response({
            'success': True,
            'message': 'Counters recalculated from database.',
            'reset_values': {
                'messages_sent': sent_count,
                'messages_received': received_count,
                'messages_failed': failed_count,
            }
        })
    
    @action(detail=True, methods=['post'], url_path='reset-latency')
    def reset_latency(self, request, id=None):
        """
        Clear all latency data without deleting messages.
        
        Useful for starting fresh latency measurements while
        keeping message history intact.
        """
        client = self.get_object()
        
        # Clear latency fields
        messages = TestMessage.objects.filter(
            Q(sender=client) | Q(recipient=client)
        )
        count = messages.count()
        
        messages.update(
            total_latency_ms=None,
            latency_to_server_ms=None,
            latency_to_client_ms=None,
        )
        
        logger.info(f'Cleared latency data for {client.name}: {count} messages')
        
        return Response({
            'success': True,
            'message': f'Cleared latency data from {count} messages.',
            'deleted_count': count,
        })
    
    @action(detail=True, methods=['post'], url_path='reset-all')
    def reset_all(self, request, id=None):
        """
        Full reset: Delete all messages and reset all counters.
        
        WARNING: This action cannot be undone!
        """
        client = self.get_object()
        
        # Delete all messages
        messages = TestMessage.objects.filter(
            Q(sender=client) | Q(recipient=client)
        )
        count = messages.count()
        messages.delete()
        
        # Reset all counters
        client.messages_sent = 0
        client.messages_received = 0
        client.messages_failed = 0
        client.save(update_fields=['messages_sent', 'messages_received', 'messages_failed'])
        
        logger.info(f'Full reset for {client.name}: deleted {count} messages')
        
        return Response({
            'success': True,
            'message': f'Full reset complete. Deleted {count} messages.',
            'deleted_count': count,
            'reset_values': {
                'messages_sent': 0,
                'messages_received': 0,
                'messages_failed': 0,
            }
        })


# =============================================================================
# CONNECTION VIEWSET
# =============================================================================

class ClientConnectionViewSet(viewsets.ModelViewSet):
    """ViewSet for client connections"""
    queryset = ClientConnection.objects.all()
    serializer_class = ClientConnectionSerializer
    
    def get_queryset(self):
        queryset = ClientConnection.objects.all()
        client_id = self.request.query_params.get('client')
        if client_id:
            queryset = queryset.filter(
                Q(client_a_id=client_id) | Q(client_b_id=client_id)
            )
        return queryset.select_related('client_a', 'client_b')


# =============================================================================
# STATISTICS VIEW
# =============================================================================

class ClientStatsView(APIView):
    """API View for global client statistics (dashboard overview)"""
    
    def get(self, request):
        stats = {
            'total': SimplexClient.objects.count(),
            'running': SimplexClient.objects.filter(
                status=SimplexClient.Status.RUNNING
            ).count(),
            'stopped': SimplexClient.objects.filter(
                status=SimplexClient.Status.STOPPED
            ).count(),
            'error': SimplexClient.objects.filter(
                status=SimplexClient.Status.ERROR
            ).count(),
            'total_messages_sent': SimplexClient.objects.aggregate(
                total=Sum('messages_sent')
            )['total'] or 0,
            'total_messages_received': SimplexClient.objects.aggregate(
                total=Sum('messages_received')
            )['total'] or 0,
        }
        
        # Available ports
        used_ports = set(SimplexClient.objects.values_list('websocket_port', flat=True))
        stats['available_ports'] = [p for p in range(3031, 3081) if p not in used_ports][:5]
        
        serializer = ClientStatsSerializer(stats)
        return Response(serializer.data)


# =============================================================================
# MESSAGE VIEWSET
# =============================================================================

class TestMessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for test messages.
    
    Supports:
    - List messages with filtering by client and direction
    - Retrieve single message
    - Delete single message (with counter updates)
    """
    queryset = TestMessage.objects.all()
    serializer_class = TestMessageSerializer
    
    def get_queryset(self):
        queryset = TestMessage.objects.all().select_related(
            'sender', 'recipient', 'connection'
        )
        
        # Filter by client (sent or received)
        client_id = self.request.query_params.get('client')
        if client_id:
            queryset = queryset.filter(
                Q(sender_id=client_id) | Q(recipient_id=client_id)
            )
        
        # Filter by direction
        direction = self.request.query_params.get('direction')
        if direction == 'sent' and client_id:
            queryset = queryset.filter(sender_id=client_id)
        elif direction == 'received' and client_id:
            queryset = queryset.filter(recipient_id=client_id)
        
        # Filter by delivery status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(delivery_status=status_filter)
        
        return queryset.order_by('-created_at')[:50]
    
    def get_serializer_context(self):
        """Pass request to serializer for direction detection"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a single message and update client counters.
        """
        instance = self.get_object()
        message_id = str(instance.id)
        
        # Update sender counters
        if instance.sender:
            instance.sender.messages_sent = max(0, instance.sender.messages_sent - 1)
            if instance.delivery_status == 'failed':
                instance.sender.messages_failed = max(0, instance.sender.messages_failed - 1)
            instance.sender.save(update_fields=['messages_sent', 'messages_failed'])
        
        # Update recipient counters
        if instance.recipient:
            instance.recipient.messages_received = max(0, instance.recipient.messages_received - 1)
            instance.recipient.save(update_fields=['messages_received'])
        
        self.perform_destroy(instance)
        
        logger.info(f'Deleted message {message_id}')
        
        return Response({
            'success': True,
            'message': f'Message deleted.',
            'deleted_id': message_id,
        }, status=status.HTTP_200_OK)


# =============================================================================
# TEST RUN VIEWSET
# =============================================================================

class TestRunViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing stress test runs.
    
    Endpoints:
    - GET    /api/v1/test-runs/           - List all test runs
    - POST   /api/v1/test-runs/           - Create new test run
    - GET    /api/v1/test-runs/{id}/      - Get test run details
    - POST   /api/v1/test-runs/{id}/start/  - Start test execution
    - POST   /api/v1/test-runs/{id}/cancel/ - Cancel running test
    - GET    /api/v1/test-runs/{id}/messages/ - Get test messages
    - GET    /api/v1/test-runs/{id}/results/  - Get detailed results
    """
    queryset = TestRun.objects.all()
    
    def get_serializer_class(self):
        from .serializers import TestRunSerializer, TestRunCreateSerializer
        if self.action == 'create':
            return TestRunCreateSerializer
        return TestRunSerializer
    
    def get_queryset(self):
        queryset = TestRun.objects.all().select_related('sender')
        
        # Filter by sender
        sender_id = self.request.query_params.get('sender')
        if sender_id:
            queryset = queryset.filter(sender_id=sender_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')
    
    def create(self, request, *args, **kwargs):
        """Create and start a new test run"""
        from .serializers import TestRunCreateSerializer, TestRunSerializer
        from clients.services.test_runner import TestRunner
        
        serializer = TestRunCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create the test run
        test_run = TestRun.objects.create(
            name=serializer.validated_data['name'],
            sender=serializer.validated_data['sender'],
            message_count=serializer.validated_data.get('message_count', 10),
            interval_ms=serializer.validated_data.get('interval_ms', 1000),
            message_size=serializer.validated_data.get('message_size', 50),
            recipient_mode=serializer.validated_data.get('recipient_mode', 'round_robin'),
        )
        
        # Set selected recipients if provided
        selected = serializer.validated_data.get('selected_recipients', [])
        if selected:
            test_run.selected_recipients.set(selected)
        
        logger.info(f'Created test run: {test_run.name} ({test_run.id})')
        
        # Check sender is running before starting
        if test_run.sender.status != 'running':
            return Response({
                'error': f'Sender client is not running (status: {test_run.sender.status})',
                'test_run': TestRunSerializer(test_run).data
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Auto-start the test runner
        try:
            runner = TestRunner(test_run)
            runner.start_async()
            logger.info(f'Auto-started test run: {test_run.name}')
        except Exception as e:
            logger.exception(f'Failed to start test runner: {e}')
            test_run.status = 'failed'
            test_run.save()
            return Response({
                'error': f'Failed to start test: {str(e)}',
                'test_run': TestRunSerializer(test_run).data
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Refresh and return
        test_run.refresh_from_db()
        response_serializer = TestRunSerializer(test_run)
        return Response({
            'success': True,
            'message': 'Test created and started',
            'test_run': response_serializer.data
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start test execution"""
        from clients.services.test_runner import TestRunner
        
        test_run = self.get_object()
        
        # Check if already running
        if test_run.status == 'running':
            return Response({
                'error': 'Test is already running'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if already completed
        if test_run.status in ['completed', 'cancelled', 'failed']:
            return Response({
                'error': f'Test has already {test_run.status}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check sender is running
        if test_run.sender.status != 'running':
            return Response({
                'error': f'Sender client is not running (status: {test_run.sender.status})'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Start the test runner
        runner = TestRunner(test_run)
        runner.start_async()
        
        logger.info(f'Started test run: {test_run.name}')
        
        # Refresh and return
        test_run.refresh_from_db()
        from .serializers import TestRunSerializer
        serializer = TestRunSerializer(test_run)
        
        return Response({
            'success': True,
            'message': 'Test started',
            'test_run': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel running test"""
        from clients.services.test_runner import TestRunner
        
        test_run = self.get_object()
        
        if test_run.status != 'running':
            return Response({
                'error': 'Test is not running'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Request cancellation
        TestRunner.cancel(str(test_run.id))
        
        # Update status
        test_run.status = 'cancelled'
        test_run.completed_at = timezone.now()
        test_run.save()
        
        logger.info(f'Test run {test_run.id} cancelled')
        
        return Response({
            'success': True,
            'message': 'Test cancelled'
        })
    
    @action(detail=True, methods=['get'])
    def messages(self, request, pk=None):
        """Get messages for this test run"""
        from .serializers import TestRunMessageSerializer
        
        test_run = self.get_object()
        test_id_prefix = f"test_{test_run.id.hex[:8]}"
        
        messages = TestMessage.objects.filter(
            tracking_id__startswith=test_id_prefix
        ).select_related('sender', 'recipient').order_by('sent_at')
        
        serializer = TestRunMessageSerializer(messages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def results(self, request, pk=None):
        """Get detailed test results"""
        test_run = self.get_object()
        test_id_prefix = f"test_{test_run.id.hex[:8]}"
        
        messages = TestMessage.objects.filter(
            tracking_id__startswith=test_id_prefix
        )
        
        # Aggregate stats
        stats = messages.filter(
            delivery_status='delivered',
            total_latency_ms__isnull=False
        ).aggregate(
            avg_total=Avg('total_latency_ms'),
            min_total=Min('total_latency_ms'),
            max_total=Max('total_latency_ms'),
            avg_to_server=Avg('latency_to_server_ms'),
            avg_to_client=Avg('latency_to_client_ms'),
        )
        
        # Count by status
        status_counts = {}
        for s in ['sending', 'sent', 'delivered', 'failed']:
            status_counts[s] = messages.filter(delivery_status=s).count()
        
        # Time series for graph
        time_series = []
        for msg in messages.filter(total_latency_ms__isnull=False).order_by('sent_at')[:100]:
            time_series.append({
                'timestamp': msg.sent_at.isoformat() if msg.sent_at else None,
                'total_latency': msg.total_latency_ms,
                'to_server': msg.latency_to_server_ms,
                'to_client': msg.latency_to_client_ms,
                'recipient': msg.recipient.name if msg.recipient else 'Unknown',
                'status': msg.delivery_status,
            })
        
        return Response({
            'test_run_id': str(test_run.id),
            'name': test_run.name,
            'status': test_run.status,
            'summary': {
                'total_messages': test_run.message_count,
                'sent': test_run.messages_sent,
                'delivered': test_run.messages_delivered,
                'failed': test_run.messages_failed,
                'success_rate': test_run.success_rate,
            },
            'latency': {
                'avg_total_ms': stats['avg_total'],
                'min_total_ms': stats['min_total'],
                'max_total_ms': stats['max_total'],
                'avg_to_server_ms': stats['avg_to_server'],
                'avg_to_client_ms': stats['avg_to_client'],
            },
            'status_counts': status_counts,
            'time_series': time_series,
            'duration_seconds': test_run.duration_seconds,
            'started_at': test_run.started_at.isoformat() if test_run.started_at else None,
            'completed_at': test_run.completed_at.isoformat() if test_run.completed_at else None,
        })