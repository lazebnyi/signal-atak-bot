import socket
from unittest.mock import MagicMock, patch

import pytest

from services.tak_sender import TAKSender


@pytest.fixture
def tcp_sender():
    return TAKSender(host="127.0.0.1", port=9999, use_ssl=False)


@pytest.fixture
def ssl_sender():
    return TAKSender(
        host="127.0.0.1",
        port=9999,
        use_ssl=True,
        ssl_cert="/fake/cert.pem",
        ssl_key="/fake/key.pem",
        ssl_ca="/fake/ca.pem",
    )


class TestTAKSenderInit:
    def test_defaults(self):
        sender = TAKSender()
        assert sender.use_ssl is True

    def test_custom_params(self, tcp_sender):
        assert tcp_sender.host == "127.0.0.1"
        assert tcp_sender.port == 9999
        assert tcp_sender.use_ssl is False


class TestTAKSenderTCP:
    @patch("services.tak_sender.socket.socket")
    def test_send_tcp_success(self, mock_socket_cls, tcp_sender):
        mock_sock = MagicMock()
        mock_socket_cls.return_value.__enter__ = MagicMock(return_value=mock_sock)
        mock_socket_cls.return_value.__exit__ = MagicMock(return_value=False)

        result = tcp_sender.send("<event/>")

        assert result is True
        mock_sock.connect.assert_called_once_with(("127.0.0.1", 9999))
        mock_sock.sendall.assert_called_once_with(b"<event/>")

    @patch("services.tak_sender.socket.socket")
    def test_send_tcp_connection_refused(self, mock_socket_cls, tcp_sender):
        mock_sock = MagicMock()
        mock_sock.connect.side_effect = ConnectionRefusedError
        mock_socket_cls.return_value.__enter__ = MagicMock(return_value=mock_sock)
        mock_socket_cls.return_value.__exit__ = MagicMock(return_value=False)

        result = tcp_sender.send("<event/>")
        assert result is False

    @patch("services.tak_sender.socket.socket")
    def test_send_tcp_timeout(self, mock_socket_cls, tcp_sender):
        mock_sock = MagicMock()
        mock_sock.connect.side_effect = socket.timeout
        mock_socket_cls.return_value.__enter__ = MagicMock(return_value=mock_sock)
        mock_socket_cls.return_value.__exit__ = MagicMock(return_value=False)

        result = tcp_sender.send("<event/>")
        assert result is False


class TestTAKSenderSSL:
    @patch("services.tak_sender.ssl.SSLContext")
    @patch("services.tak_sender.socket.socket")
    def test_send_ssl_success(self, mock_socket_cls, mock_ctx_cls, ssl_sender):
        mock_ctx = MagicMock()
        mock_ctx_cls.return_value = mock_ctx
        mock_ssock = MagicMock()
        mock_sock = MagicMock()
        mock_socket_cls.return_value.__enter__ = MagicMock(return_value=mock_sock)
        mock_socket_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_ctx.wrap_socket.return_value.__enter__ = MagicMock(return_value=mock_ssock)
        mock_ctx.wrap_socket.return_value.__exit__ = MagicMock(return_value=False)

        result = ssl_sender.send("<event/>")

        assert result is True
        mock_ctx.load_cert_chain.assert_called_once_with(
            certfile="/fake/cert.pem", keyfile="/fake/key.pem"
        )
        mock_ssock.connect.assert_called_once_with(("127.0.0.1", 9999))
        mock_ssock.sendall.assert_called_once_with(b"<event/>")

    @patch("services.tak_sender.ssl.SSLContext")
    @patch("services.tak_sender.socket.socket")
    def test_send_ssl_connection_refused(self, mock_socket_cls, mock_ctx_cls, ssl_sender):
        mock_ctx = MagicMock()
        mock_ctx_cls.return_value = mock_ctx
        mock_ssock = MagicMock()
        mock_ssock.connect.side_effect = ConnectionRefusedError
        mock_sock = MagicMock()
        mock_socket_cls.return_value.__enter__ = MagicMock(return_value=mock_sock)
        mock_socket_cls.return_value.__exit__ = MagicMock(return_value=False)
        mock_ctx.wrap_socket.return_value.__enter__ = MagicMock(return_value=mock_ssock)
        mock_ctx.wrap_socket.return_value.__exit__ = MagicMock(return_value=False)

        result = ssl_sender.send("<event/>")
        assert result is False

    def test_send_dispatches_to_ssl(self, ssl_sender):
        with patch.object(ssl_sender, "_send_ssl", return_value=True) as mock:
            ssl_sender.send("<event/>")
            mock.assert_called_once_with("<event/>")

    def test_send_dispatches_to_tcp(self, tcp_sender):
        with patch.object(tcp_sender, "_send_tcp", return_value=True) as mock:
            tcp_sender.send("<event/>")
            mock.assert_called_once_with("<event/>")
