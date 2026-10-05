# """
# Vehicle Inspection AI
# Application entry point.
#
# This file initializes the inspection pipeline and provides
# a reusable function for processing an inspection video.
# """
#
# import os
#
# from src.inspection.inspection_session import create_inspection_session
# from src.inspection.report_generator import ReportGenerator
# from src.pipeline.inference_pipeline import InferencePipeline
# from src.pipeline.damage_pipeline import DamagePipeline
# from src.pipeline.coverage_pipeline import CoveragePipeline
#
# from src.tracking.vehicle_tracker import VehicleTracker
# from src.tracking.primary_vehicle_selection import PrimaryVehicleSelector
#
# from src.inspection.frame_quality import FrameQualityEvaluator
# from src.inspection.representative_frame_extractor import (
#     RepresentativeFrameExtractor,
# )
# from src.inspection.inspection_evaluator import InspectionEvaluator
#
# from src.vision.vehicle_view_classifier import VehicleViewClassifier
# from src.vision.vehicle_damage_detector import VehicleDamageDetector
#
# from src.inspection.coverage_estimator import CoverageEstimator
#
# from src.config import VIEW_CLASSIFIER_MODEL
#
#
# # ----------------------------------------------------------------------
# # MODEL PATHS
# # ----------------------------------------------------------------------
#
# DAMAGE_MODEL_PATH = (
#     "/content/drive/MyDrive/"
#     "vehicle-inspection-ai/"
#     "models/vehicle_damage_detection/"
#     "yolo11n_seg_damage_v1/"
#     "weights/best.pt"
# )
#
#
# # ----------------------------------------------------------------------
# # PIPELINE FACTORY
# # ----------------------------------------------------------------------
#
# def create_pipeline():
#     """
#     Create and configure the complete vehicle inspection pipeline.
#
#     Returns:
#         InferencePipeline
#     """
#
#     # --------------------------------------------------------------
#     # View classification
#     # --------------------------------------------------------------
#
#     classifier = VehicleViewClassifier(
#         VIEW_CLASSIFIER_MODEL
#     )
#
#     # --------------------------------------------------------------
#     # Coverage
#     # --------------------------------------------------------------
#
#     coverage_estimator = CoverageEstimator()
#
#     coverage_pipeline = CoveragePipeline(
#         classifier,
#         coverage_estimator,
#     )
#
#     # --------------------------------------------------------------
#     # Vehicle tracking
#     # --------------------------------------------------------------
#
#     tracker = VehicleTracker()
#
#     selector = PrimaryVehicleSelector()
#
#     # --------------------------------------------------------------
#     # Representative frames
#     # --------------------------------------------------------------
#
#     frame_quality_evaluator = FrameQualityEvaluator()
#
#     frame_extractor = RepresentativeFrameExtractor(
#         frame_quality_evaluator
#     )
#
#     # --------------------------------------------------------------
#     # Damage detection
#     # --------------------------------------------------------------
#
#     damage_detector = VehicleDamageDetector(
#         DAMAGE_MODEL_PATH
#     )
#
#     damage_pipeline = DamagePipeline(
#         damage_detector
#     )
#
#     # --------------------------------------------------------------
#     # Inspection evaluation
#     # --------------------------------------------------------------
#
#     evaluator = InspectionEvaluator()
#
#     # --------------------------------------------------------------
#     # Report generation
#     # --------------------------------------------------------------
#
#     report_generator = ReportGenerator()
#
#     # --------------------------------------------------------------
#     # Final pipeline
#     # --------------------------------------------------------------
#
#     pipeline = InferencePipeline(
#         tracker,
#         selector,
#         coverage_pipeline,
#         frame_extractor,
#         damage_pipeline,
#         evaluator,
#         report_generator,
#     )
#
#     return pipeline
#
#
# # ----------------------------------------------------------------------
# # INSPECTION RUNNER
# # ----------------------------------------------------------------------
#
# def run_inspection(video_path):
#     """
#     Run a complete vehicle inspection.
#
#     Args:
#         video_path:
#             Path to the inspection video.
#
#     Returns:
#         Completed inspection dictionary.
#     """
#
#     if not video_path:
#         raise ValueError(
#             "video_path must be provided."
#         )
#
#     if not os.path.isfile(video_path):
#         raise FileNotFoundError(
#             f"Inspection video not found: {video_path}"
#         )
#
#     # --------------------------------------------------------------
#     # Create inspection state
#     # --------------------------------------------------------------
#
#     inspection = create_inspection_session()
#
#     inspection["video_path"] = video_path
#
#     inspection["video_name"] = os.path.basename(
#         video_path
#     )
#
#     # --------------------------------------------------------------
#     # Create pipeline
#     # --------------------------------------------------------------
#
#     pipeline = create_pipeline()
#
#     # --------------------------------------------------------------
#     # Run inspection
#     # --------------------------------------------------------------
#
#     inspection = pipeline.run(
#         inspection
#     )
#
#     return inspection
#
#
# # ----------------------------------------------------------------------
# # MAIN
# # ----------------------------------------------------------------------
#
# if __name__ == "__main__":
#
#     import argparse
#
#     parser = argparse.ArgumentParser(
#         description="Run Vehicle Inspection AI"
#     )
#
#     parser.add_argument(
#         "video",
#         help="Path to the inspection video",
#     )
#
#     args = parser.parse_args()
#
#     inspection = run_inspection(
#         args.video
#     )
#
#     print("=" * 70)
#     print("VEHICLE INSPECTION COMPLETE")
#     print("=" * 70)
#
#     print(
#         "Session ID:",
#         inspection.get("session_id")
#     )
#
#     print(
#         "Video:",
#         inspection.get("video_name")
#     )
#
#     print(
#         "Coverage:",
#         inspection.get("coverage")
#     )
#
#     print(
#         "Coverage complete:",
#         inspection.get("coverage_complete")
#     )
#
#     print(
#         "Damage records:",
#         sum(
#             len(records)
#             for records in inspection.get(
#                 "damages",
#                 {}
#             ).values()
#             if isinstance(records, list)
#         )
#     )
#
#     print(
#         "Vehicle-part records:",
#         sum(
#             len(records)
#             for records in inspection.get(
#                 "vehicle_parts",
#                 {}
#             ).values()
#             if isinstance(records, list)
#         )
#     )
#
#     print("=" * 70)


# ======================================================================
# app.py — Vehicle Inspection AI Application Entry Point
# ======================================================================

import os
import argparse
from datetime import datetime


# ======================================================================
# CONFIGURATION
# ======================================================================

from src.config import (
    YOLO_DETECTOR_MODEL,
    VIEW_CLASSIFIER_MODEL,
    VEHICLE_PART_MODEL_PATH,
    DAMAGE_MODEL_PATH,
    VEHICLE_DETECTOR_MODEL,
)


# ======================================================================
# INSPECTION SESSION
# ======================================================================

from src.inspection.inspection_session import (
    create_inspection_session,
)


# ======================================================================
# TRACKING
# ======================================================================

from src.tracking.vehicle_tracker import (
    VehicleTracker,
)

from src.tracking.primary_vehicle_selection import (
    PrimaryVehicleSelector,
)


# ======================================================================
# COVERAGE / INSPECTION
# ======================================================================

from src.inspection.coverage_estimator import (
    CoverageEstimator,
)

from src.pipeline.coverage_pipeline import (
    CoveragePipeline,
)

from src.inspection.representative_frame_extractor import (
    RepresentativeFrameExtractor,
)

from src.inspection.frame_quality import (
    FrameQualityEvaluator,
)


# ======================================================================
# VISION
# ======================================================================

from src.vision.vehicle_detector import (
    VehicleDetector,
)

from src.vision.vehicle_view_classifier import (
    VehicleViewClassifier,
)

from src.vision.vehicle_damage_detector import (
    VehicleDamageDetector,
)

from src.vision.vehicle_part_segmenter import (
    VehiclePartSegmenter,
)

from src.vision.vehicle_part_visualizer import (
    VehiclePartVisualizer,
)

from src.vision.vehicle_part_extractor import (
    VehiclePartExtractor,
)


# ======================================================================
# DAMAGE PIPELINE
# ======================================================================

from src.vision.vehicle_damage_visualizer import (
    VehicleDamageVisualizer,
)

from src.pipeline.damage_pipeline import (
    DamagePipeline,
)


# ======================================================================
# VEHICLE PART PIPELINE
# ======================================================================

from src.inspection.part_mapper import (
    PartMapper,
)

from src.pipeline.part_pipeline import (
    PartPipeline,
)


# ======================================================================
# EVALUATION / REPORTING
# ======================================================================

from src.inspection.inspection_evaluator import (
    InspectionEvaluator,
)

from src.inspection.report_generator import (
    ReportGenerator,
)


# ======================================================================
# FINAL INFERENCE PIPELINE
# ======================================================================

from src.pipeline.inference_pipeline import (
    InferencePipeline,
)


# ======================================================================
# UTILITY
# ======================================================================

def validate_file(path, name):
    """
    Validate that a required file exists.
    """

    if not path:
        raise ValueError(
            f"{name} path is empty."
        )

    if not os.path.isfile(path):
        raise FileNotFoundError(
            f"{name} not found: {path}"
        )


# ======================================================================
# BUILD INSPECTION PIPELINE
# ======================================================================

def build_pipeline():
    """
    Construct and connect all components of the inspection system.

    The inference pipeline itself is intentionally kept unchanged.
    """

    print("\n" + "=" * 70)
    print("BUILDING VEHICLE INSPECTION PIPELINE")
    print("=" * 70)

    # --------------------------------------------------------------
    # Validate model paths
    # --------------------------------------------------------------

    print("\nValidating model files...")

    validate_file(
        YOLO_DETECTOR_MODEL,
        "Vehicle detector model",
    )

    validate_file(
        VIEW_CLASSIFIER_MODEL,
        "Vehicle view classifier model",
    )

    validate_file(
        VEHICLE_PART_MODEL_PATH,
        "Vehicle part segmentation model",
    )

    validate_file(
        DAMAGE_MODEL_PATH,
        "Vehicle damage model",
    )

    print("Model files validated: True")

    # --------------------------------------------------------------
    # Vehicle detector
    # --------------------------------------------------------------

    print("\nLoading vehicle detector...")

    vehicle_detector = VehicleDetector(
        model_path=YOLO_DETECTOR_MODEL
    )

    print("Vehicle detector loaded.")

    # --------------------------------------------------------------
    # Vehicle view classifier
    # --------------------------------------------------------------

    print("\nLoading vehicle view classifier...")

    view_classifier = VehicleViewClassifier(
        model_path=VIEW_CLASSIFIER_MODEL
    )

    print("Vehicle view classifier loaded.")

    # --------------------------------------------------------------
    # Vehicle tracker
    # --------------------------------------------------------------

    print("\nCreating vehicle tracker...")

    tracker = VehicleTracker(
        model_path=VEHICLE_DETECTOR_MODEL
    )

    print("Vehicle tracker created.")

    # --------------------------------------------------------------
    # Primary vehicle selector
    # --------------------------------------------------------------

    print("\nCreating primary vehicle selector...")

    selector = PrimaryVehicleSelector()

    print("Primary vehicle selector created.")

    # --------------------------------------------------------------
    # Coverage estimator
    # --------------------------------------------------------------

    print("\nCreating coverage estimator...")

    coverage_estimator = CoverageEstimator()

    coverage_pipeline = CoveragePipeline(
        coverage_estimator=coverage_estimator,
        view_classifier=view_classifier,
    )

    print("Coverage pipeline created.")

    # --------------------------------------------------------------
    # Frame quality evaluator
    # --------------------------------------------------------------

    print("\nCreating frame quality evaluator...")

    quality_evaluator = FrameQualityEvaluator()

    print("Frame quality evaluator created.")

    # --------------------------------------------------------------
    # Representative frame extractor
    # --------------------------------------------------------------

    print("\nCreating representative frame extractor...")

    frame_extractor = RepresentativeFrameExtractor(
        quality_evaluator=quality_evaluator,
    )

    print("Representative frame extractor created.")

    # --------------------------------------------------------------
    # Vehicle damage detector
    # --------------------------------------------------------------

    print("\nLoading vehicle damage detector...")

    damage_detector = VehicleDamageDetector(
        model_path=DAMAGE_MODEL_PATH
    )

    print("Vehicle damage detector loaded.")

    # --------------------------------------------------------------
    # Damage pipeline
    # --------------------------------------------------------------
    print("\nCreating vehicle damage visualizer...")

    damage_visualizer = VehicleDamageVisualizer()

    print("Vehicle damage visualizer created.")

    print("\nCreating damage pipeline...")

    damage_pipeline = DamagePipeline(
        damage_detector=damage_detector,
        damage_visualizer=damage_visualizer
    )

    print("Damage pipeline created.")

    # --------------------------------------------------------------
    # Vehicle-part segmentation
    # --------------------------------------------------------------

    print("\nLoading vehicle-part segmenter...")

    part_segmenter = VehiclePartSegmenter(
        model_path=VEHICLE_PART_MODEL_PATH
    )

    print("Vehicle-part segmenter loaded.")

    # --------------------------------------------------------------
    # Part mapper
    # --------------------------------------------------------------

    print("\nCreating part mapper...")

    part_mapper = PartMapper()

    print("Part mapper created.")

    # --------------------------------------------------------------
    # Vehicle-part extractor
    # --------------------------------------------------------------

    print("\nCreating vehicle-part extractor...")

    part_extractor = VehiclePartExtractor(
        segmenter=part_segmenter,
        mapper=part_mapper,
    )

    print("Vehicle-part extractor created.")

    # --------------------------------------------------------------
    # Vehicle-part visualizer
    # --------------------------------------------------------------

    print("\nCreating vehicle-part visualizer...")

    vehicle_part_visualizer = VehiclePartVisualizer(
        alpha=0.45,
        draw_bbox=True,
        draw_label=True,
    )

    print("Vehicle-part visualizer created.")

    # --------------------------------------------------------------
    # Part pipeline
    # --------------------------------------------------------------

    print("\nCreating part pipeline...")

    part_pipeline = PartPipeline(
        part_extractor=part_extractor,
        visualizer=vehicle_part_visualizer,
    )

    print("Part pipeline created.")

    # --------------------------------------------------------------
    # Inspection evaluator
    # --------------------------------------------------------------

    print("\nCreating inspection evaluator...")

    evaluator = InspectionEvaluator()

    print("Inspection evaluator created.")

    # --------------------------------------------------------------
    # Report generator
    # --------------------------------------------------------------

    print("\nCreating report generator...")

    report_generator = ReportGenerator()

    print("Report generator created.")

    # --------------------------------------------------------------
    # Final inference pipeline
    # --------------------------------------------------------------

    print("\nConnecting inference pipeline...")

    pipeline = InferencePipeline(
        tracker=tracker,
        selector=selector,
        coverage_pipeline=coverage_pipeline,
        frame_extractor=frame_extractor,
        damage_pipeline=damage_pipeline,
        part_pipeline=part_pipeline,
        evaluator=evaluator,
        report_generator=report_generator,
    )

    print("Inference pipeline ready.")

    print("\n" + "=" * 70)
    print("PIPELINE READY")
    print("=" * 70)

    return pipeline


# ======================================================================
# CREATE INSPECTION SESSION
# ======================================================================

def create_session(video_path):
    """
    Create and initialize an inspection session.
    """

    validate_file(
        video_path,
        "Inspection video",
    )

    inspection = create_inspection_session()

    inspection["video_path"] = os.path.abspath(
        video_path
    )

    inspection["video_name"] = os.path.basename(
        video_path
    )

    inspection["start_time"] = (
        datetime.now().isoformat()
    )

    return inspection


# ======================================================================
# VERIFY FINAL REPORT OUTPUT
# ======================================================================

def verify_report_outputs(inspection):
    """
    Verify the JSON and PDF report references stored in
    the inspection object.

    This does not generate the reports itself.
    It only verifies that the pipeline/report generator
    produced them.
    """

    print("\n" + "-" * 70)
    print("VERIFY FINAL REPORT OUTPUTS")
    print("-" * 70)

    # --------------------------------------------------------------
    # JSON
    # --------------------------------------------------------------

    final_report_export = inspection.get(
        "final_report_export"
    )

    if not isinstance(
        final_report_export,
        dict,
    ):
        print(
            "JSON report reference : NOT AVAILABLE"
        )
    else:

        json_path = final_report_export.get(
            "path"
        )

        if json_path:

            json_exists = os.path.isfile(
                json_path
            )

            print(
                "JSON report path      :",
                json_path,
            )

            print(
                "JSON report exists    :",
                json_exists,
            )

            if json_exists:

                print(
                    "JSON report size      :",
                    f"{os.path.getsize(json_path):,} bytes",
                )

        else:

            print(
                "JSON report path      : NOT AVAILABLE"
            )

    # --------------------------------------------------------------
    # PDF
    # --------------------------------------------------------------

    final_report_pdf = inspection.get(
        "final_report_pdf"
    )

    if not isinstance(
        final_report_pdf,
        dict,
    ):
        print(
            "PDF report reference  : NOT AVAILABLE"
        )
    else:

        pdf_path = final_report_pdf.get(
            "path"
        )

        if pdf_path:

            pdf_exists = os.path.isfile(
                pdf_path
            )

            print(
                "PDF report path       :",
                pdf_path,
            )

            print(
                "PDF report exists     :",
                pdf_exists,
            )

            if pdf_exists:

                print(
                    "PDF report size       :",
                    f"{os.path.getsize(pdf_path):,} bytes",
                )

        else:

            print(
                "PDF report path       : NOT AVAILABLE"
            )

    print("-" * 70)


# ======================================================================
# RUN INSPECTION
# ======================================================================

def run_inspection(video_path):
    """
    Run one complete vehicle inspection.

    Returns:
        dict:
            Completed inspection object.
    """

    print("\n" + "=" * 70)
    print("VEHICLE INSPECTION AI")
    print("=" * 70)

    # --------------------------------------------------------------
    # Validate input
    # --------------------------------------------------------------

    validate_file(
        video_path,
        "Inspection video",
    )

    video_path = os.path.abspath(
        video_path
    )

    print(
        f"\nInput video:\n{video_path}"
    )

    # --------------------------------------------------------------
    # Create inspection session
    # --------------------------------------------------------------

    inspection = create_session(
        video_path
    )

    print(
        f"\nInspection session created: "
        f"{inspection['session_id']}"
    )

    # --------------------------------------------------------------
    # Build pipeline
    # --------------------------------------------------------------

    pipeline = build_pipeline()

    # --------------------------------------------------------------
    # Run complete inference
    # --------------------------------------------------------------

    print("\n" + "=" * 70)
    print("STARTING INSPECTION")
    print("=" * 70)

    inspection = pipeline.run(
        inspection
    )

    if not isinstance(
        inspection,
        dict,
    ):
        raise TypeError(
            "InferencePipeline.run() must return "
            "the inspection dictionary."
        )

    # --------------------------------------------------------------
    # Final status
    # --------------------------------------------------------------

    print("\n" + "=" * 70)
    print("INSPECTION COMPLETE")
    print("=" * 70)

    print(
        "Inspection ID:",
        inspection.get("session_id"),
    )

    print(
        "Coverage complete:",
        inspection.get("coverage_complete"),
    )

    print(
        "Damage results available:",
        bool(
            inspection.get("damages")
        ),
    )

    print(
        "Vehicle-part results available:",
        bool(
            inspection.get("vehicle_parts")
        ),
    )

    # --------------------------------------------------------------
    # Verify generated reports
    # --------------------------------------------------------------

    verify_report_outputs(
        inspection
    )

    # --------------------------------------------------------------
    # Report locations
    # --------------------------------------------------------------

    final_report_export = inspection.get(
        "final_report_export"
    )

    final_report_pdf = inspection.get(
        "final_report_pdf"
    )

    if isinstance(
        final_report_export,
        dict,
    ):

        print(
            "\nJSON report:"
        )

        print(
            final_report_export.get(
                "path"
            )
        )

    if isinstance(
        final_report_pdf,
        dict,
    ):

        print(
            "\nPDF report:"
        )

        print(
            final_report_pdf.get(
                "path"
            )
        )

    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)

    return inspection


# ======================================================================
# COMMAND-LINE INTERFACE
# ======================================================================

def main():

    parser = argparse.ArgumentParser(
        description=(
            "Vehicle Inspection AI — "
            "run a complete inspection on a video."
        )
    )

    parser.add_argument(
        "video",
        help=(
            "Path to the vehicle inspection video."
        ),
    )

    args = parser.parse_args()

    run_inspection(
        args.video
    )


# ======================================================================
# APPLICATION ENTRY POINT
# ======================================================================

if __name__ == "__main__":
    main()
