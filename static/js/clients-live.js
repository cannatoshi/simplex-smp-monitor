/**
 * SimpleX SMP Monitor - Live WebSocket Updates
 * v0.1.8-security
 */

class ClientsWebSocket {
    constructor(options = {}) {
        this.url = options.url || this._buildUrl();
        this.reconnectDelay = options.reconnectDelay || 3000;
        this.ws = null;
        this.handlers = {};
        this.connected = false;
        this.connectedAt = null;
        this.lastEventAt = null;
        this.eventCount = 0;
        this.clientCount = 0;
        
        this.connect();
        this._startUptimeTimer();
    }

    // SECURITY: HTML escape to prevent XSS
    _escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    _buildUrl() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const path = window.clientSlug 
            ? `/ws/clients/${window.clientSlug}/`
            : '/ws/clients/';
        return `${protocol}//${window.location.host}${path}`;
    }
    
    connect() {
        console.log(`🔌 Connecting to ${this.url}...`);
        
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
            console.log('✅ WebSocket connected');
            this.connected = true;
            this.connectedAt = new Date();
            this._updateStatus('connected');
            
            // Request initial state
            this.send({ action: 'get_status' });
        };
        
        this.ws.onclose = (e) => {
            console.log('❌ WebSocket closed:', e.code);
            this.connected = false;
            this.connectedAt = null;
            this._updateStatus('disconnected');
            
            // Auto-reconnect
            setTimeout(() => this.connect(), this.reconnectDelay);
        };
        
        this.ws.onerror = (e) => {
            console.error('WebSocket error:', e);
        };
        
        this.ws.onmessage = (e) => {
            try {
                const data = JSON.parse(e.data);
                this._handleMessage(data);
            } catch (err) {
                console.error('Parse error:', err);
            }
        };
    }
    
    _handleMessage(data) {
        const type = data.type;
        console.log('📨 Received:', type, data);
        
        // Track events
        this.lastEventAt = new Date();
        this.eventCount++;
        this._updateLastEvent(type);
        
        // Call registered handlers
        if (this.handlers[type]) {
            this.handlers[type].forEach(handler => handler(data));
        }
        
        // Built-in handlers
        switch (type) {
            case 'client_status':
                this._updateClientStatus(data);
                break;
            case 'client_stats':
                this._updateClientStats(data);
                break;
            case 'message_status':
                this._updateMessageStatus(data);
                break;
            case 'new_message':
                this._handleNewMessage(data);
                break;
            case 'bridge_status':
                this._updateBridgeStatus(data);
                break;
        }
        
        // Call detail page handler if exists
        if (typeof window.handleDetailPageEvent === 'function') {
            window.handleDetailPageEvent(data);
        }
    }
    
    on(type, handler) {
        if (!this.handlers[type]) {
            this.handlers[type] = [];
        }
        this.handlers[type].push(handler);
    }
    
    send(data) {
        if (this.connected) {
            this.ws.send(JSON.stringify(data));
        }
    }
    
    // === Status UI Updates ===
    
    _updateStatus(status) {
        const indicator = document.getElementById('ws-status');
        const statusText = document.getElementById('ws-status-text');
        const tooltipConnection = document.getElementById('ws-tooltip-connection');
        
        if (status === 'connected') {
            if (indicator) {
                indicator.className = 'w-2 h-2 rounded-full bg-green-500';
            }
            if (statusText) {
                statusText.textContent = 'Live';
                statusText.className = 'text-xs text-green-600 dark:text-green-400 font-medium';
            }
            if (tooltipConnection) {
                tooltipConnection.textContent = 'Connected';
                tooltipConnection.className = 'font-medium text-green-500';
            }
        } else {
            if (indicator) {
                indicator.className = 'w-2 h-2 rounded-full bg-red-500 animate-pulse';
            }
            if (statusText) {
                statusText.textContent = 'Reconnecting...';
                statusText.className = 'text-xs text-red-500 dark:text-red-400';
            }
            if (tooltipConnection) {
                tooltipConnection.textContent = 'Disconnected';
                tooltipConnection.className = 'font-medium text-red-500';
            }
        }
    }
    
    _updateLastEvent(type) {
        const el = document.getElementById('ws-tooltip-last-event');
        if (el) {
            const typeMap = {
                'client_status': '🔄 Status Update',
                'client_stats': '📊 Stats Update',
                'message_status': '✉️ Message Status',
                'new_message': '📨 New Message',
                'bridge_status': '🌉 Bridge Status',
                'pong': '🏓 Ping/Pong',
            };
            el.textContent = typeMap[type] || type;
        }
    }
    
    _updateBridgeStatus(data) {
        const clientsEl = document.getElementById('ws-tooltip-clients');
        if (clientsEl && data.connected_clients !== undefined) {
            this.clientCount = data.connected_clients;
            clientsEl.textContent = `${data.connected_clients} Clients`;
        }
    }
    
    _startUptimeTimer() {
        setInterval(() => {
            const el = document.getElementById('ws-tooltip-uptime');
            if (el && this.connectedAt) {
                const seconds = Math.floor((new Date() - this.connectedAt) / 1000);
                el.textContent = this._formatUptime(seconds);
            }
        }, 1000);
    }
    
    _formatUptime(seconds) {
        if (seconds < 60) return `${seconds}s`;
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
        const hours = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        return `${hours}h ${mins}m`;
    }
    
    // === Client UI Updates ===
    
    _updateClientStatus(data) {
        const card = document.querySelector(`[data-client-slug="${data.client_slug}"]`);
        if (!card) return;
        
        const badge = card.querySelector('.status-badge');
        if (badge) {
            badge.className = `status-badge ${this._statusClass(data.status)}`;
            badge.textContent = data.status;
        }
    }
    
    _updateClientStats(data) {
        // Update auf Client Liste
        const card = document.querySelector(`[data-client-slug="${data.client_slug}"]`);
        if (card) {
            const sent = card.querySelector('.stat-sent');
            const recv = card.querySelector('.stat-received');
            if (sent) sent.textContent = data.messages_sent;
            if (recv) recv.textContent = data.messages_received;
        }
        
        // Update auf Detail Page (beide ID-Varianten checken)
        const statSent = document.getElementById('stat-sent') || document.getElementById('stat-messages-sent');
        const statRecv = document.getElementById('stat-received') || document.getElementById('stat-messages-received');
        if (statSent) statSent.textContent = data.messages_sent;
        if (statRecv) statRecv.textContent = data.messages_received;
    }
    
    _updateMessageStatus(data) {
        // Suche nach allen Rows mit dieser Message ID
        const rows = document.querySelectorAll(`[data-message-id="${data.message_id}"]`);
        
        rows.forEach(row => {
            // Versuche beide Klassen-Varianten
            const statusCell = row.querySelector('.msg-status') || row.querySelector('.message-status');
            const latencyCell = row.querySelector('.msg-latency') || row.querySelector('.message-latency');
            
            if (statusCell) {
                // SECURITY: _statusIcon returns safe predefined HTML only
                statusCell.innerHTML = this._statusIcon(data.status);
            }
            
            if (latencyCell && data.latency_ms) {
                latencyCell.textContent = `${data.latency_ms}ms`;
            }
            
            // Flash animation
            row.classList.add('bg-green-500/20');
            setTimeout(() => row.classList.remove('bg-green-500/20'), 1000);
        });
    }
    
    _handleNewMessage(data) {
        // SECURITY: Escape user content before displaying
        const safeSender = this._escapeHtml(data.sender || 'Unknown');
        const safeContent = this._escapeHtml(data.content || '');
        this._showToast(`📨 ${safeSender}: ${safeContent}`);
        
        // Optional: Tabelle aktualisieren via HTMX
        const messagesTable = document.getElementById('messages-table');
        if (messagesTable && window.htmx) {
            htmx.trigger(messagesTable, 'refresh');
        }
    }
    
    _statusClass(status) {
        const classes = {
            'running': 'bg-green-500 text-white',
            'stopped': 'bg-gray-500 text-white',
            'error': 'bg-red-500 text-white',
            'created': 'bg-yellow-500 text-black',
        };
        return classes[status] || 'bg-gray-500 text-white';
    }
    
    _statusIcon(status) {
        // SECURITY: Only predefined safe HTML, no user input
        const icons = {
            'pending': '<span class="text-gray-400 animate-pulse">⏳</span>',
            'sending': '<span class="text-gray-400 animate-pulse">⏳</span>',
            'sent': '<span class="text-yellow-400" title="Server empfangen">✓</span>',
            'delivered': '<span class="text-green-400 font-bold" title="Zugestellt">✓✓</span>',
            'failed': '<span class="text-red-400" title="Fehlgeschlagen">✗</span>',
        };
        return icons[status] || this._escapeHtml(status);
    }
    
    _showToast(message) {
        const toast = document.createElement('div');
        toast.className = 'fixed bottom-4 right-4 bg-slate-800 text-white px-4 py-3 rounded-lg shadow-lg z-50 animate-fade-in max-w-sm';
        
        // SECURITY: Build DOM safely without innerHTML for user content
        const wrapper = document.createElement('div');
        wrapper.className = 'flex items-start gap-3';
        
        const icon = document.createElement('span');
        icon.className = 'text-lg';
        icon.textContent = '📨';
        
        const content = document.createElement('div');
        content.className = 'flex-1 text-sm';
        content.textContent = message;
        
        wrapper.appendChild(icon);
        wrapper.appendChild(content);
        toast.appendChild(wrapper);
        
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transition = 'opacity 0.3s';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }
}

// Auto-init wenn DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.clientsWS = new ClientsWebSocket();
});