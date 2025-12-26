import socket
import ssl
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.utils import timezone

logger = logging.getLogger(__name__)


def parse_simplex_address(address):
    """Extrahiert Host und Port aus SimpleX-Adresse"""
    try:
        if '://' in address:
            address = address.split('://', 1)[1]
        
        if '@' in address:
            address = address.split('@', 1)[1]
        
        if ':' in address:
            parts = address.rsplit(':', 1)
            host = parts[0]
            port = int(parts[1]) if len(parts) > 1 else 5223
        else:
            host = address
            port = 5223
            
        return host, port
    except Exception as e:
        logger.error(f"Failed to parse address {address}: {e}")
        return None, None


def test_server_connection(server, timeout=30):
    """Testet Verbindung zu einem Server"""
    start_time = time.time()
    success = False
    latency_ms = None
    error_message = ""
    tls_version = ""
    used_tor = False
    
    try:
        host, port = parse_simplex_address(server.address)
        
        if not host:
            raise ValueError(f"Could not parse address: {server.address}")
        
        # Onion-Adressen über Tor
        if '.onion' in host:
            used_tor = True
            import socks
            sock = socks.socksocket()
            sock.set_proxy(socks.SOCKS5, "127.0.0.1", 9050)
            sock.settimeout(timeout)
        else:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
        
        # TLS Context
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        # Verbinden
        connect_start = time.time()
        sock.connect((host, port))
        
        # TLS Handshake
        ssl_sock = context.wrap_socket(sock, server_hostname=host)
        
        latency_ms = int((time.time() - connect_start) * 1000)
        tls_version = ssl_sock.version() or ""
        success = True
        
        ssl_sock.close()
        
    except socket.timeout:
        error_message = "Connection timeout"
    except ConnectionRefusedError:
        error_message = "Connection refused"
    except Exception as e:
        error_message = str(e)[:200]
    
    return {
        'server': server,
        'success': success,
        'latency_ms': latency_ms,
        'error_message': error_message,
        'tls_version': tls_version,
        'used_tor': used_tor
    }


def run_server_check(test_id):
    """Führt Server-Check für einen Test aus"""
    from .models import Test, TestResult
    
    try:
        test = Test.objects.get(pk=test_id)
    except Test.DoesNotExist:
        logger.error(f"Test {test_id} not found")
        return
    
    servers = list(test.target_servers)
    if not servers:
        logger.warning(f"Test '{test.name}' has no servers")
        return
    
    logger.info(f"Running check for '{test.name}' with {len(servers)} servers")
    
    results = []
    
    # Parallel execution
    with ThreadPoolExecutor(max_workers=min(10, len(servers))) as executor:
        future_to_server = {
            executor.submit(test_server_connection, server): server 
            for server in servers
        }
        
        for future in as_completed(future_to_server):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                server = future_to_server[future]
                results.append({
                    'server': server,
                    'success': False,
                    'latency_ms': None,
                    'error_message': str(e)[:200],
                    'tls_version': "",
                    'used_tor': False
                })
    
    # Ergebnisse speichern
    now = timezone.now()
    successful = 0
    failed = 0
    
    for result in results:
        TestResult.objects.create(
            test=test,
            server=result['server'],
            timestamp=now,
            success=result['success'],
            latency_ms=result['latency_ms'],
            error_message=result['error_message'] or "",
            used_tor=result['used_tor'],
            tls_version=result['tls_version'] or ""
        )
        
        if result['success']:
            successful += 1
            # Update server - nur Felder die existieren
            result['server'].last_check = now
            result['server'].last_latency = result['latency_ms']
            result['server'].save(update_fields=['last_check', 'last_latency'])
        else:
            failed += 1
    
    # Test-Statistiken aktualisieren
    test.last_run = now
    test.total_runs += 1
    test.successful_runs += successful
    test.failed_runs += failed
    test.save(update_fields=['last_run', 'total_runs', 'successful_runs', 'failed_runs'])
    
    logger.info(f"✅ Test '{test.name}' completed: {successful} OK, {failed} failed")
    print(f"✅ Test '{test.name}' completed: {successful} OK, {failed} failed")
    
    # Optional: InfluxDB
    if test.write_to_influxdb:
        try:
            write_results_to_influxdb(test, results, now)
        except Exception as e:
            logger.error(f"Failed to write to InfluxDB: {e}")
    
    return results


def write_results_to_influxdb(test, results, timestamp):
    """Schreibt Ergebnisse nach InfluxDB"""
    try:
        from core.metrics import write_metric
        
        for result in results:
            write_metric(
                measurement='server_check',
                tags={
                    'test_name': test.name,
                    'server_name': result['server'].name,
                    'server_type': result['server'].server_type,
                },
                fields={
                    'success': 1 if result['success'] else 0,
                    'latency_ms': result['latency_ms'] or 0,
                    'used_tor': 1 if result['used_tor'] else 0,
                },
                timestamp=timestamp
            )
    except Exception as e:
        logger.error(f"InfluxDB write error: {e}")
