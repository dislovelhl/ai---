"""Core accessibility checker logic for testing tool accessibility from China perspective."""
from shared.models import Tool, AccessibilityCheckLog
from shared.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import httpx
import time
import socket
import asyncio
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


async def test_http_connectivity(
    url: str,
    timeout: float = 10.0,
    verify_ssl: bool = True,
    user_agent: Optional[str] = None
) -> dict:
    """
    Test HTTP/HTTPS connectivity to a given URL.

    Args:
        url: The URL to test (must include http:// or https://)
        timeout: Request timeout in seconds (default: 10.0)
        verify_ssl: Whether to verify SSL certificates (default: True)
        user_agent: Custom user-agent string. If None, uses common browser UA.

    Returns:
        dict: Test results with keys:
            - success: bool - Whether the request succeeded
            - status_code: int or None - HTTP status code
            - response_time: float - Response time in seconds
            - error_type: str or None - Type of error if failed (timeout, ssl, connection, etc.)
            - error_message: str or None - Detailed error message
    """
    # Default user-agent to mimic Chrome browser
    if user_agent is None:
        user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )

    headers = {
        "User-Agent": user_agent,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    start_time = time.time()
    result = {
        "success": False,
        "status_code": None,
        "response_time": 0.0,
        "error_type": None,
        "error_message": None,
    }

    try:
        async with httpx.AsyncClient(verify=verify_ssl) as client:
            response = await client.get(
                url,
                headers=headers,
                timeout=timeout,
                follow_redirects=True  # Follow redirects to final destination
            )

            response_time = time.time() - start_time
            result["response_time"] = response_time
            result["status_code"] = response.status_code

            # Consider 2xx and 3xx status codes as successful
            if 200 <= response.status_code < 400:
                result["success"] = True
                logger.debug(f"HTTP connectivity test succeeded for {url}: {response.status_code} in {response_time:.2f}s")
            else:
                result["error_type"] = "http_error"
                result["error_message"] = f"HTTP {response.status_code}"
                logger.debug(f"HTTP connectivity test failed for {url}: HTTP {response.status_code}")

    except httpx.TimeoutException as e:
        result["response_time"] = time.time() - start_time
        result["error_type"] = "timeout"
        result["error_message"] = f"Request timeout after {timeout}s"
        logger.debug(f"HTTP connectivity test timeout for {url}: {e}")

    except httpx.SSLError as e:
        result["response_time"] = time.time() - start_time
        result["error_type"] = "ssl_error"
        result["error_message"] = f"SSL verification failed: {str(e)}"
        logger.debug(f"HTTP connectivity test SSL error for {url}: {e}")

    except httpx.ConnectError as e:
        result["response_time"] = time.time() - start_time
        result["error_type"] = "connection_error"
        result["error_message"] = f"Connection failed: {str(e)}"
        logger.debug(f"HTTP connectivity test connection error for {url}: {e}")

    except httpx.HTTPError as e:
        result["response_time"] = time.time() - start_time
        result["error_type"] = "http_error"
        result["error_message"] = f"HTTP error: {str(e)}"
        logger.debug(f"HTTP connectivity test error for {url}: {e}")

    except Exception as e:
        result["response_time"] = time.time() - start_time
        result["error_type"] = "unknown_error"
        result["error_message"] = f"Unexpected error: {str(e)}"
        logger.error(f"Unexpected error during HTTP connectivity test for {url}: {e}")

    return result


async def test_dns_resolution(
    url: str,
    timeout: float = 5.0
) -> dict:
    """
    Test DNS resolution to detect DNS-level blocking.

    DNS poisoning or DNS-level blocking is a common censorship technique in China
    where DNS queries return fake IPs (often pointing to block pages) or fail entirely.

    Args:
        url: The URL to test (will extract hostname for DNS lookup)
        timeout: DNS resolution timeout in seconds (default: 5.0)

    Returns:
        dict: Test results with keys:
            - success: bool - Whether DNS resolution succeeded
            - hostname: str - The hostname that was resolved
            - ip_addresses: list[str] or None - List of resolved IP addresses
            - resolution_time: float - DNS resolution time in seconds
            - error_type: str or None - Type of error if failed (timeout, nxdomain, etc.)
            - error_message: str or None - Detailed error message
    """
    # Parse URL to extract hostname
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname or parsed.netloc or url

        # Remove port if present in hostname
        if ':' in hostname and not hostname.startswith('['):  # Not IPv6
            hostname = hostname.split(':')[0]

    except Exception as e:
        logger.error(f"Failed to parse URL {url}: {e}")
        return {
            "success": False,
            "hostname": url,
            "ip_addresses": None,
            "resolution_time": 0.0,
            "error_type": "invalid_url",
            "error_message": f"Invalid URL format: {str(e)}"
        }

    if not hostname:
        return {
            "success": False,
            "hostname": url,
            "ip_addresses": None,
            "resolution_time": 0.0,
            "error_type": "invalid_url",
            "error_message": "Could not extract hostname from URL"
        }

    start_time = time.time()
    result = {
        "success": False,
        "hostname": hostname,
        "ip_addresses": None,
        "resolution_time": 0.0,
        "error_type": None,
        "error_message": None,
    }

    try:
        # Use asyncio.wait_for with timeout to prevent hanging
        # socket.getaddrinfo is a blocking call, so we run it in a thread executor
        dns_info = await asyncio.wait_for(
            asyncio.to_thread(
                socket.getaddrinfo,
                hostname,
                None,  # port (None means any)
                socket.AF_UNSPEC,  # Address family (IPv4 or IPv6)
                socket.SOCK_STREAM  # Socket type (TCP)
            ),
            timeout=timeout
        )

        resolution_time = time.time() - start_time
        result["resolution_time"] = resolution_time

        # Extract unique IP addresses from getaddrinfo results
        # getaddrinfo returns: [(family, type, proto, canonname, sockaddr), ...]
        # sockaddr is (ip, port) for IPv4 or (ip, port, flow, scope) for IPv6
        ip_addresses = list(set([info[4][0] for info in dns_info]))

        result["success"] = True
        result["ip_addresses"] = ip_addresses
        logger.debug(f"DNS resolution succeeded for {hostname}: {ip_addresses} in {resolution_time:.3f}s")

    except asyncio.TimeoutError:
        result["resolution_time"] = time.time() - start_time
        result["error_type"] = "timeout"
        result["error_message"] = f"DNS resolution timeout after {timeout}s"
        logger.debug(f"DNS resolution timeout for {hostname}")

    except socket.gaierror as e:
        result["resolution_time"] = time.time() - start_time
        # gaierror codes: EAI_NONAME (-2), EAI_AGAIN (-3), etc.
        if e.errno == socket.EAI_NONAME or "Name or service not known" in str(e):
            result["error_type"] = "nxdomain"
            result["error_message"] = f"Domain does not exist: {hostname}"
        elif e.errno == socket.EAI_AGAIN or "Temporary failure" in str(e):
            result["error_type"] = "dns_server_error"
            result["error_message"] = f"DNS server temporary failure: {str(e)}"
        else:
            result["error_type"] = "dns_error"
            result["error_message"] = f"DNS resolution error: {str(e)}"
        logger.debug(f"DNS resolution error for {hostname}: {e}")

    except OSError as e:
        result["resolution_time"] = time.time() - start_time
        result["error_type"] = "network_error"
        result["error_message"] = f"Network error during DNS resolution: {str(e)}"
        logger.debug(f"Network error during DNS resolution for {hostname}: {e}")

    except Exception as e:
        result["resolution_time"] = time.time() - start_time
        result["error_type"] = "unknown_error"
        result["error_message"] = f"Unexpected error: {str(e)}"
        logger.error(f"Unexpected error during DNS resolution for {hostname}: {e}")

    return result


async def check_tool_accessibility(tool: Tool, session: AsyncSession) -> dict:
    """
    Check if a tool is accessible from China.

    Args:
        tool: The Tool instance to check
        session: Database session for logging results

    Returns:
        dict: Check results with keys:
            - was_accessible: bool
            - requires_vpn: bool
            - response_time: float (in seconds)
            - error_message: str or None
    """
    logger.info(f"Checking accessibility for tool: {tool.name}")

    # Placeholder implementation - will be completed in subtasks 2.4-2.5
    # TODO: Implement accessibility scoring logic (subtask 2.4)
    # TODO: Add check result persistence (subtask 2.5)

    return {
        "was_accessible": False,
        "requires_vpn": False,
        "response_time": 0.0,
        "error_message": "Not implemented yet"
    }
