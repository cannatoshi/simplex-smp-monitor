"""
Dashboard API - URL Configuration
"""
from django.urls import path

from .views import (
    DashboardStatsView,
    ServerActivityView,
    LatencyOverviewView,
    RecentServersView,
    RecentTestsView,
    RecentEventsView,
)

urlpatterns = [
    path('stats/', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('activity/', ServerActivityView.as_view(), name='dashboard-activity'),
    path('latency/', LatencyOverviewView.as_view(), name='dashboard-latency'),
    path('servers/', RecentServersView.as_view(), name='dashboard-servers'),
    path('tests/', RecentTestsView.as_view(), name='dashboard-tests'),
    path('events/', RecentEventsView.as_view(), name='dashboard-events'),
]
