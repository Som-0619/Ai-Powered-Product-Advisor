"""SSRF (Server-Side Request Forgery) protection validator."""

import ipaddress
import socket
from urllib.parse import urlparse
from typing import List, Optional, Set
from app.core.logging import logger


class SSRFSecurityError(ValueError):
    """Raised when a URL targets a private, internal, or forbidden network."""
    pass


# Private, loopback, link-local, and cloud metadata subnets to block
BLOCKED_IP_NETWORKS = [
    # IPv4
    ipaddress.ip_network("0.0.0.0/8"),          # Current network (only valid as source)
    ipaddress.ip_network("10.0.0.0/8"),          # RFC 1918 Private
    ipaddress.ip_network("100.64.0.0/10"),       # Carrier-grade NAT
    ipaddress.ip_network("127.0.0.0/8"),        # Loopback
    ipaddress.ip_network("169.254.0.0/16"),      # Link-local / AWS & GCP metadata (169.254.169.254)
    ipaddress.ip_network("172.16.0.0/12"),       # RFC 1918 Private
    ipaddress.ip_network("192.0.0.0/24"),        # IETF Protocol Assignments
    ipaddress.ip_network("192.0.2.0/24"),        # TEST-NET-1 documentation
    ipaddress.ip_network("192.168.0.0/16"),      # RFC 1918 Private
    ipaddress.ip_network("198.18.0.0/15"),       # Network benchmark tests
    ipaddress.ip_network("198.51.100.0/24"),     # TEST-NET-2 documentation
    ipaddress.ip_network("203.0.113.0/24"),      # TEST-NET-3 documentation
    ipaddress.ip_network("224.0.0.0/4"),         # Multicast
    ipaddress.ip_network("240.0.0.0/4"),         # Reserved / Future use
    ipaddress.ip_network("255.255.255.255/32"),  # Broadcast
    # IPv6
    ipaddress.ip_network("::/128"),              # Unspecified
    ipaddress.ip_network("::1/128"),             # Loopback
    ipaddress.ip_network("::ffff:0:0/96"),       # IPv4-mapped IPv6
    ipaddress.ip_network("64:ff9b::/96"),        # IPv4/IPv6 translation
    ipaddress.ip_network("100::/64"),            # Discard prefix
    ipaddress.ip_network("2001:db8::/32"),       # Documentation
    ipaddress.ip_network("fc00::/7"),            # Unique Local Addresses (ULA)
    ipaddress.ip_network("fe80::/10"),           # Link-local
    ipaddress.ip_network("ff00::/8"),            # Multicast
]

BLOCKED_HOSTNAMES = {
    "localhost",
    "metadata.google.internal",
    "instance-data",
    "vault.internal",
}

ALLOWED_SCHEMES = {"http", "https"}
ALLOWED_PORTS = {80, 443, 8080, 8443}


class SSRFValidator:
    """Validates URLs against SSRF vulnerabilities before any outbound HTTP request."""

    @classmethod
    def validate_url(
        cls,
        url: str,
        allowed_schemes: Optional[Set[str]] = None,
        allowed_ports: Optional[Set[int]] = None,
    ) -> str:
        """Validate URL and resolve IP addresses to ensure no private/internal network access.

        Returns normalized URL if safe, or raises SSRFSecurityError.
        """
        if not url or not isinstance(url, str):
            raise SSRFSecurityError("URL must be a non-empty string.")

        parsed = urlparse(url.strip())
        schemes = allowed_schemes or ALLOWED_SCHEMES
        if parsed.scheme.lower() not in schemes:
            raise SSRFSecurityError(
                f"Forbidden URL scheme '{parsed.scheme}'. Only {schemes} are permitted."
            )

        hostname = parsed.hostname
        if not hostname:
            raise SSRFSecurityError("URL does not contain a valid hostname.")

        hostname_lower = hostname.lower()

        # Check blocked hostnames and internal patterns
        if hostname_lower in BLOCKED_HOSTNAMES:
            raise SSRFSecurityError(f"Target hostname '{hostname}' is explicitly blocked.")

        if (
            hostname_lower.endswith(".local")
            or hostname_lower.endswith(".internal")
            or hostname_lower.endswith(".lan")
            or hostname_lower.endswith(".localhost")
        ):
            raise SSRFSecurityError(f"Internal domain name '{hostname}' is not permitted.")

        # Check port
        port = parsed.port or (443 if parsed.scheme.lower() == "https" else 80)
        valid_ports = allowed_ports or ALLOWED_PORTS
        if port not in valid_ports:
            raise SSRFSecurityError(
                f"Target port {port} is not in permitted ports {valid_ports}."
            )

        # Resolve IP addresses and inspect each one
        resolved_ips = cls._resolve_hostname(hostname)
        for ip in resolved_ips:
            cls._check_ip_safety(ip, hostname)

        return url

    @classmethod
    def _resolve_hostname(cls, hostname: str) -> List[ipaddress.IPv4Address | ipaddress.IPv6Address]:
        """Resolve DNS for hostname and return all resolved IP addresses."""
        try:
            # Check if hostname is already an IP literal
            return [ipaddress.ip_address(hostname)]
        except ValueError:
            pass

        try:
            addr_info = socket.getaddrinfo(hostname, None)
            resolved: List[ipaddress.IPv4Address | ipaddress.IPv6Address] = []
            for family, _, _, _, sockaddr in addr_info:
                ip_str = sockaddr[0]
                resolved.append(ipaddress.ip_address(ip_str))
            if not resolved:
                raise SSRFSecurityError(f"Hostname '{hostname}' could not be resolved.")
            return resolved
        except socket.gaierror as err:
            raise SSRFSecurityError(f"DNS resolution failed for '{hostname}': {err}")

    @classmethod
    def _check_ip_safety(
        cls,
        ip: ipaddress.IPv4Address | ipaddress.IPv6Address,
        hostname: str,
    ) -> None:
        """Ensure IP address does not fall into any blocked, private, or loopback range."""
        if ip.is_loopback:
            raise SSRFSecurityError(f"Target '{hostname}' resolves to loopback IP {ip}.")
        if ip.is_private:
            raise SSRFSecurityError(f"Target '{hostname}' resolves to private IP {ip}.")
        if ip.is_link_local:
            raise SSRFSecurityError(f"Target '{hostname}' resolves to link-local IP {ip}.")
        if ip.is_multicast:
            raise SSRFSecurityError(f"Target '{hostname}' resolves to multicast IP {ip}.")
        if ip.is_reserved:
            raise SSRFSecurityError(f"Target '{hostname}' resolves to reserved IP {ip}.")
        if ip.is_unspecified:
            raise SSRFSecurityError(f"Target '{hostname}' resolves to unspecified IP {ip}.")

        for blocked_net in BLOCKED_IP_NETWORKS:
            if ip in blocked_net:
                raise SSRFSecurityError(
                    f"Target '{hostname}' resolves to blocked network {blocked_net} ({ip})."
                )
