"""Tests for BLE classification."""

from custom_components.fan_ble_home.classifier import CandidateClassifier, CandidateStatus, CandidateEvidence

def test_classifier_no_metadata():
    res = CandidateClassifier.process({}, {}, None)
    assert res["status"] == CandidateStatus.UNKNOWN.value
    assert res["evidence"] == CandidateEvidence.METADATA_ONLY.value

def test_classifier_metadata_only():
    res = CandidateClassifier.process({1: b'\x00'}, {}, None)
    assert res["status"] == CandidateStatus.UNKNOWN.value
    assert res["evidence"] == CandidateEvidence.METADATA_ONLY.value

def test_classifier_raw_known_signature():
    raw = b"\x48\x46\x4B\x4A\x01\x02"
    res = CandidateClassifier.process({1: raw}, {}, raw)
    assert res["status"] == CandidateStatus.CANDIDATE_WITH_KNOWN_SIGNATURE.value
    assert res["candidate_type"] == "zhimei_v1_family_candidate"
    assert res["evidence"] == CandidateEvidence.RAW_SIGNATURE.value
    assert res["confidence"] == "medium"

def test_classifier_raw_unknown():
    raw = b"\x01\x02\x03"
    res = CandidateClassifier.process({1: raw}, {}, raw)
    assert res["status"] == CandidateStatus.UNKNOWN.value
    assert res["candidate_type"] == "unknown"
