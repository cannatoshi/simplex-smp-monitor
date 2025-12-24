from django.urls import path
from . import views

app_name = 'servers'

urlpatterns = [
    path('', views.server_list, name='list'),
    path('create/', views.server_create, name='create'),
    path('reorder/', views.server_reorder, name='reorder'),
    path('test/', views.test_connection, name='test_connection'),
    path('check-duplicate/', views.check_duplicate, name='check_duplicate'),
    path('<int:pk>/', views.server_detail, name='detail'),
    path('<int:pk>/edit/', views.server_edit, name='edit'),
    path('<int:pk>/toggle/', views.server_toggle, name='toggle'),
    path('<int:pk>/delete/', views.server_delete, name='delete'),
]
