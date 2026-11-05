"""Pipeline package for SentinelEdge."""

from src.pipeline.router import (
    PipelineResult,
    UnifiedPipeline,
    analyze,
    detect_input_type,
)

__all__ = [
    "PipelineResult",
    "UnifiedPipeline",
    "analyze",
    "detect_input_type",
]
