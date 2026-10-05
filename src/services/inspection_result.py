"""
Public inspection result.

Defines the small, stable response returned by the application
service layer.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class InspectionResult:
    """
    Public result returned after an inspection.
    """

    success: bool

    session_id: Optional[str]

    coverage_complete: bool

    damage_results_available: bool

    vehicle_part_results_available: bool

    json_report_path: Optional[str]

    pdf_report_path: Optional[str]

    error: Optional[str] = None

    # Keep the original inspection available internally for now.
    # This will help us transition safely from Phase 1.
    inspection: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to a JSON-friendly dictionary.
        """

        return {
            "success": self.success,
            "session_id": self.session_id,
            "coverage_complete": (
                self.coverage_complete
            ),
            "damage_results_available": (
                self.damage_results_available
            ),
            "vehicle_part_results_available": (
                self.vehicle_part_results_available
            ),
            "json_report_path": (
                self.json_report_path
            ),
            "pdf_report_path": (
                self.pdf_report_path
            ),
            "error": self.error,
        }
