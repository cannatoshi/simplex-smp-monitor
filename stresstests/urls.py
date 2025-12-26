from django.urls import path
from . import views

app_name = 'stresstests'

urlpatterns = [
    # Liste & Auswahl
    path('', views.test_list, name='list'),
    path('new/', views.test_type_select, name='type_select'),
    
    # Erstellen (je nach Typ)
    path('create/<str:test_type>/', views.test_create, name='create'),
    
    # Detail, Edit, Delete
    path('<int:pk>/', views.test_detail, name='detail'),
    path('<int:pk>/edit/', views.test_edit, name='edit'),
    path('<int:pk>/delete/', views.test_delete, name='delete'),
    
    # Aktionen
    path('<int:pk>/toggle/', views.test_toggle, name='toggle'),
    path('<int:pk>/run/', views.test_run_now, name='run_now'),
    
    # API
    path('<int:pk>/metrics/', views.test_metrics_api, name='metrics_api'),
    
    # Legacy
    path('<int:pk>/start/', views.test_start, name='start'),
    path('<int:pk>/stop/', views.test_stop, name='stop'),
]
