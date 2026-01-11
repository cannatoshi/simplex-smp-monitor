"""
Django Forms für SimpleX CLI Clients
"""

from django import forms
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from .models import SimplexClient, ClientConnection, TestMessage


class SimplexClientForm(forms.ModelForm):
    """
    Formular zum Erstellen/Bearbeiten eines SimpleX Clients.
    """
    
    class Meta:
        model = SimplexClient
        fields = ['websocket_port', 'connection_mode', 'chutnex_network', 'chutnex_socks_port', 'smp_servers', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500',
                'placeholder': 'z.B. Test Client 1'
            }),
            'slug': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500',
                'placeholder': 'z.B. client-001'
            }),
            'profile_name': forms.TextInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500',
                'placeholder': 'Optional - wird für SimpleX Profil verwendet'
            }),
            'websocket_port': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500',
                'min': 3031,
                'max': 3080,
                'placeholder': '3031-3080'
            }),
            'connection_mode': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500'
            }),
            'chutnex_network': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500'
            }),
            'chutnex_socks_port': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500'
            }),
            'smp_servers': forms.CheckboxSelectMultiple(attrs={
                'class': 'space-y-2'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Port-Dropdown nur mit freien Ports
        used_ports = set(SimplexClient.objects.values_list('websocket_port', flat=True))
        if self.instance.pk and self.instance.websocket_port:
            used_ports.discard(self.instance.websocket_port)
        
        free_ports = [(p, str(p)) for p in range(3031, 3081) if p not in used_ports]
        self.fields['websocket_port'].choices = free_ports
        
        if free_ports:
            self.fields['websocket_port'].initial = free_ports[0][0]
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug:
            slug = slugify(slug)
        return slug
    
    def clean_websocket_port(self):
        port = self.cleaned_data.get('websocket_port')
        if port:
            # Prüfe ob Port bereits verwendet wird
            existing = SimplexClient.objects.filter(websocket_port=port)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError(f'Port {port} wird bereits verwendet.')
        return port


class ClientConnectionForm(forms.ModelForm):
    """
    Formular zum Erstellen einer Verbindung zwischen zwei Clients.
    """
    
    class Meta:
        model = ClientConnection
        fields = ['client_a', 'client_b']
        widgets = {
            'client_a': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500'
            }),
            'client_b': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Nur laufende Clients anzeigen
        running_clients = SimplexClient.objects.filter(status=SimplexClient.Status.RUNNING)
        self.fields['client_a'].queryset = running_clients
        self.fields['client_b'].queryset = running_clients
    
    def clean(self):
        cleaned_data = super().clean()
        client_a = cleaned_data.get('client_a')
        client_b = cleaned_data.get('client_b')
        
        if client_a and client_b:
            if client_a == client_b:
                raise ValidationError('Ein Client kann nicht mit sich selbst verbunden werden.')
            
            # Prüfe ob Verbindung bereits existiert (in beide Richtungen)
            existing = ClientConnection.objects.filter(
                models.Q(client_a=client_a, client_b=client_b) |
                models.Q(client_a=client_b, client_b=client_a)
            )
            if existing.exists():
                raise ValidationError('Diese Verbindung existiert bereits.')
        
        return cleaned_data


class TestMessageForm(forms.Form):
    """
    Formular zum Senden einer Test-Nachricht.
    """
    
    sender = forms.ModelChoiceField(
        queryset=SimplexClient.objects.none(),
        label='Sender',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500'
        })
    )
    
    recipient = forms.ModelChoiceField(
        queryset=SimplexClient.objects.none(),
        label='Empfänger',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500'
        })
    )
    
    content = forms.CharField(
        label='Nachricht',
        max_length=1000,
        widget=forms.Textarea(attrs={
            'class': 'w-full px-3 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white focus:outline-none focus:ring-2 focus:ring-cyan-500',
            'rows': 3,
            'placeholder': 'Nachrichteninhalt...'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        running_clients = SimplexClient.objects.filter(status=SimplexClient.Status.RUNNING)
        self.fields['sender'].queryset = running_clients
        self.fields['recipient'].queryset = running_clients
    
    def clean(self):
        cleaned_data = super().clean()
        sender = cleaned_data.get('sender')
        recipient = cleaned_data.get('recipient')
        
        if sender and recipient:
            if sender == recipient:
                raise ValidationError('Sender und Empfänger müssen unterschiedlich sein.')
            
            # Prüfe ob Verbindung existiert
            connection_exists = ClientConnection.objects.filter(
                models.Q(client_a=sender, client_b=recipient) |
                models.Q(client_a=recipient, client_b=sender),
                status=ClientConnection.Status.CONNECTED
            ).exists()
            
            if not connection_exists:
                raise ValidationError('Keine aktive Verbindung zwischen diesen Clients.')
        
        return cleaned_data


class BatchTestForm(forms.Form):
    """
    Formular für Batch-Tests (mehrere Nachrichten senden).
    """
    
    sender = forms.ModelChoiceField(
        queryset=SimplexClient.objects.none(),
        label='Sender',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white'
        })
    )
    
    recipient = forms.ModelChoiceField(
        queryset=SimplexClient.objects.none(),
        label='Empfänger',
        widget=forms.Select(attrs={
            'class': 'w-full px-3 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white'
        })
    )
    
    message_count = forms.IntegerField(
        label='Anzahl Nachrichten',
        min_value=1,
        max_value=100,
        initial=10,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white'
        })
    )
    
    interval_ms = forms.IntegerField(
        label='Interval (ms)',
        min_value=100,
        max_value=10000,
        initial=1000,
        widget=forms.NumberInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white'
        })
    )
    
    message_template = forms.CharField(
        label='Nachrichtenvorlage',
        initial='Test message #{n}',
        help_text='Verwende {n} für Nachrichtennummer',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-600 rounded-lg bg-gray-700 text-white'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        running_clients = SimplexClient.objects.filter(status=SimplexClient.Status.RUNNING)
        self.fields['sender'].queryset = running_clients
        self.fields['recipient'].queryset = running_clients


# Import für ValidationError in clean Methoden
from django.db import models
