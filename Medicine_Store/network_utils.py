"""Detect network / connectivity failures for email and payment flows."""
import errno
import socket

try:
    from smtplib import SMTPException
except ImportError:
    SMTPException = Exception

try:
    import requests
    REQUESTS_ERRORS = (
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        requests.exceptions.ConnectTimeout,
    )
except ImportError:
    REQUESTS_ERRORS = ()


_NETWORK_KEYWORDS = (
    'network',
    'connection',
    'timed out',
    'timeout',
    'unreachable',
    'getaddrinfo',
    'nodename nor servname',
    'failed to establish',
    'no route to host',
    'name or service not known',
    'internet',
    'offline',
)


def is_network_error(exc):
    """Return True if the exception likely indicates no internet / unreachable host."""
    if exc is None:
        return False

    network_types = (
        ConnectionError,
        TimeoutError,
        socket.timeout,
        socket.gaierror,
        SMTPException,
        *REQUESTS_ERRORS,
    )
    if isinstance(exc, network_types):
        return True

    if isinstance(exc, OSError):
        winerr = getattr(exc, 'winerror', None)
        if winerr in (10051, 10060, 10061, 10054, 10065):
            return True
        if exc.errno in (
            errno.ENETUNREACH,
            errno.ENETDOWN,
            errno.ETIMEDOUT,
            errno.ECONNREFUSED,
            errno.EHOSTUNREACH,
            errno.ENOTCONN,
        ):
            return True

    msg = str(exc).lower()
    return any(keyword in msg for keyword in _NETWORK_KEYWORDS)
