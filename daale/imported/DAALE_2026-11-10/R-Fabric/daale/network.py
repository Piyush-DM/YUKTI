"""Connection helpers for networks where IPv6 does not work.

Google's API hostname resolves to eight IPv6 addresses before any IPv4 one. On a network with an IPv6
route that leads nowhere, each of those connection attempts hangs (about 21 s on Windows) before the next
is tried, so every new connection spent about 169 s failing over to IPv4 before a byte of the request was
sent. Measured on 2026-11-09: listing the models took 169 s, and 1.2 s with IPv4 only. For a while that
wait was mistaken for Google queueing the request.
"""

import socket
from urllib.parse import urlparse

import urllib3.util.connection as _connection


def force_ipv4():
    """Make every connection opened through urllib3, and so ``requests``, use IPv4 only.

    It replaces one function in urllib3, so it applies to the whole process and stays until the process ends.
    """
    _connection.allowed_gai_family = lambda: socket.AF_INET


def ipv6_is_broken(url, probe_seconds=3.0):
    """True when ``url``'s host has IPv6 addresses that do not answer while an IPv4 address does.

    A diagnostic: one connection attempt for each family, each limited to ``probe_seconds``. It says
    False when it cannot tell (no IPv6 or no IPv4 address, the name does not resolve, both fail).
    """
    parsed = urlparse(url or "")
    host = parsed.hostname
    if not host:
        return False
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    try:
        addresses = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except OSError:
        return False
    v6 = [entry[4] for entry in addresses if entry[0] == socket.AF_INET6]
    v4 = [entry[4] for entry in addresses if entry[0] == socket.AF_INET]
    if not v6 or not v4:
        return False
    return not _connects(v6[0], probe_seconds) and _connects(v4[0], probe_seconds)


def _connects(address, seconds):
    try:
        with socket.create_connection(address[:2], timeout=seconds):
            return True
    except OSError:
        return False
