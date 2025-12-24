from django.urls import path
from . import views

app_name = 'stresstests'

urlpatterns = [
    path('', views.test_list, name='list'),
    path('create/', views.test_create, name='create'),
    path('<int:pk>/', views.test_detail, name='detail'),
    path('<int:pk>/start/', views.test_start, name='start'),
    path('<int:pk>/stop/', views.test_stop, name='stop'),
    path('<int:pk>/metrics/', views.test_metrics_api, name='metrics_api'),
]
