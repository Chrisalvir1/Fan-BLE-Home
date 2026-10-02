"""Passive BLE observation classifier and filters."""

from enum import Enum
from typing import Any

class CandidateEvidence(str, Enum):
    METADATA_ONLY = "metadata_only"
    RAW_SIGNATURE = "raw_signature"

class CandidateStatus(str, Enum):
    UNKNOWN = "unknown"
    CANDIDATE = "candidate"
    CANDIDATE_WITH_KNOWN_SIGNATURE = "candidate_with_known_signature"

class Sensitivity(str, Enum):
    STRICT = "strict"
    RESEARCH = "research"

class MetadataCandidateFilter:
    """Filters traffic based on metadata presence without building raw packets."""

    @staticmethod
    def evaluate(manufacturer_data: dict[int, bytes], service_data: dict[str, bytes]) -> bool:
        """Return True if metadata suggests it could be worth aggregating."""
        return bool(manufacturer_data or service_data)


class RawAdvertisementAnalyzer:
    """Analyzes raw bytes natively if provided by the adapter."""

    # ZhiMei v1 family known header
    ZHIMEI_V1_HEADER = b"\x48\x46\x4B\x4A"

    @staticmethod
    def analyze(raw_payload: bytes | None) -> tuple[CandidateStatus, str, str]:
        """Examine raw payload without making identity claims."""
        if not raw_payload:
            return (
                CandidateStatus.UNKNOWN,
                "unknown",
                "Home Assistant provided metadata only. No raw packet was available, so protocol classification was intentionally not attempted."
            )
        
        idx = 0
        while idx < len(raw_payload):
            length = raw_payload[idx]
            if length == 0 or idx + 1 + length > len(raw_payload):
                break
            ad_type = raw_payload[idx + 1]
            ad_data = raw_payload[idx + 2 : idx + 1 + length]
            
            # AD Type 0xFF is Manufacturer Specific Data
            if ad_type == 0xFF:
                if ad_data.startswith(RawAdvertisementAnalyzer.ZHIMEI_V1_HEADER):
                    return (
                        CandidateStatus.CANDIDATE_WITH_KNOWN_SIGNATURE,
                        "zhimei_v1_family_candidate",
                        "Observed a known reference header at correct offset in a native raw advertisement. This does not identify a physical fan, confirm the app, decode commands, or establish control compatibility."
                    )
            idx += 1 + length
            
        return (
            CandidateStatus.UNKNOWN,
            "unknown",
            "Raw payload available but no known signature was matched."
        )

class CandidateClassifier:
    """Main classifier combining filters and analyzers."""
    
    @staticmethod
    def process(
        manufacturer_data: dict[int, bytes], 
        service_data: dict[str, bytes], 
        raw_payload: bytes | None
    ) -> dict[str, Any]:
        """Process an advertisement and classify it."""
        
        has_metadata = MetadataCandidateFilter.evaluate(manufacturer_data, service_data)
        
        if raw_payload:
            status, ctype, expl = RawAdvertisementAnalyzer.analyze(raw_payload)
            evidence = CandidateEvidence.RAW_SIGNATURE.value if status != CandidateStatus.UNKNOWN else CandidateEvidence.METADATA_ONLY.value
            confidence = "medium" if status == CandidateStatus.CANDIDATE_WITH_KNOWN_SIGNATURE else "low"
            return {
                "status": status.value,
                "candidate_type": ctype,
                "evidence": evidence,
                "confidence": confidence,
                "raw_available": True,
                "explanation": expl
            }

        # If no native raw is available, we NEVER synthesize it.
        # Metadata check only produces unknown in Phase 2 because we don't have metadata signatures validated.
        expl = "Home Assistant provided metadata only. No raw packet was available, so protocol classification was intentionally not attempted."
        if not has_metadata:
            expl = "No relevant metadata found and no raw data available."

        return {
            "status": CandidateStatus.UNKNOWN.value,
            "candidate_type": "unknown",
            "evidence": CandidateEvidence.METADATA_ONLY.value,
            "confidence": "low",
            "raw_available": False,
            "explanation": expl
        }
