"""
URL Routing für SimpleX CLI Clients
"""
from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    # === CRUD ===
    path('', views.ClientListView.as_view(), name='list'),
    path('create/', views.ClientCreateView.as_view(), name='create'),
    path('<slug:slug>/', views.ClientDetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', views.ClientUpdateView.as_view(), name='edit'),
    path('<slug:slug>/delete/', views.ClientDeleteView.as_view(), name='delete'),
    
    # === Client Actions ===
    path('<slug:slug>/start/', views.ClientStartView.as_view(), name='start'),
    path('<slug:slug>/stop/', views.ClientStopView.as_view(), name='stop'),
    path('<slug:slug>/restart/', views.ClientRestartView.as_view(), name='restart'),
    path('<slug:slug>/logs/', views.ClientLogsView.as_view(), name='logs'),
    
    # === SimpleX Connect & Message ===
    path('<slug:slug>/connect/', views.ClientConnectView.as_view(), name='connect'),
    path('<slug:slug>/send/', views.QuickMessageView.as_view(), name='quick_send'),
    path('<slug:slug>/contacts/', views.ClientContactsAPIView.as_view(), name='contacts_api'),
    
    # === Connections ===
    path('connections/create/', views.ConnectionCreateView.as_view(), name='connection_create'),
    path('connections/<uuid:pk>/delete/', views.ConnectionDeleteView.as_view(), name='connection_delete'),
    
    # === Messages ===
    path('messages/send/', views.SendMessageView.as_view(), name='send_message'),
    path('messages/<uuid:pk>/status/', views.MessageStatusView.as_view(), name='message_status'),
    
    # === Test Panel ===
    path('test-panel/', views.TestPanelView.as_view(), name='test_panel'),
    
    # === Bulk Actions ===
    path('bulk/start/', views.BulkStartView.as_view(), name='bulk_start'),
    path('bulk/stop/', views.BulkStopView.as_view(), name='bulk_stop'),
]
