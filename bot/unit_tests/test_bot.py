from unittest.mock import MagicMock, patch

import pytest

from core.helpers import parse_coordinate
from main import SignalCoTBot


@pytest.fixture
def bot():
    mock_listener = MagicMock()
    mock_listener.parse = staticmethod(parse_coordinate)

    with patch("main.SignalListener", return_value=mock_listener), \
         patch("main.TAKSender") as mock_sender_cls, \
         patch("main.CoTBuilder") as mock_builder_cls:
        mock_sender = MagicMock()
        mock_sender.send.return_value = True
        mock_sender_cls.return_value = mock_sender

        mock_builder = MagicMock()
        mock_builder.build.return_value = "<event/>"
        mock_builder_cls.return_value = mock_builder

        b = SignalCoTBot()
        yield b


class TestProcessMessage:
    def test_valid_coordinate_message(self, bot):
        result = bot.process_message("48.5 39.8 tank", "+1234567890")

        assert result is True
        bot.builder.build.assert_called_once_with(48.5, 39.8, "tank")
        bot.sender.send.assert_called_once_with("<event/>")

    def test_invalid_message_returns_false(self, bot):
        result = bot.process_message("hello world", "+1234567890")

        assert result is False
        bot.builder.build.assert_not_called()
        bot.sender.send.assert_not_called()

    def test_send_failure_returns_false(self, bot):
        bot.sender.send.return_value = False
        result = bot.process_message("48.5 39.8 tank", "+1")

        assert result is False

    def test_multi_word_target(self, bot):
        result = bot.process_message("48.5 39.8 heavy tank", "+1")

        assert result is True
        bot.builder.build.assert_called_once_with(48.5, 39.8, "heavy tank")
