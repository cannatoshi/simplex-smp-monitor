"""
URL patterns für SimpleX CLI Clients

WICHTIG: Die Reihenfolge ist kritisch!
- Spezifische Pfade (messages/, connections/) MÜSSEN vor <slug:slug>/ stehen
- Sonst wird z.B. "messages" als Slug interpretiert → 404
"""

from django.urls import path
from . import views

app_name = 'clients'

urlpatterns = [
    # === Liste und Erstellen (kein Konflikt) ===
    path('', views.ClientListView.as_view(), name='list'),
    path('create/', views.ClientCreateView.as_view(), name='create'),
    
    # === Messages (VOR slug-routes!) ===
    path('messages/send/', views.SendMessageView.as_view(), name='send_message'),
    path('messages/<uuid:pk>/status/', views.MessageStatusView.as_view(), name='message_status'),
    
    # === Connections (VOR slug-routes!) ===
    path('connections/create/', views.ConnectionCreateView.as_view(), name='connection_create'),
    path('connections/<uuid:pk>/delete/', views.ConnectionDeleteView.as_view(), name='connection_delete'),
    
    # === Bulk Actions (VOR slug-routes!) ===
    path('bulk/start/', views.BulkStartView.as_view(), name='bulk_start'),
    path('bulk/stop/', views.BulkStopView.as_view(), name='bulk_stop'),
    
    # === Test Panel (VOR slug-routes!) ===
    path('test-panel/', views.TestPanelView.as_view(), name='test_panel'),
    
    # === Client Detail und Aktionen (slug-basiert - AM ENDE!) ===
    path('<slug:slug>/', views.ClientDetailView.as_view(), name='detail'),
    path('<slug:slug>/edit/', views.ClientUpdateView.as_view(), name='edit'),
    path('<slug:slug>/delete/', views.ClientDeleteView.as_view(), name='delete'),
    path('<slug:slug>/start/', views.ClientStartView.as_view(), name='start'),
    path('<slug:slug>/stop/', views.ClientStopView.as_view(), name='stop'),
    path('<slug:slug>/restart/', views.ClientRestartView.as_view(), name='restart'),
    path('<slug:slug>/logs/', views.ClientLogsView.as_view(), name='logs'),
    path('<slug:slug>/connect/', views.ClientConnectView.as_view(), name='connect'),
    path('<slug:slug>/quick-message/', views.QuickMessageView.as_view(), name='quick_message'),
    path('<slug:slug>/contacts/', views.ClientContactsAPIView.as_view(), name='contacts_api'),
]