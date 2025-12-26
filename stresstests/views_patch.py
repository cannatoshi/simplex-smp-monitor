# Füge diesen Code zur test_detail View hinzu (nach server_stats):

from django.db.models import Avg
from django.utils import timezone
from datetime import timedelta

# In test_detail view, nach server_stats berechnen:

# Durchschnittliche Latenz
avg_latency = TestResult.objects.filter(
    test=test,
    success=True,
    latency_ms__isnull=False
).aggregate(avg=Avg('latency_ms'))['avg']

# Latenz-History für Sparkline (letzte 12 Datenpunkte)
latency_history = []
results = TestResult.objects.filter(
    test=test,
    success=True,
    latency_ms__isnull=False
).order_by('-timestamp')[:12]

if results:
    latencies = [r.latency_ms for r in reversed(results)]
    max_lat = max(latencies) if latencies else 1
    for lat in latencies:
        height = max(10, int((lat / max_lat) * 100))
        latency_history.append({'value': lat, 'height': height})

# Zum context hinzufügen:
# 'avg_latency': avg_latency,
# 'latency_history': latency_history,
