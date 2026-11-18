import ipaddress
import socket
from urllib.parse import urlparse
from fastapi import HTTPException, status


def validate_and_sanitize_url(url: str) -> str:
    """
    Validates the website URL, checks for RFC compliance, scheme (http/https),
    and strictly enforces SSRF protection by blocking private/internal/loopback/link-local IP addresses.
    """
    url = url.strip()
    if not url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL cannot be empty."
        )

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid URL scheme '{parsed.scheme}'. Only 'http' and 'https' are allowed."
        )

    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL: Missing host."
        )

    # Disallow common localhost aliases
    if hostname.lower() in ("localhost", "0.0.0.0", "127.0.0.1", "::1", "metadata.google.internal"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Access to private/local host '{hostname}' is forbidden for security (SSRF protection)."
        )

    # Resolve IP address to prevent SSRF against private/loopback/cloud metadata networks
    try:
        addr_info = socket.getaddrinfo(hostname, None)
        for family, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            ip = ipaddress.ip_address(ip_str)

            if (
                ip.is_private
                or ip.is_loopback
                or ip.is_link_local
                or ip.is_multicast
                or ip.is_reserved
                or ip.is_unspecified
            ):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Access to private or reserved IP address ({ip_str}) is blocked (SSRF protection)."
                )
    except socket.gaierror:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Could not resolve domain name '{hostname}'. Please provide a reachable, valid URL."
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to validate host: {str(e)}"
        )

    return url
