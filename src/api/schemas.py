from typing import Optional

from pydantic import BaseModel, Field


# ============================================================
# Report links
# ============================================================

class ReportLinks(BaseModel):
    """
    Public URLs for generated inspection reports.
    """

    json_url: Optional[str] = None
    pdf_url: Optional[str] = None


# ============================================================
# Inspection result
# ============================================================

class InspectionResultResponse(BaseModel):
    """
    Public inspection result returned by the API.

    Internal pipeline data is intentionally excluded.
    """

    success: bool

    session_id: Optional[str] = None

    coverage_complete: bool = False

    damage_results_available: bool = False

    vehicle_part_results_available: bool = False

    json_report_path: Optional[str] = None

    pdf_report_path: Optional[str] = None

    error: Optional[str] = None


# ============================================================
# Inspection job response
# ============================================================

class InspectionJobResponse(BaseModel):
    """
    Public representation of an inspection job.
    """

    job_id: str

    status: str

    created_at: str

    started_at: Optional[str] = None

    completed_at: Optional[str] = None

    result: Optional[
        InspectionResultResponse
    ] = None

    reports: Optional[
        ReportLinks
    ] = None

    error: Optional[str] = None


# ============================================================
# Create inspection response
# ============================================================

class CreateInspectionResponse(BaseModel):
    """
    Response returned immediately after creating
    an asynchronous inspection job.
    """

    job_id: str

    status: str = Field(
        default="queued"
    )


# ============================================================
# Health response
# ============================================================

class HealthResponse(BaseModel):
    """
    API health response.
    """

    status: str

    service: str
