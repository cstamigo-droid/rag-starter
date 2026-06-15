"""The single return type every module and tool produces (reused from mcp-factory).

A uniform shape lets an LLM reason across heterogeneous tools without each one
inventing its own format. Plain-data tools fill `summary` + `data`. Analysis
tools additionally set `score` (-100..+100) and `confidence` (0..1).
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


def clamp(x: float, lo: float, hi: float) -> float:
    """Constrain x to the inclusive [lo, hi] range."""
    return max(lo, min(hi, x))


@dataclass
class Result:
    """Uniform result object.

    Attributes:
        source:     short id of the producing module, e.g. "retrieve".
        ok:         True if the operation succeeded and the result is meaningful.
        summary:    one-line human-readable takeaway.
        data:       raw structured details (module-specific). Put citations here.
        score:      optional -100..+100 directional score (analysis only).
        confidence: optional 0..1 — how much to trust this result.
        error:      failure reason when ok is False; None otherwise.
    """

    source: str
    ok: bool
    summary: str = ""
    data: dict[str, Any] = field(default_factory=dict)
    score: float | None = None
    confidence: float | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def failed(cls, source: str, error: str) -> "Result":
        """Graceful degradation: a failure NEVER fabricates a value."""
        return cls(source=source, ok=False, summary=f"no data ({error})", error=error)
