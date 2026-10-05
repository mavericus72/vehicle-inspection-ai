from src.config import (
    ensure_project_directories,
    verify_model_files,
    YOLO_DETECTOR_MODEL,
    VIEW_CLASSIFIER_MODEL,
    DAMAGE_MODEL_PATH,
    VEHICLE_PART_MODEL_PATH,
    VEHICLE_PART_CONFIDENCE,
)

from src.tracking.vehicle_tracker import VehicleTracker
from src.tracking.primary_vehicle_selection import PrimaryVehicleSelector

from src.inspection.coverage_estimator import CoverageEstimator
from src.inspection.representative_frame_extractor import (
    RepresentativeFrameExtractor,
)
from src.inspection.inspection_evaluator import InspectionEvaluator
from src.inspection.part_mapper import PartMapper
from src.inspection.report_generator import ReportGenerator

from src.pipeline.coverage_pipeline import CoveragePipeline
# from src.pipeline.frame_extraction_pipeline import FrameExtractionPipeline
from src.pipeline.damage_pipeline import DamagePipeline
from src.pipeline.part_pipeline import PartPipeline
from src.pipeline.inference_pipeline import InferencePipeline

from src.vision.vehicle_detector import VehicleDetector
from src.vision.vehicle_view_classifier import VehicleViewClassifier
from src.vision.vehicle_damage_detector import VehicleDamageDetector
from src.vision.vehicle_part_segmenter import VehiclePartSegmenter
from src.vision.vehicle_part_extractor import VehiclePartExtractor
from src.vision.vehicle_part_visualizer import VehiclePartVisualizer


def build_inspection_pipeline():
    """
    Construct the complete vehicle inspection pipeline.

    Returns:
        InferencePipeline
    """

    # --------------------------------------------------------------
    # Prepare directories
    # --------------------------------------------------------------

    ensure_project_directories()

    # --------------------------------------------------------------
    # Verify required model files
    # --------------------------------------------------------------

    verify_model_files()

    # --------------------------------------------------------------
    # Vehicle detector
    # --------------------------------------------------------------

    vehicle_detector = VehicleDetector(
        model_path=str(
            YOLO_DETECTOR_MODEL
        )
    )

    # --------------------------------------------------------------
    # Vehicle tracker
    # --------------------------------------------------------------

    vehicle_tracker = VehicleTracker(
        detector=vehicle_detector
    )

    # --------------------------------------------------------------
    # Primary vehicle selector
    # --------------------------------------------------------------

    primary_vehicle_selector = (
        PrimaryVehicleSelector()
    )

    # --------------------------------------------------------------
    # View classifier
    # --------------------------------------------------------------

    view_classifier = VehicleViewClassifier(
        model_path=str(
            VIEW_CLASSIFIER_MODEL
        )
    )

    # --------------------------------------------------------------
    # Coverage estimator
    # --------------------------------------------------------------

    coverage_estimator = CoverageEstimator(
        view_classifier=view_classifier
    )

    # --------------------------------------------------------------
    # Coverage pipeline
    # --------------------------------------------------------------

    coverage_pipeline = CoveragePipeline(
        coverage_estimator=coverage_estimator
    )

    # --------------------------------------------------------------
    # Representative frame extractor
    # --------------------------------------------------------------

    representative_frame_extractor = (
        RepresentativeFrameExtractor(
            view_classifier=view_classifier
        )
    )

    # --------------------------------------------------------------
    # Frame extraction pipeline
    # --------------------------------------------------------------

    # frame_extraction_pipeline = (
    #     FrameExtractionPipeline(
    #         frame_extractor=
    #             representative_frame_extractor
    #     )
    # )

    # --------------------------------------------------------------
    # Damage detector
    # --------------------------------------------------------------

    damage_detector = VehicleDamageDetector(
        model_path=str(
            DAMAGE_MODEL_PATH
        )
    )

    # --------------------------------------------------------------
    # Damage pipeline
    # --------------------------------------------------------------

    damage_pipeline = DamagePipeline(
        damage_detector=damage_detector
    )

    # --------------------------------------------------------------
    # Vehicle-part segmentation
    # --------------------------------------------------------------

    vehicle_part_segmenter = (
        VehiclePartSegmenter(
            model_path=str(
                VEHICLE_PART_MODEL_PATH
            ),
            confidence_threshold=(
                VEHICLE_PART_CONFIDENCE
            ),
        )
    )

    # --------------------------------------------------------------
    # Vehicle-part mapping
    # --------------------------------------------------------------

    part_mapper = PartMapper()

    # --------------------------------------------------------------
    # Vehicle-part extraction
    # --------------------------------------------------------------

    part_extractor = VehiclePartExtractor(
        segmenter=vehicle_part_segmenter,
        mapper=part_mapper,
    )

    # --------------------------------------------------------------
    # Vehicle-part visualization
    # --------------------------------------------------------------

    part_visualizer = VehiclePartVisualizer()

    # --------------------------------------------------------------
    # Vehicle-part pipeline
    # --------------------------------------------------------------

    part_pipeline = PartPipeline(
        part_extractor=part_extractor
    )

    # --------------------------------------------------------------
    # Evaluator
    # --------------------------------------------------------------

    evaluator = InspectionEvaluator()

    # --------------------------------------------------------------
    # Report generator
    # --------------------------------------------------------------

    report_generator = ReportGenerator(
        output_root=None
    )

    # --------------------------------------------------------------
    # Complete inference pipeline
    # --------------------------------------------------------------

    pipeline = InferencePipeline(
        tracker=vehicle_tracker,
        selector=primary_vehicle_selector,
        coverage_pipeline=coverage_pipeline,
        # frame_extractor=frame_extraction_pipeline,
        damage_pipeline=damage_pipeline,
        part_pipeline=part_pipeline,
        evaluator=evaluator,
        report_generator=report_generator,
        part_visualizer=part_visualizer,
    )

    return pipeline
