# # src/pipeline/damage_pipeline.py
#
# from src.vision.vehicle_damage_detector import VehicleDamageDetector
#
#
# class DamagePipeline:
#
#     def __init__(self, damage_detector):
#         self.damage_detector = damage_detector
#
#     def run(self, inspection):
#
#         damages = inspection.get(
#             "damages",
#             {
#                 "front": [],
#                 "rear": [],
#                 "left": [],
#                 "right": []
#             }
#         )
#
#         representative_frames = inspection.get(
#             "representative_frames",
#             {}
#         )
#
#         for view in ["front", "rear", "left", "right"]:
#
#             view_data = representative_frames.get(
#                 view,
#                 {}
#             )
#
#             image = view_data.get("image")
#
#             # No representative frame for this view
#             if image is None:
#                 damages[view] = []
#                 continue
#
#             # Run damage detection
#             detections = self.damage_detector.predict(
#                 image
#             )
#
#             damages[view] = detections
#
#         inspection["damages"] = damages
#
#         return inspection


# src/pipeline/damage_pipeline.py

import os
import cv2


class DamagePipeline:
    """
    Vehicle damage inspection pipeline.

    Responsibilities:
        - Read representative vehicle frames.
        - Run vehicle damage detection.
        - Store damage detections by vehicle view.
        - Generate damage visualization images.
        - Save damage visualization images to disk.
        - Store visualization paths in the inspection dictionary.

    This pipeline does NOT:
        - classify vehicle views
        - select the primary vehicle
        - detect vehicle parts
        - associate damage with vehicle parts
        - perform multi-frame fusion
        - estimate severity
        - generate reports
    """

    VIEWS = [
        "front",
        "rear",
        "left",
        "right",
    ]

    def __init__(
        self,
        damage_detector,
        damage_visualizer,
    ):
        """
        Initialize the damage pipeline.

        Args:
            damage_detector:
                Object responsible for running damage detection.

            damage_visualizer:
                VehicleDamageVisualizer instance responsible for
                drawing segmentation masks, bounding boxes, and labels.
        """

        self.damage_detector = damage_detector
        self.damage_visualizer = damage_visualizer

    # ==================================================================
    # RUN PIPELINE
    # ==================================================================

    def run(self, inspection):
        """
        Run damage detection and visualization on all available
        representative vehicle views.

        Args:
            inspection:
                Current inspection session dictionary.

        Returns:
            Updated inspection dictionary.
        """

        if not isinstance(
            inspection,
            dict,
        ):
            raise TypeError(
                "inspection must be a dictionary."
            )

        representative_frames = inspection.get(
            "representative_frames",
            {},
        )

        if not isinstance(
            representative_frames,
            dict,
        ):
            representative_frames = {}

        # --------------------------------------------------------------
        # Existing damage results
        # --------------------------------------------------------------

        damages = inspection.get(
            "damages",
            {},
        )

        if not isinstance(
            damages,
            dict,
        ):
            damages = {}

        # --------------------------------------------------------------
        # Resolve directory where visualization images will be saved.
        # --------------------------------------------------------------

        visualization_dir = (
            self._resolve_visualization_directory(
                inspection
            )
        )

        os.makedirs(
            visualization_dir,
            exist_ok=True,
        )

        print(
            "\nDamage visualization directory:",
            visualization_dir,
        )

        # --------------------------------------------------------------
        # Visualization results
        # --------------------------------------------------------------

        damage_visualizations = {}

        # --------------------------------------------------------------
        # Process each vehicle view
        # --------------------------------------------------------------

        for view in self.VIEWS:

            view_data = representative_frames.get(
                view,
                {},
            )

            if not isinstance(
                view_data,
                dict,
            ):
                view_data = {}

            image = view_data.get(
                "image"
            )

            # ==========================================================
            # NO REPRESENTATIVE FRAME
            # ==========================================================

            if image is None:

                damages[view] = []

                print(
                    f"No representative frame for damage detection: "
                    f"{view}"
                )

                continue

            # ==========================================================
            # DAMAGE DETECTION
            # ==========================================================

            print(
                f"\nDetecting vehicle damage: {view}"
            )

            try:

                detections = (
                    self.damage_detector.predict(
                        image
                    )
                )

                if detections is None:
                    detections = []

                damages[view] = detections

                print(
                    f"Damage detections "
                    f"({view}): {len(detections)}"
                )

            except Exception as exc:

                print(
                    f"Damage detection failed "
                    f"for {view}: "
                    f"{type(exc).__name__}: {exc}"
                )

                # Keep the pipeline running for the
                # remaining vehicle views.
                damages[view] = []

                continue

            # ==========================================================
            # DAMAGE VISUALIZATION
            # ==========================================================

            try:

                print(
                    f"Generating damage visualization: {view}"
                )

                visualized_image = (
                    self.damage_visualizer.visualize(
                        image=image,
                        detections=detections,
                    )
                )

                if visualized_image is None:

                    raise ValueError(
                        "Damage visualizer returned None."
                    )

                # ------------------------------------------------------
                # Build output filename
                # ------------------------------------------------------

                filename = (
                    f"{view}_damage_visualization.jpg"
                )

                output_path = os.path.join(
                    visualization_dir,
                    filename,
                )

                # ------------------------------------------------------
                # Save image
                # ------------------------------------------------------

                success = cv2.imwrite(
                    output_path,
                    visualized_image,
                )

                if not success:

                    raise IOError(
                        "cv2.imwrite() failed to save "
                        f"damage visualization: {output_path}"
                    )

                # ------------------------------------------------------
                # Verify file exists
                # ------------------------------------------------------

                if not os.path.isfile(
                    output_path
                ):

                    raise FileNotFoundError(
                        "Damage visualization file was not created: "
                        f"{output_path}"
                    )

                file_size = os.path.getsize(
                    output_path
                )

                if file_size <= 0:

                    raise ValueError(
                        "Damage visualization file is empty: "
                        f"{output_path}"
                    )

                # ------------------------------------------------------
                # Store visualization metadata
                # ------------------------------------------------------

                damage_visualizations[view] = {
                    "path": os.path.abspath(
                        output_path
                    ),
                    "source_path": os.path.abspath(
                        output_path
                    ),
                    "type": "damage_visualization",
                    "view": view,
                    "detection_count": len(
                        detections
                    ),
                    "exists": True,
                    "size_bytes": file_size,
                }

                print(
                    f"Damage visualization saved "
                    f"[{view}]: {output_path}"
                )

            except Exception as exc:

                print(
                    f"Damage visualization failed "
                    f"for {view}: "
                    f"{type(exc).__name__}: {exc}"
                )

        # ==============================================================
        # STORE RESULTS IN INSPECTION
        # ==============================================================

        inspection["damages"] = damages

        inspection["damage_visualizations"] = (
            damage_visualizations
        )

        # --------------------------------------------------------------
        # Summary
        # --------------------------------------------------------------

        print(
            "\nDamage pipeline complete."
        )

        print(
            "Damage visualization images generated:",
            len(
                damage_visualizations
            ),
        )

        return inspection

    # ==================================================================
    # RESOLVE VISUALIZATION DIRECTORY
    # ==================================================================

    def _resolve_visualization_directory(
            self,
            inspection,
    ):
        """
        Resolve the inspection-specific directory for damage
        visualization images.

        Damage visualization images are stored directly inside:

            <project_root>/reports/inspections/<session_id>/
                damage_visualizations/

        They are never stored beside the source video.
        """

        session_id = inspection.get(
            "session_id"
        )

        if not session_id:
            raise ValueError(
                "Inspection session_id is required."
            )

        # ==============================================================
        # 1. Use an already-resolved report directory
        # ==============================================================

        report_output_dir = inspection.get(
            "report_output_dir"
        )

        if report_output_dir:
            report_output_dir = os.path.abspath(
                str(report_output_dir)
            )

            os.makedirs(
                report_output_dir,
                exist_ok=True,
            )

            visualization_dir = os.path.join(
                report_output_dir,
                "damage_visualizations",
            )

            os.makedirs(
                visualization_dir,
                exist_ok=True,
            )

            return visualization_dir

        # ==============================================================
        # 2. Use an existing inspection output directory
        # ==============================================================

        inspection_output_dir = inspection.get(
            "inspection_output_dir"
        )

        if inspection_output_dir:
            inspection_output_dir = os.path.abspath(
                str(inspection_output_dir)
            )

            os.makedirs(
                inspection_output_dir,
                exist_ok=True,
            )

            # Keep both fields synchronized.
            inspection[
                "report_output_dir"
            ] = inspection_output_dir

            visualization_dir = os.path.join(
                inspection_output_dir,
                "damage_visualizations",
            )

            os.makedirs(
                visualization_dir,
                exist_ok=True,
            )

            return visualization_dir

        # ==============================================================
        # 3. Derive project root from video path
        # ==============================================================

        video_path = inspection.get(
            "video_path"
        )

        if video_path:

            video_path = os.path.abspath(
                str(video_path)
            )

            video_dir = os.path.dirname(
                video_path
            )

            # ----------------------------------------------------------
            # Find the project root.
            #
            # We look upward for an existing "reports" directory.
            # ----------------------------------------------------------

            current = video_dir

            while True:

                reports_dir = os.path.join(
                    current,
                    "reports",
                )

                if os.path.isdir(
                        reports_dir
                ):
                    report_output_dir = os.path.join(
                        reports_dir,
                        "inspections",
                        session_id,
                    )

                    os.makedirs(
                        report_output_dir,
                        exist_ok=True,
                    )

                    inspection[
                        "report_output_dir"
                    ] = report_output_dir

                    visualization_dir = os.path.join(
                        report_output_dir,
                        "damage_visualizations",
                    )

                    os.makedirs(
                        visualization_dir,
                        exist_ok=True,
                    )

                    return visualization_dir

                parent = os.path.dirname(
                    current
                )

                if parent == current:
                    break

                current = parent

            # ----------------------------------------------------------
            # If reports/ was not found, use the project root implied
            # by the video path.
            #
            # Your layout:
            #
            # vehicle-inspection-ai/
            #     test1.mp4
            #
            # becomes:
            #
            # vehicle-inspection-ai/
            #     reports/
            #         inspections/
            #             <session_id>/
            # ----------------------------------------------------------

            project_root = video_dir

            report_output_dir = os.path.join(
                project_root,
                "reports",
                "inspections",
                session_id,
            )

            os.makedirs(
                report_output_dir,
                exist_ok=True,
            )

            inspection[
                "report_output_dir"
            ] = report_output_dir

            visualization_dir = os.path.join(
                report_output_dir,
                "damage_visualizations",
            )

            os.makedirs(
                visualization_dir,
                exist_ok=True,
            )

            return visualization_dir

        # ==============================================================
        # 4. Final fallback
        # ==============================================================

        report_output_dir = os.path.join(
            os.getcwd(),
            "reports",
            "inspections",
            session_id,
        )

        os.makedirs(
            report_output_dir,
            exist_ok=True,
        )

        inspection[
            "report_output_dir"
        ] = report_output_dir

        visualization_dir = os.path.join(
            report_output_dir,
            "damage_visualizations",
        )

        os.makedirs(
            visualization_dir,
            exist_ok=True,
        )

        return visualization_dir
