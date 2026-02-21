from core.helpers import extract_message, parse_coordinate


class TestParseCoordinate:
    def test_valid_message(self):
        result = parse_coordinate("48.567123 37.87897 tank")
        assert result == (48.567123, 37.87897, "tank")

    def test_negative_coordinates(self):
        result = parse_coordinate("-33.8688 151.2093 infantry")
        assert result == (-33.8688, 151.2093, "infantry")

    def test_multi_word_target(self):
        result = parse_coordinate("48.0 39.0 heavy tank")
        assert result == (48.0, 39.0, "heavy tank")

    def test_leading_trailing_whitespace(self):
        result = parse_coordinate("  48.5 39.8 truck  ")
        assert result == (48.5, 39.8, "truck")

    def test_integer_coordinates(self):
        result = parse_coordinate("48 39 apc")
        assert result == (48.0, 39.0, "apc")

    def test_lat_out_of_range(self):
        assert parse_coordinate("91.0 39.0 tank") is None

    def test_lat_negative_out_of_range(self):
        assert parse_coordinate("-91.0 39.0 tank") is None

    def test_lon_out_of_range(self):
        assert parse_coordinate("48.0 181.0 tank") is None

    def test_lon_negative_out_of_range(self):
        assert parse_coordinate("48.0 -181.0 tank") is None

    def test_missing_target(self):
        assert parse_coordinate("48.0 39.0") is None

    def test_missing_lon(self):
        assert parse_coordinate("48.0 tank") is None

    def test_empty_string(self):
        assert parse_coordinate("") is None

    def test_random_text(self):
        assert parse_coordinate("hello world") is None

    def test_boundary_lat_90(self):
        result = parse_coordinate("90.0 39.0 tank")
        assert result == (90.0, 39.0, "tank")

    def test_boundary_lon_180(self):
        result = parse_coordinate("48.0 180.0 ship")
        assert result == (48.0, 180.0, "ship")


class TestExtractMessage:
    def test_valid_envelope(self):
        envelope = {
            "sourceNumber": "+1234567890",
            "dataMessage": {
                "message": "48.5 39.8 tank",
                "timestamp": 1700000000,
            },
        }
        result = extract_message(envelope)
        assert result == {
            "sender": "+1234567890",
            "text": "48.5 39.8 tank",
            "timestamp": 1700000000,
        }

    def test_fallback_to_source_name(self):
        envelope = {
            "sourceName": "John",
            "dataMessage": {"message": "hello", "timestamp": 100},
        }
        result = extract_message(envelope)
        assert result["sender"] == "John"

    def test_fallback_to_source(self):
        envelope = {
            "source": "uuid-abc-123",
            "dataMessage": {"message": "hello", "timestamp": 100},
        }
        result = extract_message(envelope)
        assert result["sender"] == "uuid-abc-123"

    def test_fallback_to_unknown(self):
        envelope = {
            "dataMessage": {"message": "hello", "timestamp": 100},
        }
        result = extract_message(envelope)
        assert result["sender"] == "unknown"

    def test_no_data_message(self):
        assert extract_message({"sourceNumber": "+1"}) is None

    def test_empty_message_text(self):
        envelope = {
            "sourceNumber": "+1",
            "dataMessage": {"message": "", "timestamp": 100},
        }
        assert extract_message(envelope) is None

    def test_no_message_key(self):
        envelope = {
            "sourceNumber": "+1",
            "dataMessage": {"timestamp": 100},
        }
        assert extract_message(envelope) is None

    def test_empty_envelope(self):
        assert extract_message({}) is None

    def test_default_timestamp(self):
        envelope = {
            "sourceNumber": "+1",
            "dataMessage": {"message": "hi"},
        }
        result = extract_message(envelope)
        assert result["timestamp"] == 0
