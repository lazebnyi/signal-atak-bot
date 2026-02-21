import xml.etree.ElementTree as ET
from datetime import datetime

import pytest

from services.cot_builder import CoTBuilder


@pytest.fixture
def builder():
    return CoTBuilder()


@pytest.fixture
def small_builder():
    """Builder with minimal target types for focused unit_tests."""
    return CoTBuilder(
        target_types={
            "vehicles": {"tank": "a-h-G-E-V-A"},
            "fallback": {"unknown": "a-u-G"},
        }
    )


class TestCoTBuilderInit:
    def test_flattens_nested_target_types(self, builder):
        assert "tank" in builder.target_types
        assert "infantry" in builder.target_types
        assert "helicopter" in builder.target_types
        # category keys should NOT be present
        assert "ground_vehicles" not in builder.target_types

    def test_correct_type_codes(self, builder):
        assert builder.target_types["tank"] == "a-h-G-E-V-A"
        assert builder.target_types["drone"] == "a-h-A-M-F-U"
        assert builder.target_types["unknown"] == "a-u-G"


class TestCoTBuilderBuild:
    def test_returns_valid_xml(self, builder):
        xml_str = builder.build(48.5, 39.8, "tank")
        root = ET.fromstring(xml_str)
        assert root.tag == "event"

    def test_event_attributes(self, builder):
        xml_str = builder.build(48.5, 39.8, "tank")
        root = ET.fromstring(xml_str)
        assert root.get("version") == "2.0"
        assert root.get("type") == "a-h-G-E-V-A"
        assert root.get("how") == "h-g-i-g-o"
        assert root.get("uid").startswith("signal-bot-")

    def test_point_element(self, builder):
        xml_str = builder.build(48.567, 39.879, "tank")
        root = ET.fromstring(xml_str)
        point = root.find("point")
        assert point is not None
        assert point.get("lat") == "48.567"
        assert point.get("lon") == "39.879"
        assert point.get("hae") == "0.0"
        assert point.get("ce") == "35.0"
        assert point.get("le") == "999999.0"

    def test_detail_contact(self, builder):
        xml_str = builder.build(48.5, 39.8, "tank")
        root = ET.fromstring(xml_str)
        contact = root.find("detail/contact")
        assert contact is not None
        callsign = contact.get("callsign")
        assert callsign.startswith("TANK-")

    def test_custom_callsign(self, builder):
        xml_str = builder.build(48.5, 39.8, "tank", callsign="ALPHA-1")
        root = ET.fromstring(xml_str)
        contact = root.find("detail/contact")
        assert contact.get("callsign") == "ALPHA-1"

    def test_remarks(self, builder):
        xml_str = builder.build(48.5, 39.8, "tank")
        root = ET.fromstring(xml_str)
        remarks = root.find("detail/remarks")
        assert remarks is not None
        assert "tank" in remarks.text
        assert "48.5" in remarks.text

    def test_unknown_target_gets_fallback_type(self, builder):
        xml_str = builder.build(48.5, 39.8, "ufo")
        root = ET.fromstring(xml_str)
        assert root.get("type") == "a-u-G"

    def test_case_insensitive_target(self, builder):
        xml_str = builder.build(48.5, 39.8, "Tank")
        root = ET.fromstring(xml_str)
        assert root.get("type") == "a-h-G-E-V-A"

    def test_stale_time_after_start(self, builder):
        xml_str = builder.build(48.5, 39.8, "tank")
        root = ET.fromstring(xml_str)
        start = datetime.strptime(root.get("start"), "%Y-%m-%dT%H:%M:%S.%fZ")
        stale = datetime.strptime(root.get("stale"), "%Y-%m-%dT%H:%M:%S.%fZ")
        assert stale > start
        diff = (stale - start).total_seconds()
        assert 55 <= diff <= 65

    def test_unique_uids(self, builder):
        xml1 = builder.build(48.5, 39.8, "tank")
        xml2 = builder.build(48.5, 39.8, "tank")
        root1 = ET.fromstring(xml1)
        root2 = ET.fromstring(xml2)
        assert root1.get("uid") != root2.get("uid")

    def test_precision_location(self, builder):
        xml_str = builder.build(48.5, 39.8, "tank")
        root = ET.fromstring(xml_str)
        precision = root.find("detail/precisionlocation")
        assert precision is not None
        assert precision.get("altsrc") == "DTED0"
