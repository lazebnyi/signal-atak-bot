import uuid
import xml.etree.ElementTree as ET
from datetime import UTC, datetime, timedelta

from core.config import (
    COT_DEFAULT_CE,
    COT_DEFAULT_HAE,
    COT_DEFAULT_LE,
    COT_HOW,
    COT_STALE_MINUTES,
    TARGET_TYPES,
)

TIME_FMT = "%Y-%m-%dT%H:%M:%S.%fZ"


class CoTBuilder:
    def __init__(
        self,
        target_types: dict[str, dict[str, str]] = TARGET_TYPES,
        stale_minutes: int = COT_STALE_MINUTES,
        how: str = COT_HOW,
        hae: float = COT_DEFAULT_HAE,
        ce: float = COT_DEFAULT_CE,
        le: float = COT_DEFAULT_LE,
    ):
        self.target_types = {
            keyword: code
            for group in target_types.values()
            for keyword, code in group.items()
        }
        self.stale_minutes = stale_minutes
        self.how = how
        self.hae = hae
        self.ce = ce
        self.le = le

    def build(
        self,
        lat: float,
        lon: float,
        target: str,
        callsign: str | None = None,
    ) -> str:
        """Builds CoT XML target report from lat, lon, target and callsign also could be specified."""
        now = datetime.now(UTC)
        stale = now + timedelta(minutes=self.stale_minutes)

        uid = f"signal-bot-{uuid.uuid4()}"
        cot_type = self.target_types.get(target.lower(), self.target_types["unknown"])
        callsign = callsign or f"{target.upper()}-{uid[-4:]}"

        event = ET.Element("event")
        event.set("version", "2.0")
        event.set("uid", uid)
        event.set("type", cot_type)
        event.set("how", self.how)
        event.set("time", now.strftime(TIME_FMT))
        event.set("start", now.strftime(TIME_FMT))
        event.set("stale", stale.strftime(TIME_FMT))

        point = ET.SubElement(event, "point")
        point.set("lat", str(lat))
        point.set("lon", str(lon))
        point.set("hae", str(self.hae))
        point.set("ce", str(self.ce))
        point.set("le", str(self.le))

        detail = ET.SubElement(event, "detail")

        contact = ET.SubElement(detail, "contact")
        contact.set("callsign", callsign)

        remarks = ET.SubElement(detail, "remarks")
        remarks.text = f"Signal-ATAK bot: {target} at {lat}, {lon}"

        precision = ET.SubElement(detail, "precisionlocation")
        precision.set("altsrc", "DTED0")

        return ET.tostring(event, encoding="unicode", xml_declaration=True)
