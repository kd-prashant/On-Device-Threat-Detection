"""Base explainer interface, data contracts, and MITRE taxonomy.

Ensures all explanation engines (ExecuTorch Llama 3.2 runtime and deterministic
stand-in heuristic) provide a unified, typed explanation contract adhering to
PRD Section 9 safety rules.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MitreTechnique:
    """Mapping to industry-standard MITRE ATT&CK Mobile framework."""

    technique_id: str
    technique_name: str
    tactic: str
    reference_url: str


@dataclass
class ExplanationResult:
    """Structured, verifiable threat explanation and defensive guidance.

    Attributes:
        verdict: Human-readable threat verdict ('PHISHING', 'SCAM', etc.).
        is_threat: Boolean indicator matching detector verdict.
        confidence_pct: Confidence percentage string (e.g. '98.5%').
        confidence_score: Raw float confidence between 0.0 and 1.0.
        reasoning: Plain-English explanation of why this was flagged.
        recommended_actions: 3 concrete, strictly defensive user steps.
        mitre_attack: Optional MITRE ATT&CK technique mapping.
        adversarial_guardrail_triggered: True if injection was neutralized.
        latency_ms: Time taken to construct the explanation in ms.
        metadata: Additional diagnostic signals (e.g. extracted tokens).
    """

    verdict: str
    is_threat: bool
    confidence_pct: str
    confidence_score: float
    reasoning: str
    recommended_actions: list[str]
    mitre_attack: MitreTechnique | None = None
    adversarial_guardrail_triggered: bool = False
    latency_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class BaseExplainer(ABC):
    """Abstract contract for on-device threat explanation engines."""

    @abstractmethod
    def explain(
        self,
        detection: Any,
        raw_input: Any,
    ) -> ExplanationResult:
        """Generate structured explanation and safe defensive recommendations.

        Args:
            detection: DetectionResult from a detector model.
            raw_input: Untrusted input payload (URL, SMS, or network flow).

        Returns:
            ExplanationResult with reasoning, actions, and safety audits.
        """
        pass
