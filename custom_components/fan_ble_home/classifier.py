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
        """Return True if metadata suggests it could be a candidate."""
        # For Phase 2, we loosely accept anything with manufacturer data as potential in research mode,
        # but the real check happens if we have raw bytes.
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
        
        # Check for ZhiMei v1 signature anywhere in the raw payload or specifically at start
        if RawAdvertisementAnalyzer.ZHIMEI_V1_HEADER in raw_payload:
            return (
                CandidateStatus.CANDIDATE_WITH_KNOWN_SIGNATURE,
                "zhimei_v1_family_candidate",
                "Observed a known reference header in a native raw advertisement. This does not identify a physical fan, confirm the app, decode commands, or establish control compatibility."
            )
            
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
        
        # Metadata check
        has_potential = MetadataCandidateFilter.evaluate(manufacturer_data, service_data)
        if not has_potential:
            return {
                "status": CandidateStatus.UNKNOWN.value,
                "candidate_type": "unknown",
                "evidence": CandidateEvidence.METADATA_ONLY.value,
                "confidence": "low",
                "raw_available": bool(raw_payload),
                "explanation": "No relevant metadata found."
            }

        # Raw check
        if raw_payload:
            status, ctype, expl = RawAdvertisementAnalyzer.analyze(raw_payload)
            evidence = CandidateEvidence.RAW_SIGNATURE.value if status != CandidateStatus.UNKNOWN else CandidateEvidence.METADATA_ONLY.value
            confidence = "medium" if status == CandidateStatus.CANDIDATE_WITH_KNOWN_SIGNATURE else "low"
        else:
            # Maybe the manufacturer data itself starts with the signature?
            # HA exposes manufacturer_data as { company_identifier: payload }
            # If the payload contains the header, we can loosely classify it, but the prompt says:
            # "Prefijos conocidos solo cuando la fuente exponga bytes confiables... Nunca reconstruyas un paquete raw combinando..."
            # Wait, if manufacturer_data has it, is it raw? 
            # The prompt says: "RawAdvertisementAnalyzer: Solo opera si el callback entrega explícitamente bytes raw originales."
            # So if we don't have raw, we return unknown.
            status = CandidateStatus.UNKNOWN
            ctype = "unknown"
            evidence = CandidateEvidence.METADATA_ONLY.value
            confidence = "low"
            expl = "Home Assistant provided metadata only. No raw packet was available, so protocol classification was intentionally not attempted."

        return {
            "status": status.value,
            "candidate_type": ctype,
            "evidence": evidence,
            "confidence": confidence,
            "raw_available": bool(raw_payload),
            "explanation": expl
        }
