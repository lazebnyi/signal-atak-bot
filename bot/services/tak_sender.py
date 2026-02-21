import logging
import socket
import ssl

from core.config import SSL_CA, SSL_CERT, SSL_KEY, TAK_HOST, TAK_PORT

log = logging.getLogger(__name__)


class TAKSender:
    """Sends CoT XML events to a TAK server via SSL or plain TCP."""

    def __init__(
        self,
        host: str = TAK_HOST,
        port: int = TAK_PORT,
        use_ssl: bool = True,
        ssl_cert: str = SSL_CERT,
        ssl_key: str = SSL_KEY,
        ssl_ca: str = SSL_CA,
    ):
        self.host = host
        self.port = port
        self.use_ssl = use_ssl
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key
        self.ssl_ca = ssl_ca

    def send(self, cot_xml: str) -> bool:
        """Send a CoT event using the configured transport."""
        if self.use_ssl:
            return self._send_ssl(cot_xml)
        return self._send_tcp(cot_xml)

    def _send_ssl(self, cot_xml: str) -> bool:
        """Send CoT XML to TAK server via SSL/TLS with client certificate."""
        try:
            ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            ctx.load_cert_chain(certfile=self.ssl_cert, keyfile=self.ssl_key)
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)
                with ctx.wrap_socket(sock) as ssock:
                    ssock.connect((self.host, self.port))
                    ssock.sendall(cot_xml.encode("utf-8"))
                    log.info(
                        "Sent CoT via SSL to %s:%d (%d bytes)",
                        self.host,
                        self.port,
                        len(cot_xml),
                    )
                    return True
        except ConnectionRefusedError:
            log.error(
                "Connection refused — is TAK server running on %s:%d?",
                self.host,
                self.port,
            )
        except TimeoutError:
            log.error("Connection timed out to %s:%d", self.host, self.port)
        except ssl.SSLError as exc:
            log.error("SSL error: %s", exc)
        except OSError as exc:
            log.error("Network error sending CoT: %s", exc)
        return False

    def _send_tcp(self, cot_xml: str) -> bool:
        """Send CoT XML to TAK server via plain TCP."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(5)
                sock.connect((self.host, self.port))
                sock.sendall(cot_xml.encode("utf-8"))
                log.info(
                    "Sent CoT to %s:%d (%d bytes)", self.host, self.port, len(cot_xml)
                )
                return True
        except ConnectionRefusedError:
            log.error(
                "Connection refused — is TAK server running on %s:%d?",
                self.host,
                self.port,
            )
        except TimeoutError:
            log.error("Connection timed out to %s:%d", self.host, self.port)
        except OSError as exc:
            log.error("Network error sending CoT: %s", exc)
        return False
