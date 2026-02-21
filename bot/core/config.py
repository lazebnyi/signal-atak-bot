"""Configuration for Signal-to-CoT-to-TAK bot.

All settings can be overridden via environment variables (for Docker).
Defaults preserve local (non-Docker) behavior.
"""

import os

_base = os.path.dirname(os.path.abspath(__file__))

SIGNAL_NUMBER = os.environ.get("SIGNAL_NUMBER", "")
SIGNAL_CLI_HOST = os.environ.get("SIGNAL_CLI_HOST", "127.0.0.1")
SIGNAL_CLI_PORT = int(os.environ.get("SIGNAL_CLI_PORT", "7583"))

TAK_HOST = os.environ.get("TAK_HOST", "127.0.0.1")
TAK_PORT = int(os.environ.get("TAK_PORT", "8089"))
SSL_CERT = os.environ.get("SSL_CERT", os.path.join(_base, "certs", "bot-cert.pem"))
SSL_KEY = os.environ.get("SSL_KEY", os.path.join(_base, "certs", "bot-key.pem"))
SSL_CA = os.environ.get("SSL_CA", os.path.join(_base, "certs", "ca.pem"))

COT_STALE_MINUTES = int(os.environ.get("COT_STALE_MINUTES", "1"))
COT_HOW = os.environ.get("COT_HOW", "h-g-i-g-o")
COT_DEFAULT_HAE = float(os.environ.get("COT_DEFAULT_HAE", "0.0"))
COT_DEFAULT_CE = float(os.environ.get("COT_DEFAULT_CE", "35.0"))
COT_DEFAULT_LE = float(os.environ.get("COT_DEFAULT_LE", "999999.0"))
TARGET_TYPES = {
    "ground_vehicles": {
        "tank": "a-h-G-E-V-A",
        "apc": "a-h-G-E-V-I",
        "truck": "a-h-G-E-V-C",
        "vehicle": "a-h-G-E-V",
    },
    "personnel": {
        "infantry": "a-h-G-U-C-I",
        "sniper": "a-h-G-U-C-I-s",
        "soldiers": "a-h-G-U-C-I",
    },
    "weapons": {
        "artillery": "a-h-G-E-W-H",
        "mortar": "a-h-G-E-W-M",
        "mlrs": "a-h-G-E-W-R",
        "sam": "a-h-G-E-W-A",
        "aa": "a-h-G-E-W-A",
    },
    "air": {
        "helicopter": "a-h-A-M-H",
        "drone": "a-h-A-M-F-U",
        "jet": "a-h-A-M-F",
        "aircraft": "a-h-A-M",
    },
    "naval": {
        "ship": "a-h-S",
        "boat": "a-h-S-C",
    },
    "structures": {
        "bunker": "a-h-G-I-B",
        "camp": "a-h-G-I",
        "hq": "a-h-G-I-H",
        "depot": "a-h-G-I-S",
    },
    "fallback": {
        "unknown": "a-u-G",
    },
}
