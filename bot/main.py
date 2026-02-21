import logging

from services.cot_builder import CoTBuilder
from services.signal_listener import SignalListener
from services.tak_sender import TAKSender

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)


class SignalCoTBot:
    """Bridges Signal messages to CoT markers on a TAK network."""

    def __init__(self):
        self.log = logging.getLogger("signal-cot-bot")
        self.builder = CoTBuilder()
        self.sender = TAKSender()
        self.listener = SignalListener()

    def process_message(self, text: str, sender: str) -> bool:
        """Parse a message, build CoT XML, and send it to TAK."""
        parsed = self.listener.parse(text)
        if parsed is None:
            self.log.debug("Ignoring non-coordinate message from %s: %s", sender, text)
            return False

        lat, lon, target = parsed
        self.log.info("Target from %s: %s at (%f, %f)", sender, target, lat, lon)

        cot_xml = self.builder.build(lat, lon, target)
        return self.sender.send(cot_xml)

    def run(self):
        """Main loop — fetch Signal messages and forward to TAK."""

        self.log.info("Bot started.")
        self.log.info("Send a message like: 48.567123 37.87897 tank")
        self.listener.connect()

        try:
            while True:
                messages = self.listener.poll()
                for msg in messages:
                    self.log.info("Signal from %s: %s", msg["sender"], msg["text"])
                    self.process_message(msg["text"], msg["sender"])
        finally:
            self.listener.close()

def main():
    bot = SignalCoTBot()
    try:
        bot.run()
    except KeyboardInterrupt:
        bot.log.info("Shutting down.")


if __name__ == "__main__":
    main()
