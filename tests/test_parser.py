"""
Parser unit tests — pure stdlib logic, no YOLO/EasyOCR needed. Run: pytest tests/
"""

from app.services.parser_service import (
    clean_license_number,
    clean_person_name,
    parse_date,
    parse_owner_text,
    consolidate_owners,
    process_and_structure,
)


def test_clean_license_number():
    assert clean_license_number(" CN - 2883802 ") == "CN-2883802"
    assert clean_license_number("cn 2477716") == "CN-2477716"


def test_clean_person_name():
    assert clean_person_name("NAJLA  ANTAR  ALJABERI 100%") == "NAJLA ANTAR ALJABERI"
    assert clean_person_name("JOHN DOE Owner") == "JOHN DOE"


def test_parse_date():
    assert parse_date("25/12/2024") == "25-12-2024"
    assert parse_date("14.10.2019") == "14-10-2019"
    assert parse_date("not a date") is None
    assert parse_date("99-99-2024") is None  # invalid date rejected


def test_parse_owner_text():
    owner = parse_owner_text("AHMED HASSAN MOHAMMED 50.0%")
    assert owner == {"name": "AHMED HASSAN MOHAMMED", "share_percentage": "50.0%"}

    # missing percentage defaults to 100%
    assert parse_owner_text("JOHN DOE")["share_percentage"] == "100%"


def test_consolidate_owners_multiple():
    results = {
        "owner_1": {"text": "MOHAMMED JUMA ALKAABI 50%"},
        "owner_2": {"text": "AHMED HASSAN MOHAMMED 50%"},
        "license_number": {"text": "CN-1"},
    }
    owners = consolidate_owners(results)
    assert [o["name"] for o in owners] == ["MOHAMMED JUMA ALKAABI", "AHMED HASSAN MOHAMMED"]


def test_process_and_structure_full():
    ocr_results = {
        "license_number": {"text": " CN - 2883802 "},
        "trade_name": {"text": "TIGER FIRE FOR SECURITY SYSTEM"},
        "establishment_date": {"text": "14/10/2019"},
        "expiry_date": {"text": "25-12-2024"},
        "owner": {"text": "NAJLA ANTAR ABDULLA ALJABERI 100%"},
        "manager": {"text": "NAJLA ANTAR ABDULLA ALJABERI"},
    }
    out = process_and_structure(ocr_results)

    assert out["license_number"] == "CN-2883802"
    assert out["company_name"] == "TIGER FIRE FOR SECURITY SYSTEM"
    assert out["establishment_date"] == "14-10-2019"
    assert out["expiry_date"] == "25-12-2024"
    assert out["owners"] == [
        {"name": "NAJLA ANTAR ABDULLA ALJABERI", "share_percentage": "100%"}
    ]
    # expired license surfaces a warning, not a hard error
    assert out["validation"]["is_valid"] is True
    assert any("expired" in w for w in out["validation"]["warnings"])


def test_process_and_structure_missing_license_is_error():
    out = process_and_structure({"company_name": {"text": "TEST LLC"}})
    assert out["validation"]["is_valid"] is False
    assert "License number is missing" in out["validation"]["errors"]
    # no crash on unexpected/missing keys either
    assert out["company_name"] == "TEST LLC"
