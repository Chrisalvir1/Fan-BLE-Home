"""Tests for BLE classification."""

from custom_components.fan_ble_home.classifier import CandidateClassifier, CandidateStatus, CandidateEvidence

def test_classifier_no_metadata():
    """Ensure it returns unknown when nothing is provided."""
    res = CandidateClassifier.process({}, {}, None)
    assert res["status"] == CandidateStatus.UNKNOWN.value
    assert res["evidence"] == CandidateEvidence.METADATA_ONLY.value
    assert res["raw_available"] is False

def test_classifier_metadata_only_header():
    """Ensure it returns unknown even if metadata contains the header, without raw bytes."""
    header = b"\x48\x46\x4B\x4A"
    res = CandidateClassifier.process({1: header}, {}, None)
    assert res["status"] == CandidateStatus.UNKNOWN.value
    assert res["evidence"] == CandidateEvidence.METADATA_ONLY.value
    assert res["raw_available"] is False
    assert res["confidence"] == "low"

def test_classifier_raw_known_signature():
    """Ensure it properly parses basic AD structure and finds the signature."""
    # Length 5, Type 0xFF (255), Data 48 46 4B 4A
    raw = bytes([0x05, 0xFF, 0x48, 0x46, 0x4B, 0x4A])
    res = CandidateClassifier.process({1: b'\x48\x46\x4B\x4A'}, {}, raw)
    assert res["status"] == CandidateStatus.CANDIDATE_WITH_KNOWN_SIGNATURE.value
    assert res["candidate_type"] == "zhimei_v1_family_candidate"
    assert res["evidence"] == CandidateEvidence.RAW_SIGNATURE.value
    assert res["raw_available"] is True
    assert res["confidence"] == "medium"

def test_classifier_raw_unknown():
    """Ensure it returns unknown if raw is available but no signature matches."""
    raw = bytes([0x02, 0xFF, 0x01])
    res = CandidateClassifier.process({1: b'\x01'}, {}, raw)
    assert res["status"] == CandidateStatus.UNKNOWN.value
    assert res["candidate_type"] == "unknown"
    assert res["raw_available"] is True
