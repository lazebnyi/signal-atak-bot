"""Shared helpers for parsing Signal messages and coordinates."""

import logging
import re

log = logging.getLogger(__name__)

COORD_PATTERN = re.compile(
    r"^\s*(-?\d{1,3}(?:\.\d+)?)\s+(-?\d{1,3}(?:\.\d+)?)\s+(.+?)\s*$"
)


def parse_coordinate(text: str) -> tuple[float, float, str] | None:
    """
    Parse a coordinate message: "LAT LON target".

    Returns (lat, lon, target) or None if invalid.
    """

    match = COORD_PATTERN.match(text)
    if not match:
        return None

    lat = float(match.group(1))
    lon = float(match.group(2))
    target = match.group(3).strip()

    if not (-90 <= lat <= 90):
        log.warning("Latitude %f out of range [-90, 90]", lat)
        return None
    if not (-180 <= lon <= 180):
        log.warning("Longitude %f out of range [-180, 180]", lon)
        return None

    return lat, lon, target


def extract_message(envelope: dict) -> dict | None:
    """Extract sender/text/timestamp from a signal-cli envelope."""

    data_msg = envelope.get("dataMessage")
    if not data_msg or not data_msg.get("message"):
        return None

    sender = (
        envelope.get("sourceNumber")
        or envelope.get("sourceName")
        or envelope.get("source", "unknown")
    )
    return {
        "sender": sender,
        "text": data_msg["message"],
        "timestamp": data_msg.get("timestamp", 0),
    }
