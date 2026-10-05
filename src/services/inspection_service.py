import os
from typing import Any

from app import run_inspection

from src.services.inspection_result import InspectionResult
from src.services.logging_service import setup_logging


class InspectionService:
    """
    Application service for vehicle inspections.

    Responsibilities:
        - Validate inspection input.
        - Execute the existing Phase 1 inspection pipeline.
        - Convert pipeline output into InspectionResult.
        - Handle pipeline failures.
        - Log inspection lifecycle events.

    This service does NOT:
        - manage asynchronous jobs
        - create job IDs
        - manage job status
        - start background workers
        - contain FastAPI routes

    Asynchronous job management belongs to InspectionRunner.
    """

    def __init__(self):
        """
        Initialize the inspection service.
        """

        self.logger = setup_logging()

    # ==================================================================
    # PUBLIC API
    # ==================================================================

    def inspect(
        self,
        video_path: str,
    ) -> InspectionResult:
        """
        Run one complete vehicle inspection.

        This method is synchronous by design.

        InspectionRunner is responsible for executing this method
        asynchronously.

        Args:
            video_path:
                Path to the inspection video.

        Returns:
            InspectionResult.
        """

        # --------------------------------------------------------------
        # Validate input
        # --------------------------------------------------------------

        validation_error = (
            self._validate_video_path(
                video_path
            )
        )

        if validation_error is not None:

            self.logger.error(
                validation_error
            )

            return self._failure_result(
                validation_error
            )

        video_path = os.path.abspath(
            str(video_path)
        )

        # --------------------------------------------------------------
        # Start inspection
        # --------------------------------------------------------------

        self.logger.info(
            "Starting inspection."
        )

        self.logger.info(
            "Input video: %s",
            video_path,
        )

        # --------------------------------------------------------------
        # Execute existing Phase 1 pipeline
        # --------------------------------------------------------------

        try:

            inspection = run_inspection(
                video_path
            )

        except Exception as exc:

            self.logger.exception(
                "Inspection pipeline failed."
            )

            return self._failure_result(
                f"{type(exc).__name__}: {exc}"
            )

        # --------------------------------------------------------------
        # Validate pipeline output
        # --------------------------------------------------------------

        if not isinstance(
            inspection,
            dict,
        ):

            error = (
                "Inspection pipeline returned "
                "an invalid result."
            )

            self.logger.error(
                error
            )

            return self._failure_result(
                error
            )

        # --------------------------------------------------------------
        # Convert pipeline output
        # --------------------------------------------------------------

        result = self._build_result(
            inspection
        )

        # --------------------------------------------------------------
        # Completion logging
        # --------------------------------------------------------------

        self.logger.info(
            "Inspection completed."
        )

        self.logger.info(
            "Session ID: %s",
            result.session_id,
        )

        self.logger.info(
            "Coverage complete: %s",
            result.coverage_complete,
        )

        self.logger.info(
            "Damage results available: %s",
            result.damage_results_available,
        )

        self.logger.info(
            "Vehicle-part results available: %s",
            result.vehicle_part_results_available,
        )

        self.logger.info(
            "JSON report: %s",
            result.json_report_path,
        )

        self.logger.info(
            "PDF report: %s",
            result.pdf_report_path,
        )

        return result

    # ==================================================================
    # INPUT VALIDATION
    # ==================================================================

    @staticmethod
    def _validate_video_path(
        video_path: str,
    ) -> str | None:
        """
        Validate the inspection video path.

        Returns:
            None when valid.
            Error message when invalid.
        """

        if not video_path:

            return (
                "video_path is required."
            )

        try:

            path = os.path.abspath(
                str(video_path)
            )

        except Exception as exc:

            return (
                "Invalid video_path: "
                f"{type(exc).__name__}: {exc}"
            )

        if not os.path.isfile(path):

            return (
                "Inspection video not found: "
                f"{path}"
            )

        return None

    # ==================================================================
    # RESULT CONVERSION
    # ==================================================================

    def _build_result(
        self,
        inspection: dict[str, Any],
    ) -> InspectionResult:
        """
        Convert the internal Phase 1 inspection dictionary into
        the stable public InspectionResult.
        """

        session_id = inspection.get(
            "session_id"
        )

        coverage_complete = bool(
            inspection.get(
                "coverage_complete",
                False,
            )
        )

        damages = inspection.get(
            "damages",
            {}
        )

        vehicle_parts = inspection.get(
            "vehicle_parts",
            {}
        )

        damage_results_available = bool(
            damages
        )

        vehicle_part_results_available = bool(
            vehicle_parts
        )

        # --------------------------------------------------------------
        # Extract report paths
        # --------------------------------------------------------------

        json_report_path = (
            self._extract_report_path(
                inspection,
                "final_report_export",
            )
        )

        pdf_report_path = (
            self._extract_report_path(
                inspection,
                "final_report_pdf",
            )
        )

        return InspectionResult(
            success=True,
            session_id=session_id,
            coverage_complete=coverage_complete,
            damage_results_available=(
                damage_results_available
            ),
            vehicle_part_results_available=(
                vehicle_part_results_available
            ),
            json_report_path=json_report_path,
            pdf_report_path=pdf_report_path,
            inspection=inspection,
        )

    # ==================================================================
    # REPORT PATH EXTRACTION
    # ==================================================================

    @staticmethod
    def _extract_report_path(
        inspection: dict[str, Any],
        field_name: str,
    ) -> str | None:
        """
        Extract a generated report path from the inspection dictionary.

        Expected structure:

            inspection[field_name] = {
                "path": "..."
            }
        """

        report_data = inspection.get(
            field_name,
            {}
        )

        if not isinstance(
            report_data,
            dict,
        ):
            return None

        path = report_data.get(
            "path"
        )

        if not path:
            return None

        return os.path.abspath(
            str(path)
        )

    # ==================================================================
    # FAILURE RESULT
    # ==================================================================

    @staticmethod
    def _failure_result(
        error: str,
    ) -> InspectionResult:
        """
        Create a consistent failed inspection result.
        """

        return InspectionResult(
            success=False,
            session_id=None,
            coverage_complete=False,
            damage_results_available=False,
            vehicle_part_results_available=False,
            json_report_path=None,
            pdf_report_path=None,
            error=error,
        )
