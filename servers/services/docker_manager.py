"""
Docker Manager für SimpleX Server (SMP/XFTP/NTF)

Verwaltet Docker Container für lokal gehostete SimpleX Server:
- Container erstellen/starten/stoppen/löschen
- Volume Management für persistente Daten
- Logs abrufen
- Fingerprint/Address extraction nach Initialisierung

Hosting Modes:
- IP Mode: Server mit IP-Adresse (für LAN)
- Tor Mode: Server als Tor Hidden Service (.onion)

Voraussetzungen:
- Docker installiert und läuft
- docker-py installiert: pip install docker
- Server Images gebaut: simplex-smp:latest, simplex-xftp:latest, simplex-ntf:latest
- Für Tor-Mode: Images mit eingebautem Tor-Daemon
"""

import docker
import logging
import re
import time
import socket
from typing import Optional, List, Dict, Any
from django.conf import settings

logger = logging.getLogger(__name__)


class ServerDockerManager:
    """
    Verwaltet Docker Container für SimpleX Server.
    
    Unterstützte Server-Typen:
    - SMP (simplex-smp:latest) - Port 5223
    - XFTP (simplex-xftp:latest) - Port 443
    - NTF (simplex-ntf:latest) - Port 443
    
    Hosting Modes:
    - IP: Server bindet an IP-Adresse (LAN erreichbar)
    - Tor: Server läuft als Hidden Service (.onion)
    """
    
    # Docker Images
    IMAGES = {
        'smp': getattr(settings, 'SIMPLEX_SMP_IMAGE', 'simplex-smp:latest'),
        'xftp': getattr(settings, 'SIMPLEX_XFTP_IMAGE', 'simplex-xftp:latest'),
        'ntf': getattr(settings, 'SIMPLEX_NTF_IMAGE', 'simplex-ntf:latest'),
    }
    
    # Tor-enabled Images (mit eingebautem Tor daemon)
    TOR_IMAGES = {
        'smp': getattr(settings, 'SIMPLEX_SMP_TOR_IMAGE', 'simplex-smp-tor:latest'),
        'xftp': getattr(settings, 'SIMPLEX_XFTP_TOR_IMAGE', 'simplex-xftp-tor:latest'),
        'ntf': getattr(settings, 'SIMPLEX_NTF_TOR_IMAGE', 'simplex-ntf-tor:latest'),
    }
    
    # Internal ports (inside container)
    INTERNAL_PORTS = {
        'smp': 5223,
        'xftp': 443,
        'ntf': 443,
    }
    
    # Volume mount paths (inside container)
    VOLUME_PATHS = {
        'smp': {
            'data': '/var/opt/simplex',
            'config': '/etc/opt/simplex',
        },
        'xftp': {
            'data': '/var/opt/simplex-xftp',
            'config': '/etc/opt/simplex-xftp',
        },
        'ntf': {
            'data': '/var/opt/simplex-notifications',
            'config': '/etc/opt/simplex-notifications',
        },
    }
    
    # Tor hidden service paths (inside container)
    TOR_PATHS = {
        'smp': '/var/lib/tor/simplex-smp',
        'xftp': '/var/lib/tor/simplex-xftp',
        'ntf': '/var/lib/tor/simplex-ntf',
    }
    
    # Docker Netzwerk
    NETWORK_NAME = getattr(settings, 'SIMPLEX_SERVER_NETWORK', 'simplex-servers')
    
    # Container Labels für Identifikation
    LABEL_PREFIX = 'simplex.server'
    
    def __init__(self):
        """Initialisiert Docker Client"""
        try:
            self.client = docker.from_env()
            self._ensure_network_exists()
            logger.info("ServerDockerManager initialisiert")
        except docker.errors.DockerException as e:
            logger.error(f"Docker nicht verfügbar: {e}")
            raise
    
    def _ensure_network_exists(self):
        """Erstellt das Docker Netzwerk falls nicht vorhanden"""
        try:
            self.client.networks.get(self.NETWORK_NAME)
        except docker.errors.NotFound:
            logger.info(f"Erstelle Docker Netzwerk: {self.NETWORK_NAME}")
            self.client.networks.create(
                self.NETWORK_NAME,
                driver='bridge',
                labels={f'{self.LABEL_PREFIX}.managed': 'true'}
            )
    
    def _get_host_ip(self) -> str:
        """Ermittelt die lokale IP-Adresse des Hosts"""
        try:
            # Trick: Connect to external address to find local IP
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
    
    def create_server_container(self, server) -> str:
        """
        Erstellt einen neuen Docker Container für einen Server.
        
        Unterstützt zwei Modi:
        - IP Mode: Server mit --ip Parameter für LAN-Zugriff
        - Tor Mode: Server mit Tor Hidden Service
        
        Args:
            server: Server Model-Instanz (mit is_docker_hosted=True)
            
        Returns:
            Container ID
        """
        from servers.models import Server
        
        if not server.is_docker_hosted:
            raise ValueError("Server is not configured for Docker hosting")
        
        container_name = server.container_name
        data_volume = server.data_volume
        config_volume = server.config_volume
        server_type = server.server_type
        exposed_port = server.exposed_port
        hosting_mode = server.hosting_mode
        
        # Check if container with this name already exists and remove it
        try:
            existing = self.client.containers.get(container_name)
            logger.warning(f"Container {container_name} existiert bereits - wird entfernt")
            existing.remove(force=True)
        except docker.errors.NotFound:
            pass  # Container doesn't exist, good
        except Exception as e:
            logger.warning(f"Fehler beim Prüfen existierender Container: {e}")
        
        # Get image based on hosting mode
        if hosting_mode in ('tor', 'chutnex'):
            # Both Tor and ChutneX use Tor-enabled images
            image = self.TOR_IMAGES.get(server_type)
        else:
            image = self.IMAGES.get(server_type)
        
        internal_port = self.INTERNAL_PORTS.get(server_type)
        volume_paths = self.VOLUME_PATHS.get(server_type, {})
        
        if not image or not internal_port:
            raise ValueError(f"Unsupported server type: {server_type}")
        
        # Ensure volumes exist
        self._ensure_volume_exists(data_volume)
        self._ensure_volume_exists(config_volume)
        
        # Build environment variables based on hosting mode
        environment = {
            'WEB_MANUAL': '1',  # Disable HTTPS web interface requirement
        }
        
        if hosting_mode == 'ip':
            # IP Mode: Use host IP or configured IP
            host_ip = server.host_ip or self._get_host_ip()
            if not host_ip or host_ip == '0.0.0.0':
                host_ip = self._get_host_ip()
            environment['ADDR'] = host_ip
            logger.info(f"IP Mode: Server wird mit ADDR={host_ip} gestartet")
        elif hosting_mode == 'chutnex':
            # ChutneX Mode: Use internal Tor from ChutneX network
            environment['USE_TOR'] = '1'
            environment['CHUTNEX_MODE'] = '1'
            # Point to ChutneX's directory authorities
            if server.chutnex_network:
                environment['CHUTNEX_NETWORK'] = server.chutnex_network.slug
            logger.info(f"ChutneX Mode: Server wird im privaten Tor-Netzwerk gestartet")
        else:
            # Tor Mode: Use onion (ADDR will be set after onion is generated)
            environment['USE_TOR'] = '1'
            logger.info("Tor Mode: Server wird als Hidden Service gestartet")
        
        # Volume configuration
        volumes = {
            data_volume: {'bind': volume_paths.get('data', '/data'), 'mode': 'rw'},
            config_volume: {'bind': volume_paths.get('config', '/config'), 'mode': 'rw'},
        }
        
        # For Tor/ChutneX mode, add tor volume for persistent onion address
        if hosting_mode in ('tor', 'chutnex'):
            tor_volume = f"{container_name}-tor"
            self._ensure_volume_exists(tor_volume)
            volumes[tor_volume] = {'bind': self.TOR_PATHS.get(server_type, '/var/lib/tor/hidden_service'), 'mode': 'rw'}
        
        # For ChutneX mode, mount the status volume for DirAuthority info
        if hosting_mode == 'chutnex' and server.chutnex_network:
            status_volume = f"chutnex-status-{server.chutnex_network.slug}"
            volumes[status_volume] = {'bind': '/status', 'mode': 'ro'}
            logger.info(f"ChutneX Mode: Status Volume {status_volume} gemountet")
        
        # Determine network based on hosting mode
        if hosting_mode == 'chutnex' and server.chutnex_network:
            # ChutneX Mode: Use the private Tor network
            network_name = f"chutnex-{server.chutnex_network.slug}"
            logger.info(f"ChutneX Mode: Server wird im Netzwerk {network_name} gestartet")
        else:
            network_name = self.NETWORK_NAME
        
        # Container configuration
        container_config = {
            'name': container_name,
            'image': image,
            'detach': True,
            'environment': environment,
            'volumes': volumes,
            'network': network_name,
            'labels': {
                f'{self.LABEL_PREFIX}.managed': 'true',
                f'{self.LABEL_PREFIX}.server_id': str(server.id),
                f'{self.LABEL_PREFIX}.server_type': server_type,
                f'{self.LABEL_PREFIX}.server_name': server.name,
                f'{self.LABEL_PREFIX}.hosting_mode': hosting_mode,
            },
            'restart_policy': {'Name': 'unless-stopped'},
        }
        
        # Port mapping only for IP mode (Tor/ChutneX don't need exposed ports)
        if hosting_mode == 'ip':
            container_config['ports'] = {
                f'{internal_port}/tcp': exposed_port
            }
            container_config['healthcheck'] = {
                'test': ['CMD', 'nc', '-z', 'localhost', str(internal_port)],
                'interval': 30000000000,  # 30s in nanoseconds
                'timeout': 10000000000,   # 10s
                'retries': 3,
            }
        
        try:
            container = self.client.containers.create(**container_config)
            logger.info(f"Container erstellt: {container_name} ({container.id[:12]}) - Mode: {hosting_mode}")
            
            # Update Server with Container ID
            server.container_id = container.id
            server.docker_status = Server.DockerStatus.CREATED
            server.docker_error = ''
            server.save(update_fields=['container_id', 'docker_status', 'docker_error'])
            
            return container.id
            
        except docker.errors.APIError as e:
            logger.error(f"Fehler beim Erstellen des Containers: {e}")
            server.docker_status = Server.DockerStatus.ERROR
            server.docker_error = str(e)
            server.save(update_fields=['docker_status', 'docker_error'])
            raise
    
    def start_container(self, server) -> bool:
        """
        Startet einen Container.
        
        Falls kein Container existiert, wird einer erstellt.
        Nach dem Start wird versucht, den Fingerprint zu extrahieren.
        Bei Tor-Mode wird zusätzlich die .onion Adresse extrahiert.
        """
        from servers.models import Server
        
        container_id = server.container_id
        
        # Container erstellen falls nicht vorhanden
        if not container_id:
            container_id = self.create_server_container(server)
        
        try:
            container = self.client.containers.get(container_id)
            
            if container.status == 'running':
                logger.info(f"Container läuft bereits: {server.container_name}")
                return True
            
            server.docker_status = Server.DockerStatus.STARTING
            server.save(update_fields=['docker_status'])
            
            container.start()
            
            # Wait for container to start and initialize
            # Tor mode needs more time to generate onion address
            wait_time = 10 if server.hosting_mode in ('tor', 'chutnex') else 3
            time.sleep(wait_time)
            container.reload()
            
            if container.status == 'running':
                server.docker_status = Server.DockerStatus.RUNNING
                server.docker_error = ''
                server.save(update_fields=['docker_status', 'docker_error'])
                logger.info(f"Container gestartet: {server.container_name}")
                
                # Extract address based on hosting mode
                if server.hosting_mode in ('tor', 'chutnex'):
                    self._extract_onion_address(server)
                else:
                    self._extract_server_address(server)
                
                return True
            else:
                raise Exception(f"Container Status: {container.status}")
                
        except docker.errors.NotFound:
            # Container existiert nicht mehr - neu erstellen
            logger.warning(f"Container nicht gefunden, erstelle neu: {server.container_name}")
            server.container_id = ''
            server.save(update_fields=['container_id'])
            return self.start_container(server)
            
        except Exception as e:
            logger.error(f"Fehler beim Starten: {e}")
            server.docker_status = Server.DockerStatus.ERROR
            server.docker_error = str(e)
            server.save(update_fields=['docker_status', 'docker_error'])
            return False
    
    def stop_container(self, server, timeout: int = 10) -> bool:
        """Stoppt einen Container"""
        from servers.models import Server
        
        if not server.container_id:
            logger.warning(f"Kein Container zum Stoppen: {server.name}")
            return False
        
        try:
            container = self.client.containers.get(server.container_id)
            
            if container.status != 'running':
                logger.info(f"Container läuft nicht: {server.container_name}")
                server.docker_status = Server.DockerStatus.STOPPED
                server.save(update_fields=['docker_status'])
                return True
            
            server.docker_status = Server.DockerStatus.STOPPING
            server.save(update_fields=['docker_status'])
            
            container.stop(timeout=timeout)
            
            server.docker_status = Server.DockerStatus.STOPPED
            server.docker_error = ''
            server.save(update_fields=['docker_status', 'docker_error'])
            logger.info(f"Container gestoppt: {server.container_name}")
            return True
            
        except docker.errors.NotFound:
            server.docker_status = Server.DockerStatus.NOT_CREATED
            server.container_id = ''
            server.save(update_fields=['docker_status', 'container_id'])
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Stoppen: {e}")
            server.docker_status = Server.DockerStatus.ERROR
            server.docker_error = str(e)
            server.save(update_fields=['docker_status', 'docker_error'])
            return False
    
    def restart_container(self, server) -> bool:
        """Startet einen Container neu"""
        self.stop_container(server)
        time.sleep(2)
        return self.start_container(server)
    
    def delete_container(self, server, remove_volumes: bool = False) -> bool:
        """
        Löscht einen Container und optional seine Volumes.
        
        Args:
            server: Server Model-Instanz
            remove_volumes: Wenn True, werden auch die Volumes gelöscht
        """
        from servers.models import Server
        
        if not server.container_id:
            logger.info(f"Kein Container zu löschen: {server.name}")
            return True
        
        try:
            container = self.client.containers.get(server.container_id)
            
            # Stop if running
            if container.status == 'running':
                container.stop(timeout=5)
            
            # Remove container
            container.remove()
            logger.info(f"Container gelöscht: {server.container_name}")
            
            # Remove volumes if requested
            if remove_volumes:
                for volume_name in [server.data_volume, server.config_volume]:
                    if volume_name:
                        try:
                            volume = self.client.volumes.get(volume_name)
                            volume.remove()
                            logger.info(f"Volume gelöscht: {volume_name}")
                        except docker.errors.NotFound:
                            pass
                        except Exception as e:
                            logger.warning(f"Konnte Volume nicht löschen {volume_name}: {e}")
                
                # Also remove tor volume if exists
                tor_volume = f"{server.container_name}-tor"
                try:
                    volume = self.client.volumes.get(tor_volume)
                    volume.remove()
                    logger.info(f"Tor Volume gelöscht: {tor_volume}")
                except docker.errors.NotFound:
                    pass
            
            # Reset server fields
            server.container_id = ''
            server.docker_status = Server.DockerStatus.NOT_CREATED
            server.docker_error = ''
            server.generated_fingerprint = ''
            server.generated_address = ''
            server.onion_address = ''
            server.save(update_fields=[
                'container_id', 'docker_status', 'docker_error',
                'generated_fingerprint', 'generated_address', 'onion_address'
            ])
            
            return True
            
        except docker.errors.NotFound:
            # Container already gone
            server.container_id = ''
            server.docker_status = Server.DockerStatus.NOT_CREATED
            server.save(update_fields=['container_id', 'docker_status'])
            return True
            
        except Exception as e:
            logger.error(f"Fehler beim Löschen: {e}")
            server.docker_error = str(e)
            server.save(update_fields=['docker_error'])
            return False
    
    def get_container_logs(self, server, tail: int = 100, timestamps: bool = False) -> str:
        """Holt Container-Logs"""
        if not server.container_id:
            return "Container not created"
        
        try:
            container = self.client.containers.get(server.container_id)
            logs = container.logs(tail=tail, timestamps=timestamps)
            return logs.decode('utf-8', errors='replace')
        except docker.errors.NotFound:
            return "Container not found"
        except Exception as e:
            return f"Error fetching logs: {e}"
    
    def get_container_status(self, server) -> Dict[str, Any]:
        """
        Holt detaillierten Container-Status.
        
        Returns:
            Dict mit status, health, stats etc.
        """
        if not server.container_id:
            return {'status': 'not_created', 'running': False}
        
        try:
            container = self.client.containers.get(server.container_id)
            container.reload()
            
            health = 'unknown'
            if container.attrs.get('State', {}).get('Health'):
                health = container.attrs['State']['Health'].get('Status', 'unknown')
            
            return {
                'status': container.status,
                'running': container.status == 'running',
                'health': health,
                'started_at': container.attrs.get('State', {}).get('StartedAt'),
                'exit_code': container.attrs.get('State', {}).get('ExitCode'),
            }
            
        except docker.errors.NotFound:
            return {'status': 'not_found', 'running': False}
        except Exception as e:
            return {'status': 'error', 'running': False, 'error': str(e)}
    
    def sync_status(self, server) -> None:
        """
        Synchronisiert den DB-Status mit dem tatsächlichen Container-Status.
        """
        from servers.models import Server
        
        status = self.get_container_status(server)
        
        if status['status'] == 'running':
            new_status = Server.DockerStatus.RUNNING
        elif status['status'] in ('exited', 'dead'):
            new_status = Server.DockerStatus.STOPPED
        elif status['status'] == 'not_found':
            new_status = Server.DockerStatus.NOT_CREATED
            server.container_id = ''
        else:
            new_status = Server.DockerStatus.ERROR
        
        if server.docker_status != new_status:
            server.docker_status = new_status
            server.save(update_fields=['docker_status', 'container_id'])
    
    def _ensure_volume_exists(self, volume_name: str) -> None:
        """Erstellt ein Volume falls nicht vorhanden"""
        try:
            self.client.volumes.get(volume_name)
        except docker.errors.NotFound:
            logger.info(f"Erstelle Volume: {volume_name}")
            self.client.volumes.create(
                name=volume_name,
                labels={f'{self.LABEL_PREFIX}.managed': 'true'}
            )
    
    def _extract_server_address(self, server, max_attempts: int = 10) -> bool:
        """
        Extrahiert die Server-Adresse aus den Container-Logs (IP-Mode).
        
        Die SimpleX Server geben beim Start ihre Adresse aus:
        SMP: "Server address: smp://fingerprint@host:port"
        XFTP: "Server address: xftp://fingerprint@host:port"
        
        Args:
            server: Server Model-Instanz
            max_attempts: Maximale Versuche
            
        Returns:
            True wenn erfolgreich
        """
        if not server.container_id:
            return False
        
        # Pattern für Server-Adresse
        address_pattern = re.compile(
            r'Server address:\s*((?:smp|xftp|ntf)://[^\s]+)',
            re.IGNORECASE
        )
        
        for attempt in range(max_attempts):
            logs = self.get_container_logs(server, tail=50, timestamps=False)
            
            match = address_pattern.search(logs)
            if match:
                raw_address = match.group(1)
                
                # Extract fingerprint
                fingerprint_match = re.match(
                    r'(smp|xftp|ntf)://([^@]+)@',
                    raw_address
                )
                
                if fingerprint_match:
                    protocol = fingerprint_match.group(1)
                    fingerprint = fingerprint_match.group(2)
                    
                    # Build correct address with host IP and exposed port
                    host_ip = server.host_ip
                    if not host_ip or host_ip == '0.0.0.0':
                        host_ip = self._get_host_ip()
                    
                    port = server.exposed_port or server.default_internal_port
                    
                    generated_address = f"{protocol}://{fingerprint}@{host_ip}:{port}"
                    
                    server.generated_fingerprint = fingerprint
                    server.generated_address = generated_address
                    server.save(update_fields=['generated_fingerprint', 'generated_address'])
                    
                    logger.info(f"Server-Adresse extrahiert: {generated_address}")
                    return True
            
            # Wait and retry
            time.sleep(1)
        
        logger.warning(f"Konnte Server-Adresse nicht extrahieren für: {server.container_name}")
        return False
    
    def _extract_onion_address(self, server, max_attempts: int = 30) -> bool:
        """
        Extrahiert die .onion Adresse und Server-Fingerprint (Tor-Mode).
        
        Bei Tor-Mode generiert der Container einen Hidden Service.
        Die .onion Adresse liegt in:
        - /var/lib/tor/simplex-smp/hostname (Tor native)
        - /var/opt/simplex/onion_address (von unserem Entrypoint geschrieben)
        
        Args:
            server: Server Model-Instanz
            max_attempts: Maximale Versuche (Tor braucht länger, ~60s)
            
        Returns:
            True wenn erfolgreich
        """
        if not server.container_id:
            return False
        
        tor_path = self.TOR_PATHS.get(server.server_type, '/var/lib/tor/simplex-smp')
        alternative_path = '/var/opt/simplex/onion_address'
        
        for attempt in range(max_attempts):
            try:
                container = self.client.containers.get(server.container_id)
                
                # Try primary path first (Tor's hostname file)
                exit_code, output = container.exec_run(f'cat {tor_path}/hostname')
                
                if exit_code != 0:
                    # Try alternative path (our entrypoint writes here)
                    exit_code, output = container.exec_run(f'cat {alternative_path}')
                
                if exit_code == 0:
                    onion_address = output.decode('utf-8').strip()
                    
                    if onion_address.endswith('.onion'):
                        server.onion_address = onion_address
                        logger.info(f"Onion-Adresse extrahiert: {onion_address}")
                        
                        # Now also get the fingerprint from logs
                        self._extract_fingerprint_for_tor(server, onion_address)
                        return True
                
            except Exception as e:
                logger.debug(f"Attempt {attempt + 1}: {e}")
            
            # Log progress every 10 seconds
            if (attempt + 1) % 5 == 0:
                logger.info(f"Warte auf Tor Hidden Service... ({(attempt + 1) * 2}s)")
            
            time.sleep(2)
        
        logger.warning(f"Konnte Onion-Adresse nicht extrahieren für: {server.container_name}")
        return False
    
    def _extract_fingerprint_for_tor(self, server, onion_address: str) -> bool:
        """
        Extrahiert den Fingerprint und baut die vollständige Tor-Adresse.
        """
        # Pattern für Fingerprint (Base64 inkl. - und _)
        fingerprint_pattern = re.compile(
            r'Fingerprint:\s*([A-Za-z0-9+/=_-]+)',
            re.IGNORECASE
        )
        
        logs = self.get_container_logs(server, tail=100, timestamps=False)
        match = fingerprint_pattern.search(logs)
        
        if match:
            fingerprint = match.group(1)
            protocol = server.server_type  # smp, xftp, or ntf
            port = self.INTERNAL_PORTS.get(server.server_type, 5223)
            
            # Build full address: smp://fingerprint@abc123.onion:5223
            generated_address = f"{protocol}://{fingerprint}@{onion_address}:{port}"
            
            server.generated_fingerprint = fingerprint
            server.generated_address = generated_address
            server.save(update_fields=['generated_fingerprint', 'generated_address', 'onion_address'])
            
            logger.info(f"Tor Server-Adresse: {generated_address}")
            return True
        
        # Fingerprint not found yet, save onion at least
        server.save(update_fields=['onion_address'])
        return False
    
    def list_managed_containers(self) -> List[Dict[str, Any]]:
        """
        Listet alle von uns verwalteten Server-Container.
        """
        containers = self.client.containers.list(
            all=True,
            filters={'label': f'{self.LABEL_PREFIX}.managed=true'}
        )
        
        return [{
            'id': c.id,
            'name': c.name,
            'status': c.status,
            'server_type': c.labels.get(f'{self.LABEL_PREFIX}.server_type', 'unknown'),
            'server_name': c.labels.get(f'{self.LABEL_PREFIX}.server_name', 'unknown'),
            'hosting_mode': c.labels.get(f'{self.LABEL_PREFIX}.hosting_mode', 'ip'),
        } for c in containers]
    
    def cleanup_orphaned_containers(self) -> int:
        """
        Entfernt Container ohne zugehörigen Server.
        
        Returns:
            Anzahl der entfernten Container
        """
        from servers.models import Server
        
        managed = self.list_managed_containers()
        known_ids = set(
            Server.objects.filter(is_docker_hosted=True)
            .values_list('container_id', flat=True)
        )
        
        removed = 0
        for container_info in managed:
            if container_info['id'] not in known_ids:
                try:
                    container = self.client.containers.get(container_info['id'])
                    container.remove(force=True)
                    logger.info(f"Orphaned Container entfernt: {container_info['name']}")
                    removed += 1
                except Exception as e:
                    logger.error(f"Fehler beim Entfernen: {e}")
        
        return removed
    
    def get_image_info(self, server_type: str, tor_mode: bool = False) -> Optional[Dict[str, Any]]:
        """
        Prüft ob das Docker Image für einen Server-Typ verfügbar ist.
        
        Args:
            server_type: 'smp', 'xftp', oder 'ntf'
            tor_mode: True für Tor-Images
            
        Returns:
            Image-Info dict oder None wenn nicht gefunden
        """
        if tor_mode:
            image_name = self.TOR_IMAGES.get(server_type)
        else:
            image_name = self.IMAGES.get(server_type)
            
        if not image_name:
            return None
        
        try:
            image = self.client.images.get(image_name)
            return {
                'id': image.id,
                'tags': image.tags,
                'size': image.attrs.get('Size', 0),
                'created': image.attrs.get('Created'),
            }
        except docker.errors.ImageNotFound:
            return None
        except Exception as e:
            logger.error(f"Fehler beim Abrufen des Images {image_name}: {e}")
            return None
    
    def check_images_available(self) -> Dict[str, Dict[str, bool]]:
        """
        Prüft welche Server-Images verfügbar sind.
        
        Returns:
            Dict mit server_type -> {ip: bool, tor: bool}
        """
        result = {}
        for server_type in self.IMAGES.keys():
            result[server_type] = {
                'ip': self.get_image_info(server_type, tor_mode=False) is not None,
                'tor': self.get_image_info(server_type, tor_mode=True) is not None,
            }
        return result
    
    def check_image_exists(self, server_type: str, hosting_mode: str = 'ip') -> bool:
        """
        Prüft ob ein bestimmtes Server-Image verfügbar ist.
        
        Args:
            server_type: 'smp', 'xftp', oder 'ntf'
            hosting_mode: 'ip' oder 'tor'
            
        Returns:
            True wenn Image existiert, sonst False
        """
        tor_mode = hosting_mode in ('tor', 'chutnex')
        return self.get_image_info(server_type, tor_mode=tor_mode) is not None


# Singleton-Instanz
_server_docker_manager: Optional[ServerDockerManager] = None


def get_server_docker_manager() -> ServerDockerManager:
    """Gibt die ServerDockerManager Singleton-Instanz zurück"""
    global _server_docker_manager
    if _server_docker_manager is None:
        _server_docker_manager = ServerDockerManager()
    return _server_docker_manager