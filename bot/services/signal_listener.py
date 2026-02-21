import contextlib
import json
import logging
import socket
import time

from core.config import SIGNAL_CLI_HOST, SIGNAL_CLI_PORT
from core.helpers import extract_message, parse_coordinate

log = logging.getLogger(__name__)


class SignalListener:
    """Connects to signal-cli JSON-RPC daemon via TCP socket."""

    def __init__(self, host: str = SIGNAL_CLI_HOST, port: int = SIGNAL_CLI_PORT):
        self.host = host
        self.port = port
        self._sock = None
        self._buffer = ""

    def connect(self):
        """Establish TCP connection to signal-cli daemon."""
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.connect((self.host, self.port))
        self._sock.settimeout(2.0)
        log.info("Connected to signal-cli daemon at %s:%d", self.host, self.port)

    def reconnect(self):
        """Reconnect after connection loss."""
        self.close()
        time.sleep(2)
        self.connect()

    def close(self):
        """Close the TCP socket."""
        if self._sock:
            with contextlib.suppress(OSError):
                self._sock.close()
            self._sock = None

    def poll(self) -> list[dict]:
        """Read pending JSON-RPC notifications from the daemon."""
        if self._sock is None:
            self.connect()

        try:
            data = self._sock.recv(65536).decode("utf-8")
            if not data:
                log.warning("signal-cli daemon closed connection")
                self.reconnect()
                return []
            self._buffer += data
        except TimeoutError:
            return []
        except OSError as exc:
            log.error("Socket error: %s — reconnecting", exc)
            self.reconnect()
            return []

        messages = []
        while "\n" in self._buffer:
            line, self._buffer = self._buffer.split("\n", 1)
            line = line.strip()
            if not line:
                continue

            try:
                rpc_msg = json.loads(line)
            except json.JSONDecodeError:
                log.warning("Invalid JSON from daemon: %s", line[:200])
                continue

            if rpc_msg.get("method") != "receive":
                continue

            params = rpc_msg.get("params", {})
            envelope = params.get("envelope", {})

            msg = extract_message(envelope)
            if msg:
                messages.append(msg)

        return messages

    @staticmethod
    def parse(text: str) -> tuple[float, float, str] | None:
        return parse_coordinate(text)
