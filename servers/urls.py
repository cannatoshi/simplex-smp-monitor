from django.urls import path
from . import views

app_name = 'servers'

urlpatterns = [
    path('', views.server_list, name='list'),
    path('create/', views.server_create, name='create'),
    path('<int:pk>/', views.server_detail, name='detail'),
    path('<int:pk>/edit/', views.server_edit, name='edit'),
    path('<int:pk>/toggle/', views.server_toggle, name='toggle'),
    path('<int:pk>/delete/', views.server_delete, name='delete'),
    path('<int:pk>/test/', views.test_server, name='test_server'),
    path('reorder/', views.server_reorder, name='reorder'),
    path('test/', views.test_connection, name='test_connection'),
    path('check-duplicate/', views.check_duplicate, name='check_duplicate'),
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/<int:pk>/', views.category_detail, name='category_detail'),
    path('categories/<int:pk>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
]
