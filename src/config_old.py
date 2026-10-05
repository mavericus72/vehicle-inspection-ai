import os
from pathlib import Path


# ======================================================================
# PROJECT ROOT
# ======================================================================

_DEFAULT_PROJECT_ROOT = Path(__file__).resolve().parent.parent

PROJECT_ROOT = Path(
    os.getenv(
        "PROJECT_ROOT",
        str(_DEFAULT_PROJECT_ROOT),
    )
).resolve()


# ======================================================================
# DIRECTORY STRUCTURE
# ======================================================================

MODELS_DIR = PROJECT_ROOT / "models"

DATA_DIR = PROJECT_ROOT / "data"

OUTPUTS_DIR = PROJECT_ROOT / "outputs"

REPORTS_DIR = PROJECT_ROOT / "reports"

INSPECTIONS_DIR = REPORTS_DIR / "inspections"


# ======================================================================
# MODEL DIRECTORIES
# ======================================================================

CLASSIFICATION_MODELS_DIR = (
    MODELS_DIR / "classification"
)

DETECTION_MODELS_DIR = (
    MODELS_DIR / "detection"
)

DAMAGE_MODELS_DIR = (
    MODELS_DIR / "vehicle_damage_detection"
)

VEHICLE_DAMAGE_SEGMENTER_DIR = (
    MODELS_DIR / "vehicle_damage_segmenter"
)

VEHICLE_PART_SEGMENTER_DIR = (
    MODELS_DIR / "vehicle_part_segmenter"
)

VIEW_CLASSIFIER_DIR = (
    MODELS_DIR / "view_classifier"
)


# ======================================================================
# VEHICLE DETECTION MODELS
# ======================================================================

YOLO_DETECTOR_MODEL = (
    DETECTION_MODELS_DIR / "yolo11n.pt"
)

YOLO_DETECTOR_LARGE_MODEL = (
    DETECTION_MODELS_DIR / "yolo26n.pt"
)


# ======================================================================
# VIEW / CLASSIFICATION MODELS
# ======================================================================

VIEW_CLASSIFIER_MODEL = (
    CLASSIFICATION_MODELS_DIR / "best.pt"
)

YOLO_CLASSIFIER_BASE = (
    CLASSIFICATION_MODELS_DIR / "last.pt"
)


# ======================================================================
# VEHICLE DAMAGE MODEL
# ======================================================================

DAMAGE_MODEL_PATH = (
    DAMAGE_MODELS_DIR
    / "yolo11n_seg_damage_v1"
    / "weights"
    / "best.pt"
)


# ======================================================================
# VEHICLE PART MODEL
# ======================================================================

# Actual project structure:
#
# models/
# └── vehicle_part_segmenter/
#     ├── best.pt
#     └── last.pt

VEHICLE_PART_MODEL_PATH = (
    VEHICLE_PART_SEGMENTER_DIR
    / "best.pt"
)

VEHICLE_PART_MODEL_LAST_PATH = (
    VEHICLE_PART_SEGMENTER_DIR
    / "last.pt"
)


# ======================================================================
# PIPELINE SETTINGS
# ======================================================================

FRAME_SKIP = int(
    os.getenv(
        "FRAME_SKIP",
        "10",
    )
)


# ======================================================================
# MODEL CONFIDENCE SETTINGS
# ======================================================================

VEHICLE_DETECTION_CONFIDENCE = float(
    os.getenv(
        "VEHICLE_DETECTION_CONFIDENCE",
        "0.30",
    )
)

VEHICLE_PART_CONFIDENCE = float(
    os.getenv(
        "VEHICLE_PART_CONFIDENCE",
        "0.30",
    )
)

DAMAGE_CONFIDENCE = float(
    os.getenv(
        "DAMAGE_CONFIDENCE",
        "0.30",
    )
)

VIEW_CLASSIFICATION_CONFIDENCE = float(
    os.getenv(
        "VIEW_CLASSIFICATION_CONFIDENCE",
        "0.30",
    )
)


# ======================================================================
# OUTPUT SETTINGS
# ======================================================================

INSPECTION_OUTPUT_DIR = (
    INSPECTIONS_DIR
)


# ======================================================================
# HELPER — CREATE RUNTIME DIRECTORIES
# ======================================================================

def ensure_project_directories():
    """
    Create runtime directories required by the application.

    Model directories are intentionally not created because missing
    model directories/files should be treated as deployment errors.
    """

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    INSPECTIONS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )


# ======================================================================
# HELPER — VERIFY REQUIRED MODELS
# ======================================================================

def verify_model_files():
    """
    Verify that the model files required by the pipeline exist.

    Returns:
        dict containing model paths and existence status.

    Raises:
        FileNotFoundError if a required model is missing.
    """

    required_models = {
        "vehicle_detector": YOLO_DETECTOR_MODEL,
        "view_classifier": VIEW_CLASSIFIER_MODEL,
        "damage_detector": DAMAGE_MODEL_PATH,
        "vehicle_part_segmenter": VEHICLE_PART_MODEL_PATH,
    }

    missing_models = {
        name: str(path)
        for name, path in required_models.items()
        if not path.is_file()
    }

    if missing_models:

        message = (
            "Required model files are missing:\n"
            + "\n".join(
                f"  {name}: {path}"
                for name, path in missing_models.items()
            )
        )

        raise FileNotFoundError(message)

    return {
        name: str(path)
        for name, path in required_models.items()
    }


# ======================================================================
# CONFIGURATION SUMMARY
# ======================================================================

def get_config_summary():
    """
    Return a JSON-serializable configuration summary.

    Useful for:
        - debugging
        - startup logs
        - API health checks
        - deployment verification
    """

    return {
        "project_root": str(PROJECT_ROOT),

        "models_dir": str(MODELS_DIR),

        "data_dir": str(DATA_DIR),

        "outputs_dir": str(OUTPUTS_DIR),

        "reports_dir": str(REPORTS_DIR),

        "inspections_dir": str(
            INSPECTIONS_DIR
        ),

        "yolo_detector_model": str(
            YOLO_DETECTOR_MODEL
        ),

        "yolo_detector_large_model": str(
            YOLO_DETECTOR_LARGE_MODEL
        ),

        "view_classifier_model": str(
            VIEW_CLASSIFIER_MODEL
        ),

        "damage_model_path": str(
            DAMAGE_MODEL_PATH
        ),

        "vehicle_part_model_path": str(
            VEHICLE_PART_MODEL_PATH
        ),

        "frame_skip": FRAME_SKIP,

        "vehicle_detection_confidence": (
            VEHICLE_DETECTION_CONFIDENCE
        ),

        "vehicle_part_confidence": (
            VEHICLE_PART_CONFIDENCE
        ),

        "damage_confidence": (
            DAMAGE_CONFIDENCE
        ),

        "view_classification_confidence": (
            VIEW_CLASSIFICATION_CONFIDENCE
        ),
    }

# ======================================================================
# PIPELINE MODEL ALIASES
# ======================================================================

VEHICLE_DETECTOR_MODEL = YOLO_DETECTOR_MODEL

VEHICLE_VIEW_CLASSIFIER_MODEL = VIEW_CLASSIFIER_MODEL

VEHICLE_PART_SEGMENTER_MODEL = VEHICLE_PART_MODEL_PATH

VEHICLE_DAMAGE_MODEL = DAMAGE_MODEL_PATH



# import os
#
# PROJECT_ROOT = "/content/drive/MyDrive/vehicle-inspection-ai"
#
# # Detection models
# YOLO_DETECTOR_MODEL = os.path.join(
#     PROJECT_ROOT,
#     "models",
#     "detection",
#     "yolo11n.pt"
# )
#
# YOLO_DETECTOR_LARGE_MODEL = os.path.join(
#     PROJECT_ROOT,
#     "models",
#     "detection",
#     "yolo26n.pt"
# )
#
# # Classification models
# VIEW_CLASSIFIER_MODEL = os.path.join(
#     PROJECT_ROOT,
#     "models",
#     "classification",
#     "best.pt"
# )
#
# YOLO_CLASSIFIER_BASE = os.path.join(
#     PROJECT_ROOT,
#     "models",
#     "classification",
#     "yolo11n-cls.pt"
# )
#
# # Damage Detection models
# DAMAGE_MODEL_PATH = os.path.join(
#     PROJECT_ROOT,
#     "models",
#     "vehicle_damage_detection",
#     "yolo11n_seg_damage_v1",
#     "weights",
#     "best.pt"
# )
# FRAME_SKIP = 10 # Used in coverage_pipeline where you can edit the frames to be skipped