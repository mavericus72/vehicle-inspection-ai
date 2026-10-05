# from src.vision.vehicle_part_extractor import VehiclePartExtractor
#
#
# class PartPipeline:
#     """
#     Vehicle-part inspection pipeline.
#
#     Responsibilities:
#         - Read representative vehicle frames.
#         - Run vehicle-part extraction.
#         - Store mapped vehicle-part detections in inspection.
#
#     This pipeline does NOT:
#         - detect vehicle damage
#         - classify vehicle views
#         - select the primary vehicle
#         - generate reports
#     """
#
#     VIEWS = [
#         "front",
#         "rear",
#         "left",
#         "right",
#     ]
#
#     def __init__(self, part_extractor):
#         self.part_extractor = part_extractor
#
#     def run(self, inspection):
#         """
#         Run vehicle-part extraction on all available
#         representative vehicle views.
#         """
#
#         representative_frames = inspection.get(
#             "representative_frames",
#             {}
#         )
#
#         vehicle_parts = inspection.get(
#             "vehicle_parts",
#             {
#                 "front": [],
#                 "rear": [],
#                 "left": [],
#                 "right": [],
#             }
#         )
#
#         for view in self.VIEWS:
#
#             view_data = representative_frames.get(
#                 view,
#                 {}
#             )
#
#             if not isinstance(view_data, dict):
#                 vehicle_parts[view] = []
#                 continue
#
#             image = view_data.get("image")
#
#             # No representative frame for this view.
#             if image is None:
#                 vehicle_parts[view] = []
#                 continue
#
#             print(
#                 f"\nDetecting vehicle parts: {view}"
#             )
#
#             try:
#
#                 detections = self.part_extractor.extract(
#                     image,
#                     view
#                 )
#
#                 if detections is None:
#                     detections = []
#
#                 vehicle_parts[view] = detections
#
#                 print(
#                     f"Vehicle parts detected "
#                     f"({view}): {len(detections)}"
#                 )
#
#             except Exception as exc:
#
#                 print(
#                     f"Vehicle-part detection failed "
#                     f"for {view}: "
#                     f"{type(exc).__name__}: {exc}"
#                 )
#
#                 vehicle_parts[view] = []
#
#         inspection["vehicle_parts"] = vehicle_parts
#
#         return inspection


import os
import cv2
from src.config import INSPECTION_OUTPUT_DIR
from src.vision.vehicle_part_extractor import VehiclePartExtractor
from src.vision.vehicle_part_visualizer import VehiclePartVisualizer


class PartPipeline:
    """
    Vehicle-part inspection pipeline.

    Responsibilities:
        - Read representative vehicle frames.
        - Extract vehicle-part detections.
        - Store structured detections in inspection.
        - Generate annotated vehicle-part visualization images.
        - Save visualization paths in inspection.

    This pipeline does NOT:
        - detect vehicle damage
        - classify vehicle views
        - select the primary vehicle
        - generate the final report
    """

    VIEWS = [
        "front",
        "rear",
        "left",
        "right",
    ]

    def __init__(
        self,
        part_extractor: VehiclePartExtractor,
        visualizer: VehiclePartVisualizer,
    ):
        self.part_extractor = part_extractor
        self.visualizer = visualizer

    def run(self, inspection):

        representative_frames = inspection.get(
            "representative_frames",
            {}
        )

        vehicle_parts = inspection.get(
            "vehicle_parts",
            {
                "front": [],
                "rear": [],
                "left": [],
                "right": [],
            }
        )

        # --------------------------------------------------------------
        # Prepare visualization output directory
        # --------------------------------------------------------------

        session_id = inspection.get(
            "session_id",
            "inspection"
        )

        output_dir = os.path.join(
            str(INSPECTION_OUTPUT_DIR),
            str(session_id),
            "vehicle_part_visualizations"
        )

        os.makedirs(
            output_dir,
            exist_ok=True
        )

        visualization_paths = {}

        # --------------------------------------------------------------
        # Process each representative view
        # --------------------------------------------------------------

        for view in self.VIEWS:

            view_data = representative_frames.get(
                view,
                {}
            )

            image = view_data.get("image")

            # ----------------------------------------------------------
            # No representative frame
            # ----------------------------------------------------------

            if image is None:

                vehicle_parts[view] = []

                continue

            print(
                f"\nDetecting vehicle parts: {view}"
            )

            # ----------------------------------------------------------
            # Extract vehicle parts
            # ----------------------------------------------------------

            try:

                detections = self.part_extractor.extract(
                    image,
                    view
                )

                vehicle_parts[view] = detections

                print(
                    f"Vehicle parts detected "
                    f"({view}): {len(detections)}"
                )

            except Exception as exc:

                print(
                    f"Vehicle-part detection failed "
                    f"for {view}: "
                    f"{type(exc).__name__}: {exc}"
                )

                vehicle_parts[view] = []

                continue

            # ----------------------------------------------------------
            # Generate visualization
            # ----------------------------------------------------------

            try:

                visualized_image = self.visualizer.visualize(
                    image,
                    detections
                )

                output_path = os.path.join(
                    output_dir,
                    f"{view}_vehicle_parts.jpg"
                )

                success = cv2.imwrite(
                    output_path,
                    visualized_image
                )

                if not success:
                    raise IOError(
                        f"Failed to write image: {output_path}"
                    )

                visualization_paths[view] = output_path

                print(
                    f"Vehicle-part visualization saved: "
                    f"{output_path}"
                )

            except Exception as exc:

                print(
                    f"Vehicle-part visualization failed "
                    f"for {view}: "
                    f"{type(exc).__name__}: {exc}"
                )

        # --------------------------------------------------------------
        # Store results
        # --------------------------------------------------------------

        inspection["vehicle_parts"] = vehicle_parts

        inspection["vehicle_part_visualizations"] = (
            visualization_paths
        )

        return inspection
