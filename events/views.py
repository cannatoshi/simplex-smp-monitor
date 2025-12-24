from django.shortcuts import render
from .models import EventLog

def event_list(request):
    level_filter = request.GET.get('level')
    source_filter = request.GET.get('source')
    
    events = EventLog.objects.all()
    
    if level_filter:
        events = events.filter(level=level_filter)
    if source_filter:
        events = events.filter(source__icontains=source_filter)
    
    events = events[:100]
    
    if request.htmx:
        return render(request, 'events/_event_list.html', {'events': events})
    
    return render(request, 'events/list.html', {
        'events': events,
        'levels': ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    })
