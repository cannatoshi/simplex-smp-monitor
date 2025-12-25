from django import template
import re

register = template.Library()

@register.filter
def get_fingerprint(address):
    """Extract fingerprint from SimpleX address"""
    try:
        pattern = r'^(smp|xftp)://([^:@]+)'
        match = re.match(pattern, address.strip())
        if match:
            return match.group(2)
    except:
        pass
    return '-'

@register.filter
def get_password(address):
    """Extract password from SimpleX address"""
    try:
        pattern = r'^(smp|xftp)://[^:@]+:([^@]+)@'
        match = re.match(pattern, address.strip())
        if match:
            return match.group(2)
    except:
        pass
    return ''
