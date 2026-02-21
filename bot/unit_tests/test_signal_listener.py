import json
import socket
from unittest.mock import MagicMock, patch

import pytest

from services.signal_listener import SignalListener


@pytest.fixture
def listener():
    return SignalListener(host="127.0.0.1", port=7583)


def _make_rpc_message(text, sender="+1234567890", timestamp=1700000000):
    """Build a JSON-RPC notification string as signal-cli daemon would send."""
    return json.dumps({
        "jsonrpc": "2.0",
        "method": "receive",
        "params": {
            "envelope": {
                "sourceNumber": sender,
                "dataMessage": {
                    "message": text,
                    "timestamp": timestamp,
                },
            }
        },
    })


class TestSignalListenerConnect:
    @patch("services.signal_listener.socket.socket")
    def test_connect_creates_socket(self, mock_socket_cls, listener):
        mock_sock = MagicMock()
        mock_socket_cls.return_value = mock_sock

        listener.connect()

        mock_sock.connect.assert_called_once_with(("127.0.0.1", 7583))
        mock_sock.settimeout.assert_called_once_with(2.0)
        assert listener._sock is mock_sock

    def test_close_clears_socket(self, listener):
        listener._sock = MagicMock()
        listener.close()
        assert listener._sock is None

    def test_close_handles_no_socket(self, listener):
        listener._sock = None
        listener.close()  # should not raise

    def test_close_handles_os_error(self, listener):
        mock_sock = MagicMock()
        mock_sock.close.side_effect = OSError("broken")
        listener._sock = mock_sock
        listener.close()  # should not raise
        assert listener._sock is None


class TestSignalListenerPoll:
    def test_poll_parses_single_message(self, listener):
        rpc = _make_rpc_message("48.5 39.8 tank") + "\n"
        mock_sock = MagicMock()
        mock_sock.recv.return_value = rpc.encode("utf-8")
        listener._sock = mock_sock

        messages = listener.poll()

        assert len(messages) == 1
        assert messages[0]["text"] == "48.5 39.8 tank"
        assert messages[0]["sender"] == "+1234567890"

    def test_poll_parses_multiple_messages(self, listener):
        rpc = (
            _make_rpc_message("48.5 39.8 tank") + "\n"
            + _make_rpc_message("49.0 40.0 infantry") + "\n"
        )
        mock_sock = MagicMock()
        mock_sock.recv.return_value = rpc.encode("utf-8")
        listener._sock = mock_sock

        messages = listener.poll()
        assert len(messages) == 2

    def test_poll_ignores_non_receive_methods(self, listener):
        rpc = json.dumps({
            "jsonrpc": "2.0",
            "method": "send",
            "params": {},
        }) + "\n"
        mock_sock = MagicMock()
        mock_sock.recv.return_value = rpc.encode("utf-8")
        listener._sock = mock_sock

        messages = listener.poll()
        assert messages == []

    def test_poll_ignores_invalid_json(self, listener):
        mock_sock = MagicMock()
        mock_sock.recv.return_value = b"not json\n"
        listener._sock = mock_sock

        messages = listener.poll()
        assert messages == []

    def test_poll_handles_timeout(self, listener):
        mock_sock = MagicMock()
        mock_sock.recv.side_effect = socket.timeout
        listener._sock = mock_sock

        messages = listener.poll()
        assert messages == []

    @patch.object(SignalListener, "reconnect")
    def test_poll_reconnects_on_empty_data(self, mock_reconnect, listener):
        mock_sock = MagicMock()
        mock_sock.recv.return_value = b""
        listener._sock = mock_sock

        messages = listener.poll()
        assert messages == []
        mock_reconnect.assert_called_once()

    @patch.object(SignalListener, "reconnect")
    def test_poll_reconnects_on_os_error(self, mock_reconnect, listener):
        mock_sock = MagicMock()
        mock_sock.recv.side_effect = OSError("connection reset")
        listener._sock = mock_sock

        messages = listener.poll()
        assert messages == []
        mock_reconnect.assert_called_once()

    @patch.object(SignalListener, "connect")
    def test_poll_auto_connects_if_no_socket(self, mock_connect, listener):
        mock_connect.side_effect = lambda: setattr(listener, "_sock", MagicMock(
            recv=MagicMock(side_effect=socket.timeout)
        ))

        listener.poll()
        mock_connect.assert_called_once()

    def test_poll_handles_partial_buffer(self, listener):
        """Simulate data arriving in two chunks — first half, then second half."""
        msg = _make_rpc_message("48.5 39.8 tank")
        half = len(msg) // 2

        mock_sock = MagicMock()
        # First call: partial data (no newline yet)
        mock_sock.recv.return_value = msg[:half].encode("utf-8")
        listener._sock = mock_sock

        messages = listener.poll()
        assert messages == []  # no complete line yet

        # Second call: rest of data + newline
        mock_sock.recv.return_value = (msg[half:] + "\n").encode("utf-8")
        messages = listener.poll()
        assert len(messages) == 1
        assert messages[0]["text"] == "48.5 39.8 tank"

    def test_poll_skips_envelope_without_data_message(self, listener):
        rpc = json.dumps({
            "jsonrpc": "2.0",
            "method": "receive",
            "params": {
                "envelope": {
                    "sourceNumber": "+1",
                    "receiptMessage": {"type": "DELIVERY"},
                }
            },
        }) + "\n"
        mock_sock = MagicMock()
        mock_sock.recv.return_value = rpc.encode("utf-8")
        listener._sock = mock_sock

        messages = listener.poll()
        assert messages == []


class TestSignalListenerParse:
    def test_parse_delegates_to_helper(self, listener):
        result = listener.parse("48.5 39.8 tank")
        assert result == (48.5, 39.8, "tank")

    def test_parse_returns_none_for_invalid(self, listener):
        assert listener.parse("hello") is None
