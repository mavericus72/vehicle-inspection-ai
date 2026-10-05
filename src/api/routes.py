from pathlib import Path
import shutil
import uuid

from fastapi import (
    APIRouter,
    BackgroundTasks,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.responses import (
    FileResponse,
    JSONResponse,
)

from src.services.inspection_runner import InspectionRunner

from src.config import (
    DATA_DIR,
)


# ============================================================
# Router
# ============================================================

router = APIRouter(
    prefix="/api/v1",
    tags=["inspections"],
)


# ============================================================
# Configuration
# ============================================================


UPLOAD_DIR = (
    DATA_DIR
    / "uploads"
)

# PROJECT_ROOT = Path(
#     "/content/drive/MyDrive/vehicle-inspection-ai"
# )
#
# UPLOAD_DIR = (
#     PROJECT_ROOT
#     / "data"
#     / "uploads"
# )

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# Inspection runner
# ============================================================

inspection_runner = InspectionRunner()


# ============================================================
# Health check
# ============================================================

@router.get("/health")
def health_check():
    """
    API health check.
    """

    return {
        "status": "healthy",
        "service": "vehicle-inspection-ai",
    }


# ============================================================
# Create inspection job
# ============================================================

@router.post(
    "/inspections",
    status_code=202,
)
def create_inspection(
    background_tasks: BackgroundTasks,
    video: UploadFile = File(...),
):
    """
    Upload a vehicle inspection video and create an
    asynchronous inspection job.

    The endpoint returns immediately with a job_id.
    """

    # --------------------------------------------------------
    # Validate filename
    # --------------------------------------------------------

    if not video.filename:

        raise HTTPException(
            status_code=400,
            detail="Video filename is required.",
        )

    # --------------------------------------------------------
    # Validate extension
    # --------------------------------------------------------

    allowed_extensions = {
        ".mp4",
        ".avi",
        ".mov",
        ".mkv",
    }

    extension = Path(
        video.filename
    ).suffix.lower()

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported video format: {extension}"
            ),
        )

    # --------------------------------------------------------
    # Generate server-side filename
    # --------------------------------------------------------

    file_id = uuid.uuid4().hex

    filename = (
        f"{file_id}{extension}"
    )

    video_path = (
        UPLOAD_DIR / filename
    )

    # --------------------------------------------------------
    # Save uploaded video
    # --------------------------------------------------------

    try:

        with video_path.open("wb") as buffer:

            shutil.copyfileobj(
                video.file,
                buffer,
            )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to save uploaded video: "
                f"{type(exc).__name__}: {exc}"
            ),
        )

    finally:

        try:
            video.file.close()
        except Exception:
            pass

    # --------------------------------------------------------
    # Create inspection job
    # --------------------------------------------------------

    try:

        job_id = (
            inspection_runner.create_job(
                str(video_path)
            )
        )

    except Exception as exc:

        try:
            video_path.unlink(
                missing_ok=True
            )
        except Exception:
            pass

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to create inspection job: "
                f"{type(exc).__name__}: {exc}"
            ),
        )

    # --------------------------------------------------------
    # Start job in background
    # --------------------------------------------------------

    background_tasks.add_task(
        inspection_runner.run_job,
        job_id,
    )

    # --------------------------------------------------------
    # Return immediately
    # --------------------------------------------------------

    return JSONResponse(
        status_code=202,
        content={
            "job_id": job_id,
            "status": "queued",
        },
    )


# ============================================================
# Get inspection job
# ============================================================

@router.get(
    "/inspections/{job_id}",
)
def get_inspection(
    job_id: str,
):
    """
    Return the current state of an inspection job.
    """

    job = (
        inspection_runner.get_job(
            job_id
        )
    )

    if job is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Inspection job not found: "
                f"{job_id}"
            ),
        )

    # --------------------------------------------------------
    # Build public response
    # --------------------------------------------------------

    result = job.get(
        "result"
    )

    response = {
        "job_id": job.get(
            "job_id"
        ),
        "status": job.get(
            "status"
        ),
        "created_at": job.get(
            "created_at"
        ),
        "started_at": job.get(
            "started_at"
        ),
        "completed_at": job.get(
            "completed_at"
        ),
        "result": result,
        "error": job.get(
            "error"
        ),
    }

    # --------------------------------------------------------
    # Add report URLs after completion
    # --------------------------------------------------------

    if (
        job.get("status") == "completed"
        and isinstance(result, dict)
    ):

        response["reports"] = {
            "json": (
                f"/api/v1/inspections/"
                f"{job_id}/report/json"
            ),
            "pdf": (
                f"/api/v1/inspections/"
                f"{job_id}/report/pdf"
            ),
        }

    return response


# ============================================================
# Internal helper — completed job
# ============================================================

def _get_completed_job(
    job_id: str,
):
    """
    Retrieve a job and ensure that it has completed.
    """

    job = (
        inspection_runner.get_job(
            job_id
        )
    )

    if job is None:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Inspection job not found: "
                f"{job_id}"
            ),
        )

    if job.get("status") != "completed":

        raise HTTPException(
            status_code=409,
            detail={
                "message": (
                    "Inspection is not completed."
                ),
                "job_id": job_id,
                "status": job.get(
                    "status"
                ),
            },
        )

    result = job.get(
        "result"
    )

    if not isinstance(
        result,
        dict,
    ):

        raise HTTPException(
            status_code=500,
            detail=(
                "Completed inspection does not "
                "contain a valid result."
            ),
        )

    return job, result


# ============================================================
# Download JSON report
# ============================================================

@router.get(
    "/inspections/{job_id}/report/json",
)
def get_json_report(
    job_id: str,
):
    """
    Download the final JSON inspection report.
    """

    _, result = _get_completed_job(
        job_id
    )

    report_path = result.get(
        "json_report_path"
    )

    if not report_path:

        raise HTTPException(
            status_code=404,
            detail=(
                "JSON inspection report is not available."
            ),
        )

    report_file = Path(
        report_path
    )

    if not report_file.is_file():

        raise HTTPException(
            status_code=404,
            detail=(
                "JSON inspection report file "
                "was not found."
            ),
        )

    return FileResponse(
        path=str(report_file),
        media_type="application/json",
        filename="final_inspection_report.json",
    )


# ============================================================
# Download PDF report
# ============================================================

@router.get(
    "/inspections/{job_id}/report/pdf",
)
def get_pdf_report(
    job_id: str,
):
    """
    Download the final PDF inspection report.
    """

    _, result = _get_completed_job(
        job_id
    )

    report_path = result.get(
        "pdf_report_path"
    )

    if not report_path:

        raise HTTPException(
            status_code=404,
            detail=(
                "PDF inspection report is not available."
            ),
        )

    report_file = Path(
        report_path
    )

    if not report_file.is_file():

        raise HTTPException(
            status_code=404,
            detail=(
                "PDF inspection report file "
                "was not found."
            ),
        )

    return FileResponse(
        path=str(report_file),
        media_type="application/pdf",
        filename="final_inspection_report.pdf",
    )










# from pathlib import Path
# import shutil
# import uuid
#
# from fastapi import (
#     APIRouter,
#     BackgroundTasks,
#     File,
#     HTTPException,
#     UploadFile,
# )
# from fastapi.responses import JSONResponse
#
# from src.services.inspection_runner import InspectionRunner
#
#
# # ============================================================
# # Router
# # ============================================================
#
# router = APIRouter(
#     prefix="/api/v1",
#     tags=["inspections"],
# )
#
#
# # ============================================================
# # Configuration
# # ============================================================
#
# PROJECT_ROOT = Path(
#     "/content/drive/MyDrive/vehicle-inspection-ai"
# )
#
# UPLOAD_DIR = (
#     PROJECT_ROOT
#     / "data"
#     / "uploads"
# )
#
# UPLOAD_DIR.mkdir(
#     parents=True,
#     exist_ok=True,
# )
#
#
# # ============================================================
# # Inspection runner
# # ============================================================
#
# inspection_runner = InspectionRunner()
#
#
# # ============================================================
# # Health check
# # ============================================================
#
# @router.get("/health")
# def health_check():
#     """
#     API health check.
#     """
#
#     return {
#         "status": "healthy",
#         "service": "vehicle-inspection-ai",
#     }
#
#
# # ============================================================
# # Create inspection job
# # ============================================================
#
# @router.post(
#     "/inspections",
#     status_code=202,
# )
# def create_inspection(
#     background_tasks: BackgroundTasks,
#     video: UploadFile = File(...),
# ):
#     """
#     Upload a vehicle inspection video and create an
#     asynchronous inspection job.
#
#     The endpoint does NOT wait for the computer-vision
#     pipeline to complete.
#
#     Returns:
#         202 Accepted with a job_id.
#     """
#
#     # --------------------------------------------------------
#     # Validate filename
#     # --------------------------------------------------------
#
#     if not video.filename:
#
#         raise HTTPException(
#             status_code=400,
#             detail="Video filename is required.",
#         )
#
#     # --------------------------------------------------------
#     # Validate extension
#     # --------------------------------------------------------
#
#     allowed_extensions = {
#         ".mp4",
#         ".avi",
#         ".mov",
#         ".mkv",
#     }
#
#     extension = Path(
#         video.filename
#     ).suffix.lower()
#
#     if extension not in allowed_extensions:
#
#         raise HTTPException(
#             status_code=400,
#             detail=(
#                 f"Unsupported video format: {extension}"
#             ),
#         )
#
#     # --------------------------------------------------------
#     # Generate server-side filename
#     # --------------------------------------------------------
#
#     file_id = uuid.uuid4().hex
#
#     filename = (
#         f"{file_id}{extension}"
#     )
#
#     video_path = (
#         UPLOAD_DIR / filename
#     )
#
#     # --------------------------------------------------------
#     # Save uploaded video
#     # --------------------------------------------------------
#
#     try:
#
#         with video_path.open("wb") as buffer:
#
#             shutil.copyfileobj(
#                 video.file,
#                 buffer,
#             )
#
#     except Exception as exc:
#
#         raise HTTPException(
#             status_code=500,
#             detail=(
#                 "Failed to save uploaded video: "
#                 f"{type(exc).__name__}: {exc}"
#             ),
#         )
#
#     finally:
#
#         try:
#             video.file.close()
#         except Exception:
#             pass
#
#     # --------------------------------------------------------
#     # Create inspection job
#     # --------------------------------------------------------
#
#     try:
#
#         job_id = (
#             inspection_runner.create_job(
#                 str(video_path)
#             )
#         )
#
#     except Exception as exc:
#
#         # Remove uploaded file if job creation failed.
#
#         try:
#             video_path.unlink(
#                 missing_ok=True
#             )
#         except Exception:
#             pass
#
#         raise HTTPException(
#             status_code=500,
#             detail=(
#                 "Failed to create inspection job: "
#                 f"{type(exc).__name__}: {exc}"
#             ),
#         )
#
#     # --------------------------------------------------------
#     # Start job in background
#     # --------------------------------------------------------
#
#     background_tasks.add_task(
#         inspection_runner.run_job,
#         job_id,
#     )
#
#     # --------------------------------------------------------
#     # Return immediately
#     # --------------------------------------------------------
#
#     return JSONResponse(
#         status_code=202,
#         content={
#             "job_id": job_id,
#             "status": "queued",
#         },
#     )
#
#
# # ============================================================
# # Get inspection job
# # ============================================================
#
# @router.get(
#     "/inspections/{job_id}",
# )
# def get_inspection(
#     job_id: str,
# ):
#     """
#     Return the current state of an inspection job.
#     """
#
#     job = (
#         inspection_runner.get_job(
#             job_id
#         )
#     )
#
#     if job is None:
#
#         raise HTTPException(
#             status_code=404,
#             detail=(
#                 f"Inspection job not found: "
#                 f"{job_id}"
#             ),
#         )
#
#     return job
