# class ReportGenerator:
#
#     def generate(self, inspection):
#
#         report = inspection["report"]
#
#         coverage = report["coverage"]
#
#         result = {}
#
#         result["inspection_id"] = report["inspection_id"]
#
#         result["video_name"] = report["video_name"]
#
#
#         # Overall status
#
#         if report["coverage_complete"]:
#             result["status"] = "Inspection Complete"
#         else:
#             result["status"] = "Inspection Incomplete"
#
#
#         # Coverage summary
#
#         result["coverage_summary"] = {
#
#             "Front View":
#                 "Available" if coverage["front"] else "Missing",
#
#             "Rear View":
#                 "Available" if coverage["rear"] else "Missing",
#
#             "Left View":
#                 "Available" if coverage["left"] else "Missing",
#
#             "Right View":
#                 "Available" if coverage["right"] else "Missing"
#         }
#
#
#         # Missing views
#
#         missing = []
#
#         for view, available in coverage.items():
#
#             if not available:
#                 missing.append(view)
#
#
#         result["missing_views"] = missing
#
#
#         # Representative frames
#
#         frames = {}
#
#         for view, data in report["representative_frames"].items():
#
#             if data["available"]:
#
#                 frames[view] = {
#                     "frame_id": data["frame_id"],
#                     "quality": data["quality"]
#                 }
#
#
#         result["representative_frames"] = frames
#
#
#         return result

# ======================================================================
# src/inspection/report_generator.py
#
# COMPLETE REPORT GENERATOR
#
# Responsibilities:
#   1. Build final inspection report
#   2. Save JSON report
#   3. Generate human-readable PDF report
#   4. Validate both outputs
#   5. Store report references in inspection
#
# Outputs:
#
#   reports/
#       inspections/
#           <INSPECTION_ID>/
#               final_inspection_report.json
#               final_inspection_report.pdf
#               vehicle_part_visualizations/
#               damage_visualizations/
#
# ======================================================================

import os
import json
import html
import shutil
from datetime import datetime


class ReportGenerator:
    """
    Generates the final machine-readable JSON report and
    human-readable PDF inspection report.

    Important behavior:
    - Creates an inspection-specific report directory.
    - Copies damage visualization images into:
          <inspection_dir>/damage_visualizations/
    - Copies vehicle-part visualization images into:
          <inspection_dir>/vehicle_part_visualizations/
    - Stores the copied image paths in the JSON report.
    - Embeds the copied images into the PDF.
    - Converts timestamps to human-readable format.
    - Does not include a "Report Files" section in the PDF.
    """

    # ==================================================================
    # INITIALIZATION
    # ==================================================================

    def __init__(self):
        print("ReportGenerator initialized.")

    # ==================================================================
    # PUBLIC ENTRY POINT
    # ==================================================================

    def generate(self, inspection):
        if not isinstance(inspection, dict):
            raise TypeError("inspection must be a dictionary.")

        session_id = inspection.get("session_id")

        if not session_id:
            raise ValueError("Inspection session_id is missing.")

        print("\n" + "=" * 70)
        print("REPORT GENERATION")
        print("=" * 70)
        print(f"Generating reports for inspection: {session_id}")

        # --------------------------------------------------------------
        # Resolve inspection output directory
        # --------------------------------------------------------------

        output_dir = self._resolve_output_directory(inspection)

        os.makedirs(output_dir, exist_ok=True)

        print("Report output directory:", output_dir)

        # --------------------------------------------------------------
        # IMPORTANT:
        # Resolve/copy visualization images BEFORE building JSON.
        #
        # This is the key fix for the missing damage images.
        # --------------------------------------------------------------

        damage_visualizations = (
            self._prepare_damage_visualizations(
                inspection=inspection,
                output_dir=output_dir,
            )
        )

        vehicle_part_visualizations = (
            self._prepare_vehicle_part_visualizations(
                inspection=inspection,
                output_dir=output_dir,
            )
        )

        # Store normalized/copied paths back into inspection.
        inspection["damage_visualizations"] = (
            damage_visualizations
        )

        inspection["vehicle_part_visualizations"] = (
            vehicle_part_visualizations
        )

        # --------------------------------------------------------------
        # Build final report
        # --------------------------------------------------------------

        report = self._build_report(inspection)

        # --------------------------------------------------------------
        # JSON
        # --------------------------------------------------------------

        json_path = os.path.join(
            output_dir,
            "final_inspection_report.json",
        )

        print("\nSaving JSON report...")

        self._write_json(
            report,
            json_path,
        )

        self._validate_file(
            json_path,
            "JSON report",
        )

        print(
            "JSON report generated:",
            json_path,
        )

        inspection["final_report_export"] = {
            "path": json_path,
            "format": "json",
            "status": "ready",
            "validated": True,
        }

        # --------------------------------------------------------------
        # PDF
        # --------------------------------------------------------------

        pdf_path = os.path.join(
            output_dir,
            "final_inspection_report.pdf",
        )

        print("\nGenerating PDF report...")

        self._generate_pdf(
            report=report,
            pdf_path=pdf_path,
            json_path=json_path,
        )

        self._validate_file(
            pdf_path,
            "PDF report",
        )

        print(
            "PDF report generated:",
            pdf_path,
        )

        inspection["final_report_pdf"] = {
            "path": pdf_path,
            "format": "pdf",
            "status": "ready",
            "source_json": json_path,
            "validated": True,
            "damage_visualizations_included": len(
                damage_visualizations
            ),
            "vehicle_part_visualizations_included": len(
                vehicle_part_visualizations
            ),
        }

        # --------------------------------------------------------------
        # Store final report
        # --------------------------------------------------------------

        inspection["final_report"] = report
        inspection["report_generation_complete"] = True

        # --------------------------------------------------------------
        # Final validation
        # --------------------------------------------------------------

        self._validate_report_outputs(inspection)

        print("\n" + "-" * 70)
        print("REPORT GENERATION COMPLETE")
        print("-" * 70)

        print("JSON:", json_path)
        print("PDF :", pdf_path)
        print("JSON valid:", True)
        print("PDF valid:", True)

        return inspection

    # ==================================================================
    # OUTPUT DIRECTORY
    # ==================================================================

    def _resolve_output_directory(self, inspection):

        session_id = inspection["session_id"]

        existing_dir = inspection.get(
            "report_output_dir"
        )

        if existing_dir:
            path = os.path.abspath(existing_dir)
            inspection["report_output_dir"] = path
            return path

        existing_dir = inspection.get(
            "inspection_output_dir"
        )

        if existing_dir:
            path = os.path.abspath(existing_dir)
            inspection["report_output_dir"] = path
            return path

        video_path = inspection.get("video_path")

        if video_path:

            video_path = os.path.abspath(video_path)

            # Walk upward looking for the project root.
            current = os.path.dirname(video_path)

            while current and current != os.path.dirname(current):

                candidate = os.path.join(
                    current,
                    "reports",
                    "inspections",
                )

                if os.path.isdir(candidate):

                    path = os.path.join(
                        candidate,
                        session_id,
                    )

                    os.makedirs(
                        path,
                        exist_ok=True,
                    )

                    inspection[
                        "report_output_dir"
                    ] = path

                    return path

                current = os.path.dirname(current)

            # Standard project layout fallback.
            project_root = os.path.dirname(
                os.path.dirname(video_path)
            )

            path = os.path.join(
                project_root,
                "reports",
                "inspections",
                session_id,
            )

            os.makedirs(
                path,
                exist_ok=True,
            )

            inspection[
                "report_output_dir"
            ] = path

            return path

        path = os.path.join(
            os.getcwd(),
            "reports",
            "inspections",
            session_id,
        )

        os.makedirs(
            path,
            exist_ok=True,
        )

        inspection[
            "report_output_dir"
        ] = path

        return path

    # ==================================================================
    # BUILD FINAL REPORT
    # ==================================================================

    def _build_report(self, inspection):

        session_id = inspection.get(
            "session_id"
        )

        observed_views = (
            self._resolve_observed_views(
                inspection
            )
        )

        damages = self._resolve_damages(
            inspection
        )

        damage_summary = (
            self._build_damage_summary(
                inspection,
                damages,
                observed_views,
            )
        )

        vehicle_parts = (
            self._resolve_vehicle_parts(
                inspection
            )
        )

        vehicle_part_summary = (
            self._build_vehicle_part_summary(
                inspection,
                vehicle_parts,
                observed_views,
            )
        )

        damage_visualizations = (
            self._resolve_damage_visualizations(
                inspection
            )
        )

        vehicle_part_visualizations = (
            self._resolve_vehicle_part_visualizations(
                inspection
            )
        )

        association_data = inspection.get(
            "damage_part_associations",
            {},
        )

        if not isinstance(
            association_data,
            dict,
        ):
            association_data = {}

        inspection_summary = {
            "session_id": session_id,
            "video_name": inspection.get(
                "video_name"
            ),
            "video_path": inspection.get(
                "video_path"
            ),
            "total_frames": inspection.get(
                "total_frames"
            ),
            "fps": inspection.get(
                "fps"
            ),
            "primary_vehicle": inspection.get(
                "primary_vehicle"
            ),
            "start_time": self._format_datetime(
                inspection.get(
                    "start_time"
                )
            ),
            "end_time": self._format_datetime(
                inspection.get(
                    "end_time"
                )
            ),
            "coverage_complete": bool(
                inspection.get(
                    "coverage_complete",
                    False,
                )
            ),
            "observed_views": observed_views,
            "missing_views": [
                view
                for view in [
                    "front",
                    "rear",
                    "left",
                    "right",
                ]
                if view not in observed_views
            ],
            "report_generated_at": (
                datetime.now().strftime(
                    "%d %b %Y, %H:%M:%S"
                )
            ),
        }

        return {
            "report_version": "1.1",

            "inspection_summary":
                inspection_summary,

            "representative_views":
                self._resolve_representative_views(
                    inspection
                ),

            "damage_summary":
                damage_summary,

            "damages":
                damages,

            "vehicle_part_summary":
                vehicle_part_summary,

            "vehicle_parts":
                vehicle_parts,

            "damage_visualizations":
                damage_visualizations,

            "vehicle_part_visualizations":
                vehicle_part_visualizations,

            "damage_part_associations":
                association_data,

            "inspection_evaluation":
                inspection.get(
                    "evaluation",
                    inspection.get(
                        "inspection_evaluation",
                        {},
                    ),
                ),

            "report_metadata": {
                "generated_at":
                    datetime.now().strftime(
                        "%d %b %Y, %H:%M:%S"
                    ),
                "generator":
                    "Vehicle Inspection AI",
                "format":
                    "final_inspection_report",
            },
        }

    # ==================================================================
    # DATETIME
    # ==================================================================

    def _format_datetime(self, value):

        if value is None:
            return "—"

        if isinstance(value, datetime):
            return value.strftime(
                "%d %b %Y, %H:%M:%S"
            )

        text = str(value).strip()

        if not text:
            return "—"

        try:
            parsed = datetime.fromisoformat(
                text.replace(
                    "Z",
                    "+00:00",
                )
            )

            return parsed.strftime(
                "%d %b %Y, %H:%M:%S"
            )

        except Exception:
            return text

    # ==================================================================
    # OBSERVED VIEWS
    # ==================================================================

    def _resolve_observed_views(self, inspection):

        observed = inspection.get(
            "observed_views"
        )

        if isinstance(
            observed,
            list,
        ):
            return self._unique_views(
                observed
            )

        coverage = inspection.get(
            "coverage"
        )

        if isinstance(
            coverage,
            dict,
        ):

            views = []

            for view in [
                "front",
                "rear",
                "left",
                "right",
            ]:

                value = coverage.get(view)

                if isinstance(
                    value,
                    dict,
                ):

                    if value.get(
                        "covered",
                        False,
                    ):
                        views.append(view)

                elif value:
                    views.append(view)

            if views:
                return self._unique_views(
                    views
                )

        representative = inspection.get(
            "representative_frames"
        )

        if isinstance(
            representative,
            dict,
        ):

            views = [
                view
                for view in [
                    "front",
                    "rear",
                    "left",
                    "right",
                ]
                if representative.get(view)
            ]

            if views:
                return self._unique_views(
                    views
                )

        views = []

        damages = inspection.get(
            "damages",
            [],
        )

        if isinstance(
            damages,
            list,
        ):

            for damage in damages:

                if not isinstance(
                    damage,
                    dict,
                ):
                    continue

                view = damage.get("view")

                if view:
                    views.append(
                        str(view).lower()
                    )

        vehicle_parts = inspection.get(
            "vehicle_parts",
            {},
        )

        if isinstance(
            vehicle_parts,
            dict,
        ):

            views.extend(
                str(view).lower()
                for view in vehicle_parts.keys()
                if view
            )

        return self._unique_views(
            views
        )

    # ==================================================================
    # UNIQUE VIEWS
    # ==================================================================

    def _unique_views(self, views):

        preferred = [
            "front",
            "rear",
            "left",
            "right",
        ]

        normalized = []

        for view in views:

            if view is None:
                continue

            view = str(
                view
            ).lower().strip()

            if not view:
                continue

            if view not in normalized:
                normalized.append(view)

        ordered = [
            view
            for view in preferred
            if view in normalized
        ]

        for view in normalized:

            if view not in ordered:
                ordered.append(view)

        return ordered

    # ==================================================================
    # REPRESENTATIVE VIEWS
    # ==================================================================

    def _resolve_representative_views(
        self,
        inspection,
    ):

        value = inspection.get(
            "representative_views"
        )

        if value is not None:
            return value

        value = inspection.get(
            "representative_frames"
        )

        if value is not None:
            return value

        return {}

    # ==================================================================
    # DAMAGE RESOLUTION
    # ==================================================================

    def _resolve_damages(
            self,
            inspection,
    ):
        """
        Resolve and normalize damage detections.

        DamagePipeline stores detections grouped by vehicle view:

            {
                "front": [...],
                "rear": [...],
                "left": [...],
                "right": [...]
            }

        The final report uses a flat list:

            [
                {
                    "damage_id": "DAMAGE_0001",
                    "view": "front",
                    ...
                }
            ]

        This method supports both structures so that the report
        generator remains compatible with older pipeline results.
        """

        damages = inspection.get(
            "damages",
            {},
        )

        normalized = []

        # ==============================================================
        # CASE 1
        #
        # DamagePipeline structure:
        #
        # {
        #     "front": [...],
        #     "rear": [...],
        #     "left": [...],
        #     "right": [...]
        # }
        # ==============================================================

        if isinstance(
                damages,
                dict,
        ):

            damage_counter = 1

            # Process views in a predictable order.
            ordered_views = [
                "front",
                "rear",
                "left",
                "right",
            ]

            # First process standard vehicle views.
            views = []

            for view in ordered_views:

                if view in damages:
                    views.append(view)

            # Then preserve any additional/custom views.
            for view in damages.keys():

                if view not in views:
                    views.append(view)

            for view in views:

                view_damages = damages.get(
                    view,
                    [],
                )

                if not isinstance(
                        view_damages,
                        list,
                ):
                    continue

                for damage in view_damages:

                    if not isinstance(
                            damage,
                            dict,
                    ):
                        continue

                    item = dict(
                        damage
                    )

                    # --------------------------------------------------
                    # Preserve the view from the pipeline.
                    #
                    # Do not overwrite an explicitly supplied view.
                    # --------------------------------------------------

                    if not item.get(
                            "view"
                    ):
                        item["view"] = str(
                            view
                        ).lower().strip()

                    # --------------------------------------------------
                    # Assign a damage ID if the detector did not provide
                    # one.
                    # --------------------------------------------------

                    if not item.get(
                            "damage_id"
                    ):
                        item["damage_id"] = (
                            f"DAMAGE_{damage_counter:04d}"
                        )

                    normalized.append(
                        item
                    )

                    damage_counter += 1

            return normalized

        # ==============================================================
        # CASE 2
        #
        # Already-flat damage list:
        #
        # [
        #     {...},
        #     {...}
        # ]
        #
        # Keep support for this structure as well.
        # ==============================================================

        if isinstance(
                damages,
                list,
        ):

            for index, damage in enumerate(
                    damages,
                    start=1,
            ):

                if not isinstance(
                        damage,
                        dict,
                ):
                    continue

                item = dict(
                    damage
                )

                if not item.get(
                        "damage_id"
                ):
                    item["damage_id"] = (
                        f"DAMAGE_{index:04d}"
                    )

                normalized.append(
                    item
                )

            return normalized

        # ==============================================================
        # CASE 3
        #
        # Unexpected structure.
        #
        # Return an empty list rather than allowing malformed data to
        # break report generation.
        # ==============================================================

        return normalized

    # ==================================================================
    # DAMAGE SUMMARY
    # ==================================================================

    def _build_damage_summary(
        self,
        inspection,
        damages,
        views,
    ):

        existing = inspection.get(
            "damage_summary"
        )

        if isinstance(
            existing,
            dict,
        ):
            summary = dict(existing)
        else:
            summary = {}

        for view in views:

            summary[view] = sum(
                1
                for damage in damages
                if str(
                    damage.get(
                        "view",
                        "",
                    )
                ).lower()
                == view
            )

        summary["total"] = len(damages)

        return summary

    # ==================================================================
    # VEHICLE PARTS
    # ==================================================================

    def _resolve_vehicle_parts(
        self,
        inspection,
    ):

        parts = inspection.get(
            "vehicle_parts",
            {},
        )

        if isinstance(
            parts,
            dict,
        ):
            return parts

        return {}

    # ==================================================================
    # VEHICLE PART SUMMARY
    # ==================================================================

    def _build_vehicle_part_summary(
        self,
        inspection,
        vehicle_parts,
        views,
    ):

        existing = inspection.get(
            "vehicle_part_summary"
        )

        if isinstance(
            existing,
            dict,
        ):
            summary = dict(existing)
        else:
            summary = {}

        total = 0

        for view in views:

            parts = vehicle_parts.get(
                view,
                [],
            )

            if isinstance(
                parts,
                list,
            ):

                count = len([
                    part
                    for part in parts
                    if isinstance(
                        part,
                        dict,
                    )
                ])

            else:
                count = 0

            summary[view] = count
            total += count

        summary["total"] = total

        return summary

    # ==================================================================
    # DAMAGE VISUALIZATION PREPARATION
    # ==================================================================

    def _prepare_damage_visualizations(
        self,
        inspection,
        output_dir,
    ):
        """
        Find every available damage visualization, copy it into the
        inspection directory, and return references to the copied files.

        This deliberately checks multiple possible locations because
        different pipeline implementations may store visualization
        references under different keys.
        """

        destination_dir = os.path.join(
            output_dir,
            "damage_visualizations",
        )

        os.makedirs(
            destination_dir,
            exist_ok=True,
        )

        candidates = []

        # --------------------------------------------------------------
        # Direct inspection keys
        # --------------------------------------------------------------

        for key in [
            "damage_visualizations",
            "damage_visualization_paths",
            "damage_visualization_files",
        ]:

            value = inspection.get(key)

            if value is not None:
                candidates.append(value)

        # --------------------------------------------------------------
        # Damage pipeline results
        # --------------------------------------------------------------

        for key in [
            "damage_results",
            "damage_detection_results",
            "damage_pipeline",
            "damage_detection",
        ]:

            value = inspection.get(key)

            if value is not None:
                candidates.append(value)

        # --------------------------------------------------------------
        # Flatten candidate references by view
        # --------------------------------------------------------------

        flattened = {}

        for candidate in candidates:

            self._collect_visualization_candidates(
                candidate,
                flattened,
            )

        # --------------------------------------------------------------
        # Also search likely directories.
        #
        # This is important when the damage pipeline generated images
        # but did not put their paths into the inspection dictionary.
        # --------------------------------------------------------------

        # search_dirs = []
        #
        # report_dir = os.path.abspath(
        #     output_dir
        # )
        #
        # search_dirs.extend([
        #     report_dir,
        #     os.path.dirname(report_dir),
        #     os.path.join(
        #         report_dir,
        #         "damage_visualizations",
        #     ),
        #     os.path.join(
        #         report_dir,
        #         "visualizations",
        #     ),
        # ])
        #
        # video_path = inspection.get(
        #     "video_path"
        # )
        #
        # if video_path:
        #
        #     video_dir = os.path.dirname(
        #         os.path.abspath(
        #             video_path
        #         )
        #     )
        #
        #     search_dirs.extend([
        #         video_dir,
        #         os.path.join(
        #             video_dir,
        #             "reports",
        #         ),
        #         os.path.join(
        #             video_dir,
        #             "damage_visualizations",
        #         ),
        #         os.path.join(
        #             video_dir,
        #             "visualizations",
        #         ),
        #     ])
        #
        # # Search recursively for obvious damage visualization files.
        # filesystem_files = self._find_damage_images(
        #     search_dirs
        # )
        #
        # for path in filesystem_files:
        #
        #     view = self._infer_view_from_filename(
        #         path
        #     )
        #
        #     if view and view not in flattened:
        #         flattened[view] = path

        # --------------------------------------------------------------
        # Copy files
        # --------------------------------------------------------------

        normalized = {}

        for view, reference in flattened.items():

            source_path = self._resolve_source_path(
                reference,
                output_dir,
                inspection,
            )

            if not source_path:
                print(
                    f"WARNING: Could not resolve damage "
                    f"visualization for view '{view}': "
                    f"{reference}"
                )
                continue

            if not os.path.isfile(
                source_path
            ):
                print(
                    f"WARNING: Damage visualization does not exist: "
                    f"{source_path}"
                )
                continue

            safe_view = (
                str(view)
                .lower()
                .strip()
                .replace(" ", "_")
            )

            extension = os.path.splitext(
                source_path
            )[1].lower()

            if not extension:
                extension = ".jpg"

            destination = os.path.join(
                destination_dir,
                f"{safe_view}_damage_visualization{extension}",
            )

            # Avoid copying a file onto itself.
            if os.path.abspath(
                source_path
            ) != os.path.abspath(
                destination
            ):

                shutil.copy2(
                    source_path,
                    destination,
                )

            if not os.path.isfile(
                destination
            ):
                print(
                    f"WARNING: Failed to copy damage "
                    f"visualization: {source_path}"
                )
                continue

            normalized[view] = {
                "path": os.path.abspath(
                    destination
                ),
                "source_path": os.path.abspath(
                    source_path
                ),
                "type": "damage_visualization",
                "view": view,
                "exists": True,
                "size_bytes": os.path.getsize(
                    destination
                ),
            }

            print(
                f"Damage visualization prepared "
                f"[{view}]: {destination}"
            )

        return normalized

    # ==================================================================
    # COLLECT VISUALIZATION CANDIDATES
    # ==================================================================

    def _collect_visualization_candidates(
        self,
        value,
        output,
        current_view=None,
    ):
        """
        Recursively inspect arbitrary pipeline result structures and
        extract image references.
        """

        if value is None:
            return

        # --------------------------------------------------------------
        # String
        # --------------------------------------------------------------

        if isinstance(
            value,
            str,
        ):

            lower = value.lower()

            if (
                lower.endswith(".jpg")
                or lower.endswith(".jpeg")
                or lower.endswith(".png")
                or lower.endswith(".webp")
            ):

                view = (
                    current_view
                    or self._infer_view_from_filename(
                        value
                    )
                )

                if view:
                    output.setdefault(
                        view,
                        value,
                    )

            return

        # --------------------------------------------------------------
        # Dictionary
        # --------------------------------------------------------------

        if isinstance(
            value,
            dict,
        ):

            detected_view = current_view

            for key in [
                "view",
                "vehicle_view",
                "camera_view",
                "side",
            ]:

                candidate_view = value.get(key)

                if candidate_view:

                    detected_view = (
                        str(
                            candidate_view
                        ).lower().strip()
                    )

                    break

            # Common image-path keys.
            for key in [
                "path",
                "image_path",
                "visualization_path",
                "file_path",
                "filepath",
                "output_path",
                "image",
                "visualization",
                "damage_visualization",
            ]:

                candidate = value.get(key)

                if isinstance(
                    candidate,
                    str,
                ):

                    lower = candidate.lower()

                    if (
                        lower.endswith(".jpg")
                        or lower.endswith(".jpeg")
                        or lower.endswith(".png")
                        or lower.endswith(".webp")
                    ):

                        view = (
                            detected_view
                            or self._infer_view_from_filename(
                                candidate
                            )
                        )

                        if view:
                            output.setdefault(
                                view,
                                candidate,
                            )

            # Recurse.
            for key, child in value.items():

                child_view = detected_view

                key_lower = str(
                    key
                ).lower()

                if key_lower in [
                    "front",
                    "rear",
                    "left",
                    "right",
                ]:
                    child_view = key_lower

                self._collect_visualization_candidates(
                    child,
                    output,
                    child_view,
                )

            return

        # --------------------------------------------------------------
        # Lists / tuples / sets
        # --------------------------------------------------------------

        if isinstance(
            value,
            (list, tuple, set),
        ):

            for child in value:

                self._collect_visualization_candidates(
                    child,
                    output,
                    current_view,
                )

    # ==================================================================
    # SEARCH DAMAGE IMAGES
    # ==================================================================

    def _find_damage_images(
        self,
        directories,
    ):

        found = []

        visited = set()

        for directory in directories:

            if not directory:
                continue

            directory = os.path.abspath(
                directory
            )

            if directory in visited:
                continue

            visited.add(directory)

            if not os.path.isdir(
                directory
            ):
                continue

            try:

                for root, _, files in os.walk(
                    directory
                ):

                    for filename in files:

                        lower = filename.lower()

                        if not (
                            lower.endswith(".jpg")
                            or lower.endswith(".jpeg")
                            or lower.endswith(".png")
                            or lower.endswith(".webp")
                        ):
                            continue

                        if not any(
                            token in lower
                            for token in [
                                "damage",
                                "damages",
                                "defect",
                                "inspection",
                            ]
                        ):
                            continue

                        path = os.path.join(
                            root,
                            filename,
                        )

                        if path not in found:
                            found.append(path)

            except Exception as exc:

                print(
                    "WARNING: Could not search "
                    f"{directory}: {exc}"
                )

        return found

    # ==================================================================
    # INFER VIEW FROM FILENAME
    # ==================================================================

    def _infer_view_from_filename(
        self,
        path,
    ):

        if not path:
            return None

        name = os.path.basename(
            str(path)
        ).lower()

        for view in [
            "front",
            "rear",
            "left",
            "right",
        ]:

            if view in name:
                return view

        return None

    # ==================================================================
    # RESOLVE SOURCE PATH
    # ==================================================================

    def _resolve_source_path(
        self,
        reference,
        output_dir,
        inspection,
    ):

        if isinstance(
            reference,
            dict,
        ):

            reference = (
                reference.get("path")
                or reference.get("image_path")
                or reference.get("visualization_path")
                or reference.get("file_path")
                or reference.get("filepath")
                or reference.get("output_path")
            )

        if not reference:
            return None

        reference = str(
            reference
        )

        if os.path.isabs(
            reference
        ):

            if os.path.isfile(
                reference
            ):
                return reference

        candidates = [
            reference,
            os.path.join(
                output_dir,
                reference,
            ),
            os.path.join(
                os.path.dirname(output_dir),
                reference,
            ),
        ]

        video_path = inspection.get(
            "video_path"
        )

        if video_path:

            video_dir = os.path.dirname(
                os.path.abspath(
                    video_path
                )
            )

            candidates.extend([
                os.path.join(
                    video_dir,
                    reference,
                ),
                os.path.join(
                    video_dir,
                    os.path.basename(
                        reference
                    ),
                ),
            ])

        for candidate in candidates:

            candidate = os.path.abspath(
                candidate
            )

            if os.path.isfile(
                candidate
            ):
                return candidate

        # Last resort: search by basename.
        basename = os.path.basename(
            reference
        )

        if basename:

            roots = [
                output_dir,
            ]

            if video_path:
                roots.append(
                    os.path.dirname(
                        os.path.abspath(
                            video_path
                        )
                    )
                )

            for root in roots:

                if not os.path.isdir(root):
                    continue

                for current_root, _, files in os.walk(
                    root
                ):

                    if basename in files:

                        return os.path.join(
                            current_root,
                            basename,
                        )

        return None

    # ==================================================================
    # VEHICLE PART VISUALIZATIONS
    # ==================================================================

    def _prepare_vehicle_part_visualizations(
        self,
        inspection,
        output_dir,
    ):

        destination_dir = os.path.join(
            output_dir,
            "vehicle_part_visualizations",
        )

        os.makedirs(
            destination_dir,
            exist_ok=True,
        )

        candidates = []

        for key in [
            "vehicle_part_visualizations",
            "vehicle_part_visualization_paths",
            "vehicle_part_visualization_files",
        ]:

            value = inspection.get(key)

            if value is not None:
                candidates.append(value)

        flattened = {}

        for candidate in candidates:

            self._collect_visualization_candidates(
                candidate,
                flattened,
            )

        normalized = {}

        for view, reference in flattened.items():

            source_path = self._resolve_source_path(
                reference,
                output_dir,
                inspection,
            )

            if not source_path:
                continue

            if not os.path.isfile(
                source_path
            ):
                continue

            safe_view = (
                str(view)
                .lower()
                .strip()
                .replace(" ", "_")
            )

            extension = os.path.splitext(
                source_path
            )[1].lower()

            if not extension:
                extension = ".jpg"

            destination = os.path.join(
                destination_dir,
                f"{safe_view}_vehicle_parts{extension}",
            )

            if os.path.abspath(
                source_path
            ) != os.path.abspath(
                destination
            ):

                shutil.copy2(
                    source_path,
                    destination,
                )

            if not os.path.isfile(
                destination
            ):
                continue

            normalized[view] = {
                "path": os.path.abspath(
                    destination
                ),
                "source_path": os.path.abspath(
                    source_path
                ),
                "type": "vehicle_part_visualization",
                "view": view,
                "exists": True,
                "size_bytes": os.path.getsize(
                    destination
                ),
            }

        return normalized

    # ==================================================================
    # RESOLVE DAMAGE VISUALIZATIONS
    # ==================================================================

    def _resolve_damage_visualizations(
        self,
        inspection,
    ):

        value = inspection.get(
            "damage_visualizations",
            {},
        )

        if isinstance(
            value,
            dict,
        ):
            return self._normalize_visualization_dict(
                value
            )

        return {}

    # ==================================================================
    # RESOLVE PART VISUALIZATIONS
    # ==================================================================

    def _resolve_vehicle_part_visualizations(
        self,
        inspection,
    ):

        value = inspection.get(
            "vehicle_part_visualizations",
            {},
        )

        if isinstance(
            value,
            dict,
        ):
            return self._normalize_visualization_dict(
                value
            )

        return {}

    # ==================================================================
    # NORMALIZE VISUALIZATION DICT
    # ==================================================================

    def _normalize_visualization_dict(
        self,
        data,
    ):

        normalized = {}

        for key, value in data.items():

            if isinstance(
                value,
                str,
            ):

                normalized[key] = {
                    "path": value,
                    "exists": os.path.isfile(
                        value
                    ),
                }

            elif isinstance(
                value,
                dict,
            ):

                item = dict(value)

                path = (
                    item.get("path")
                    or item.get("image_path")
                    or item.get(
                        "visualization_path"
                    )
                )

                if path:
                    item["path"] = path
                    item["exists"] = os.path.isfile(
                        path
                    )

                normalized[key] = item

        return normalized

    # ==================================================================
    # WRITE JSON
    # ==================================================================

    def _write_json(
        self,
        report,
        path,
    ):

        os.makedirs(
            os.path.dirname(path),
            exist_ok=True,
        )

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                report,
                f,
                indent=2,
                ensure_ascii=False,
                default=str,
            )

    # ==================================================================
    # VALIDATE FILE
    # ==================================================================

    def _validate_file(
        self,
        path,
        description,
    ):

        if not path:
            raise ValueError(
                f"{description} path is missing."
            )

        if not os.path.isfile(
            path
        ):
            raise FileNotFoundError(
                f"{description} was not created: {path}"
            )

        size = os.path.getsize(
            path
        )

        if size <= 0:
            raise ValueError(
                f"{description} is empty: {path}"
            )

        return True

    # ==================================================================
    # VALIDATE REPORT OUTPUTS
    # ==================================================================

    def _validate_report_outputs(
        self,
        inspection,
    ):

        json_ref = inspection.get(
            "final_report_export"
        )

        pdf_ref = inspection.get(
            "final_report_pdf"
        )

        if not isinstance(
            json_ref,
            dict,
        ):
            raise ValueError(
                "final_report_export was not stored."
            )

        if not isinstance(
            pdf_ref,
            dict,
        ):
            raise ValueError(
                "final_report_pdf was not stored."
            )

        json_path = json_ref.get("path")
        pdf_path = pdf_ref.get("path")

        self._validate_file(
            json_path,
            "JSON report",
        )

        self._validate_file(
            pdf_path,
            "PDF report",
        )

        with open(
            json_path,
            "r",
            encoding="utf-8",
        ) as f:

            loaded = json.load(f)

        required_sections = [
            "inspection_summary",
            "representative_views",
            "damage_summary",
            "damages",
            "vehicle_part_summary",
            "vehicle_parts",
            "damage_visualizations",
            "vehicle_part_visualizations",
        ]

        missing = [
            key
            for key in required_sections
            if key not in loaded
        ]

        if missing:
            raise ValueError(
                "Final JSON report is missing required "
                f"sections: {missing}"
            )

        # --------------------------------------------------------------
        # Validate visualization files actually exist.
        # --------------------------------------------------------------

        for section_name in [
            "damage_visualizations",
            "vehicle_part_visualizations",
        ]:

            visualizations = loaded.get(
                section_name,
                {},
            )

            if not isinstance(
                visualizations,
                dict,
            ):
                continue

            for view, item in visualizations.items():

                if not isinstance(
                    item,
                    dict,
                ):
                    continue

                path = item.get("path")

                if path and not os.path.isfile(
                    path
                ):
                    raise FileNotFoundError(
                        f"{section_name} for '{view}' "
                        f"does not exist: {path}"
                    )

        return True

    # ==================================================================
    # PDF GENERATION
    # ==================================================================

    def _generate_pdf(
        self,
        report,
        pdf_path,
        json_path,
    ):

        try:

            from reportlab.lib import colors
            from reportlab.lib.enums import TA_CENTER
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import (
                getSampleStyleSheet,
                ParagraphStyle,
            )
            from reportlab.lib.units import mm
            from reportlab.platypus import (
                SimpleDocTemplate,
                Paragraph,
                Spacer,
                Table,
                TableStyle,
                Image,
                PageBreak,
            )

        except ImportError as exc:

            raise ImportError(
                "ReportLab is required for PDF generation. "
                "Install it with: pip install reportlab"
            ) from exc

        summary = report.get(
            "inspection_summary",
            {},
        )

        damage_summary = report.get(
            "damage_summary",
            {},
        )

        vehicle_part_summary = report.get(
            "vehicle_part_summary",
            {},
        )

        damages = report.get(
            "damages",
            [],
        )

        vehicle_parts = report.get(
            "vehicle_parts",
            {},
        )

        damage_visualizations = report.get(
            "damage_visualizations",
            {},
        )

        vehicle_part_visualizations = report.get(
            "vehicle_part_visualizations",
            {},
        )

        association_data = report.get(
            "damage_part_associations",
            {},
        )

        if not isinstance(
            association_data,
            dict,
        ):
            association_data = {}

        association_confirmed = bool(
            association_data.get(
                "confirmed",
                False,
            )
        )

        association_records = (
            association_data.get(
                "records",
                [],
            )
        )

        if not isinstance(
            association_records,
            list,
        ):
            association_records = []

        views = summary.get(
            "observed_views",
            [],
        )

        # --------------------------------------------------------------
        # Styles
        # --------------------------------------------------------------

        styles = getSampleStyleSheet()

        styles.add(
            ParagraphStyle(
                name="ReportTitle",
                parent=styles["Title"],
                fontName="Helvetica-Bold",
                fontSize=22,
                leading=27,
                textColor=colors.HexColor(
                    "#111827"
                ),
                alignment=TA_CENTER,
                spaceAfter=8,
            )
        )

        styles.add(
            ParagraphStyle(
                name="ReportSubtitle",
                parent=styles["Normal"],
                fontSize=10,
                leading=14,
                textColor=colors.HexColor(
                    "#6B7280"
                ),
                alignment=TA_CENTER,
                spaceAfter=12,
            )
        )

        styles.add(
            ParagraphStyle(
                name="SectionTitle",
                parent=styles["Heading2"],
                fontName="Helvetica-Bold",
                fontSize=14,
                leading=18,
                textColor=colors.HexColor(
                    "#111827"
                ),
                spaceBefore=8,
                spaceAfter=5,
            )
        )

        styles.add(
            ParagraphStyle(
                name="BodySmall",
                parent=styles["BodyText"],
                fontSize=9,
                leading=13,
                textColor=colors.HexColor(
                    "#374151"
                ),
            )
        )

        styles.add(
            ParagraphStyle(
                name="BodyTiny",
                parent=styles["BodyText"],
                fontSize=7.5,
                leading=10,
                textColor=colors.HexColor(
                    "#4B5563"
                ),
            )
        )

        styles.add(
            ParagraphStyle(
                name="Finding",
                parent=styles["BodyText"],
                fontSize=10,
                leading=14,
                textColor=colors.HexColor(
                    "#111827"
                ),
            )
        )

        styles.add(
            ParagraphStyle(
                name="Warning",
                parent=styles["BodyText"],
                fontSize=9,
                leading=13,
                textColor=colors.HexColor(
                    "#92400E"
                ),
                backColor=colors.HexColor(
                    "#FEF3C7"
                ),
                borderPadding=7,
            )
        )

        # --------------------------------------------------------------
        # Helpers
        # --------------------------------------------------------------

        def safe_text(
            value,
            default="—",
        ):

            if value is None:
                return default

            if isinstance(
                value,
                bool,
            ):
                return (
                    "Yes"
                    if value
                    else "No"
                )

            if isinstance(
                value,
                float,
            ):
                return f"{value:.2f}"

            return html.escape(
                str(value)
            )

        def format_confidence(value):

            if value is None:
                return "—"

            try:
                return (
                    f"{float(value) * 100:.1f}%"
                )
            except Exception:
                return safe_text(value)

        def view_list_text(values):

            if not values:
                return "No representative views available"

            return ", ".join(
                str(view).title()
                for view in values
            )

        def add_section_title(
            story,
            title,
        ):

            story.append(
                Spacer(
                    1,
                    5 * mm,
                )
            )

            story.append(
                Paragraph(
                    title,
                    styles["SectionTitle"],
                )
            )

            story.append(
                Spacer(
                    1,
                    2 * mm,
                )
            )

        def make_table(
            data,
            col_widths=None,
            header=True,
        ):

            table = Table(
                data,
                colWidths=col_widths,
                repeatRows=(
                    1
                    if header
                    else 0
                ),
                hAlign="LEFT",
            )

            commands = [
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.HexColor(
                        "#D1D5DB"
                    ),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]

            if header:

                commands.extend([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.HexColor(
                            "#1F2937"
                        ),
                    ),
                    (
                        "TEXTCOLOR",
                        (0, 0),
                        (-1, 0),
                        colors.white,
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold",
                    ),
                ])

            table.setStyle(
                TableStyle(commands)
            )

            return table

        def resolve_visualization_path(
            visualization,
        ):

            if isinstance(
                visualization,
                str,
            ):
                path = visualization

            elif isinstance(
                visualization,
                dict,
            ):
                path = (
                    visualization.get(
                        "path"
                    )
                    or visualization.get(
                        "image_path"
                    )
                    or visualization.get(
                        "visualization_path"
                    )
                )

            else:
                path = None

            if not path:
                return None

            path = os.path.abspath(
                str(path)
            )

            if os.path.isfile(
                path
            ):
                return path

            return None

        def add_image_file(
            story,
            image_path,
            max_width=165 * mm,
            max_height=100 * mm,
        ):

            if not image_path:
                return False

            image_path = os.path.abspath(
                str(image_path)
            )

            if not os.path.isfile(
                image_path
            ):
                print(
                    "PDF image missing:",
                    image_path,
                )
                return False

            try:

                img = Image(
                    image_path
                )

                if (
                    img.imageWidth <= 0
                    or img.imageHeight <= 0
                ):
                    return False

                scale = min(
                    max_width
                    / img.imageWidth,
                    max_height
                    / img.imageHeight,
                )

                img.drawWidth = (
                    img.imageWidth
                    * scale
                )

                img.drawHeight = (
                    img.imageHeight
                    * scale
                )

                story.append(
                    img
                )

                return True

            except Exception as exc:

                print(
                    "PDF image loading error:",
                    image_path,
                    exc,
                )

                story.append(
                    Paragraph(
                        "Image could not be loaded: "
                        + safe_text(exc),
                        styles["BodyTiny"],
                    )
                )

                return False

        # --------------------------------------------------------------
        # Header / footer
        # --------------------------------------------------------------

        def draw_page_header_footer(
            canvas,
            doc,
        ):

            canvas.saveState()

            width, height = A4

            canvas.setStrokeColor(
                colors.HexColor(
                    "#E5E7EB"
                )
            )

            canvas.line(
                18 * mm,
                height - 15 * mm,
                width - 18 * mm,
                height - 15 * mm,
            )

            canvas.setFont(
                "Helvetica",
                7,
            )

            canvas.setFillColor(
                colors.HexColor(
                    "#6B7280"
                )
            )

            canvas.drawString(
                18 * mm,
                height - 12 * mm,
                "Vehicle Inspection Report",
            )

            canvas.drawRightString(
                width - 18 * mm,
                height - 12 * mm,
                safe_text(
                    summary.get(
                        "session_id"
                    )
                ),
            )

            canvas.line(
                18 * mm,
                14 * mm,
                width - 18 * mm,
                14 * mm,
            )

            canvas.setFillColor(
                colors.HexColor(
                    "#9CA3AF"
                )
            )

            canvas.drawString(
                18 * mm,
                9 * mm,
                "Vehicle Inspection AI",
            )

            canvas.drawRightString(
                width - 18 * mm,
                9 * mm,
                f"Page {doc.page}",
            )

            canvas.restoreState()

        # --------------------------------------------------------------
        # Document
        # --------------------------------------------------------------

        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=18 * mm,
            leftMargin=18 * mm,
            topMargin=20 * mm,
            bottomMargin=18 * mm,
            title="Vehicle Inspection Report",
            author="Vehicle Inspection AI",
        )

        story = []

        # ==============================================================
        # TITLE
        # ==============================================================

        story.append(
            Spacer(
                1,
                15 * mm,
            )
        )

        story.append(
            Paragraph(
                "Vehicle Inspection Report",
                styles["ReportTitle"],
            )
        )

        story.append(
            Paragraph(
                "Inspection ID: "
                + safe_text(
                    summary.get(
                        "session_id"
                    )
                ),
                styles["ReportSubtitle"],
            )
        )

        story.append(
            Spacer(
                1,
                5 * mm,
            )
        )

        coverage_text = view_list_text(
            views
        )

        status_data = [
            [
                Paragraph(
                    "<b>Report status</b>",
                    styles["BodySmall"],
                ),
                Paragraph(
                    "READY",
                    styles["BodySmall"],
                ),
            ],
            [
                Paragraph(
                    "<b>Observed views</b>",
                    styles["BodySmall"],
                ),
                Paragraph(
                    safe_text(
                        coverage_text
                    ),
                    styles["BodySmall"],
                ),
            ],
            [
                Paragraph(
                    "<b>Detected damage</b>",
                    styles["BodySmall"],
                ),
                Paragraph(
                    safe_text(
                        damage_summary.get(
                            "total",
                            0,
                        )
                    ),
                    styles["BodySmall"],
                ),
            ],
            [
                Paragraph(
                    "<b>Vehicle parts identified</b>",
                    styles["BodySmall"],
                ),
                Paragraph(
                    safe_text(
                        vehicle_part_summary.get(
                            "total",
                            0,
                        )
                    ),
                    styles["BodySmall"],
                ),
            ],
        ]

        status_table = Table(
            status_data,
            colWidths=[
                55 * mm,
                105 * mm,
            ],
        )

        status_table.setStyle(
            TableStyle([
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.HexColor(
                        "#D1D5DB"
                    ),
                ),
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor(
                        "#F3F4F6"
                    ),
                ),
                (
                    "BACKGROUND",
                    (1, 0),
                    (1, 0),
                    colors.HexColor(
                        "#DCFCE7"
                    ),
                ),
                (
                    "TEXTCOLOR",
                    (1, 0),
                    (1, 0),
                    colors.HexColor(
                        "#166534"
                    ),
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ])
        )

        story.append(status_table)

        story.append(
            Spacer(
                1,
                8 * mm,
            )
        )

        story.append(
            Paragraph(
                "This report summarizes visible vehicle conditions "
                "identified by the inspection system. Model confidence "
                "values are provided for transparency and should not "
                "be interpreted as repair-cost estimates or definitive "
                "mechanical diagnoses.",
                styles["BodySmall"],
            )
        )

        # ==============================================================
        # 1. INSPECTION OVERVIEW
        # ==============================================================

        add_section_title(
            story,
            "1. Inspection Overview",
        )

        overview_data = [
            ["Item", "Details"],
            [
                "Inspection ID",
                safe_text(
                    summary.get(
                        "session_id"
                    )
                ),
            ],
            [
                "Video",
                safe_text(
                    summary.get(
                        "video_name"
                    )
                ),
            ],
            [
                "Total frames",
                safe_text(
                    summary.get(
                        "total_frames"
                    )
                ),
            ],
            [
                "Frame rate",
                safe_text(
                    summary.get(
                        "fps"
                    )
                ),
            ],
            [
                "Primary vehicle",
                safe_text(
                    summary.get(
                        "primary_vehicle"
                    )
                ),
            ],
            [
                "Inspection start",
                safe_text(
                    summary.get(
                        "start_time"
                    )
                ),
            ],
            [
                "Inspection end",
                safe_text(
                    summary.get(
                        "end_time"
                    )
                ),
            ],
            [
                "Observed views",
                safe_text(
                    coverage_text
                ),
            ],
            [
                "Coverage complete",
                safe_text(
                    summary.get(
                        "coverage_complete",
                        False,
                    )
                ),
            ],
        ]

        story.append(
            make_table(
                overview_data,
                col_widths=[
                    55 * mm,
                    105 * mm,
                ],
            )
        )

        # ==============================================================
        # 2. DAMAGE SUMMARY
        # ==============================================================

        add_section_title(
            story,
            "2. Damage Summary",
        )

        damage_summary_table = [
            [
                "Vehicle view",
                "Detected damage",
            ]
        ]

        for view in views:

            damage_summary_table.append([
                view.title(),
                str(
                    damage_summary.get(
                        view,
                        0,
                    )
                ),
            ])

        damage_summary_table.append([
            "Total",
            str(
                damage_summary.get(
                    "total",
                    0,
                )
            ),
        ])

        story.append(
            make_table(
                damage_summary_table,
                col_widths=[
                    80 * mm,
                    80 * mm,
                ],
            )
        )

        # ==============================================================
        # 3. DAMAGE FINDINGS
        # ==============================================================

        add_section_title(
            story,
            "3. Damage Findings",
        )

        story.append(
            Paragraph(
                "The following findings represent detected visible "
                "damage in the selected representative vehicle views.",
                styles["BodySmall"],
            )
        )

        story.append(
            Spacer(
                1,
                3 * mm,
            )
        )

        damage_table = [
            [
                "ID",
                "View",
                "Type",
                "Confidence",
            ]
        ]

        for damage in damages:

            damage_table.append([
                safe_text(
                    damage.get(
                        "damage_id"
                    )
                ),
                safe_text(
                    damage.get(
                        "view"
                    )
                ).title(),
                safe_text(
                    damage.get(
                        "damage_type"
                    )
                    or damage.get(
                        "damage_class"
                    )
                    or damage.get(
                        "class_name"
                    )
                ).title(),
                format_confidence(
                    damage.get(
                        "confidence"
                    )
                ),
            ])

        if len(damage_table) == 1:

            damage_table.append([
                "—",
                "—",
                "No damage detections",
                "—",
            ])

        story.append(
            make_table(
                damage_table,
                col_widths=[
                    35 * mm,
                    35 * mm,
                    45 * mm,
                    45 * mm,
                ],
            )
        )

        # ==============================================================
        # 4. DAMAGE VISUALIZATIONS
        # ==============================================================

        add_section_title(
            story,
            "4. Damage Visualizations",
        )

        visualization_images_added = 0

        # --------------------------------------------------------------
        # IMPORTANT:
        # Iterate over the visualization dictionary itself rather than
        # only iterating over observed views.
        #
        # This prevents a visualization from being skipped because the
        # coverage/observed-view list is incomplete.
        # --------------------------------------------------------------

        visualization_views = []

        if isinstance(
            damage_visualizations,
            dict,
        ):

            visualization_views = list(
                damage_visualizations.keys()
            )

        for view in visualization_views:

            visualization = (
                damage_visualizations.get(
                    view
                )
            )

            image_path = (
                resolve_visualization_path(
                    visualization
                )
            )

            detection_count = (
                damage_summary.get(
                    view,
                    0,
                )
            )

            frame_id = None

            if isinstance(
                visualization,
                dict,
            ):

                frame_id = visualization.get(
                    "frame_id"
                )

                detection_count = (
                    visualization.get(
                        "detection_count",
                        detection_count,
                    )
                )

            label = (
                f"<b>{safe_text(view).title()} View</b>"
                f" — {safe_text(detection_count)} damage detection(s)"
            )

            if frame_id is not None:

                label += (
                    f" — Frame {safe_text(frame_id)}"
                )

            story.append(
                Paragraph(
                    label,
                    styles["Finding"],
                )
            )

            story.append(
                Spacer(
                    1,
                    2 * mm,
                )
            )

            if add_image_file(
                story,
                image_path,
            ):

                visualization_images_added += 1

            else:

                story.append(
                    Paragraph(
                        "Damage visualization image "
                        "could not be loaded.",
                        styles["BodyTiny"],
                    )
                )

            story.append(
                Spacer(
                    1,
                    6 * mm,
                )
            )

        if visualization_images_added == 0:

            story.append(
                Paragraph(
                    "No damage visualization images were available.",
                    styles["BodySmall"],
                )
            )

        # ==============================================================
        # 5. VEHICLE PART SUMMARY
        # ==============================================================

        story.append(PageBreak())

        add_section_title(
            story,
            "5. Vehicle Parts Identified",
        )

        story.append(
            Paragraph(
                "The inspection system identified visible vehicle "
                "components in each representative view.",
                styles["BodySmall"],
            )
        )

        story.append(
            Spacer(
                1,
                3 * mm,
            )
        )

        part_summary_table = [
            [
                "Vehicle view",
                "Parts identified",
            ]
        ]

        for view in views:

            part_summary_table.append([
                view.title(),
                str(
                    vehicle_part_summary.get(
                        view,
                        0,
                    )
                ),
            ])

        part_summary_table.append([
            "Total",
            str(
                vehicle_part_summary.get(
                    "total",
                    0,
                )
            ),
        ])

        story.append(
            make_table(
                part_summary_table,
                col_widths=[
                    80 * mm,
                    80 * mm,
                ],
            )
        )

        # ==============================================================
        # 6. IDENTIFIED COMPONENTS BY VIEW
        # ==============================================================

        add_section_title(
            story,
            "6. Identified Components by View",
        )

        for view in views:

            parts = vehicle_parts.get(
                view,
                [],
            )

            story.append(
                Paragraph(
                    f"<b>{safe_text(view).title()}</b>",
                    styles["Finding"],
                )
            )

            if not parts:

                story.append(
                    Paragraph(
                        "No vehicle-part detections recorded.",
                        styles["BodyTiny"],
                    )
                )

                story.append(
                    Spacer(
                        1,
                        4 * mm,
                    )
                )

                continue

            component_table = [
                [
                    "Component",
                    "Model confidence",
                ]
            ]

            for part in parts:

                if not isinstance(
                    part,
                    dict,
                ):
                    continue

                name = (
                    part.get(
                        "vehicle_part"
                    )
                    or part.get(
                        "raw_part"
                    )
                    or part.get(
                        "part"
                    )
                    or part.get(
                        "class_name"
                    )
                )

                if not name:
                    continue

                component_table.append([
                    safe_text(
                        name
                    ).replace(
                        "_",
                        " ",
                    ).title(),
                    format_confidence(
                        part.get(
                            "confidence"
                        )
                    ),
                ])

            if len(
                component_table
            ) > 1:

                story.append(
                    make_table(
                        component_table,
                        col_widths=[
                            105 * mm,
                            55 * mm,
                        ],
                    )
                )

            else:

                story.append(
                    Paragraph(
                        "No valid component records available.",
                        styles["BodyTiny"],
                    )
                )

            story.append(
                Spacer(
                    1,
                    4 * mm,
                )
            )

        # ==============================================================
        # 7. VEHICLE PART IMAGES
        # ==============================================================

        story.append(PageBreak())

        add_section_title(
            story,
            "7. Vehicle Part Images",
        )

        story.append(
            Paragraph(
                "These images show the vehicle components identified "
                "by the vehicle-part detection system.",
                styles["BodySmall"],
            )
        )

        story.append(
            Spacer(
                1,
                4 * mm,
            )
        )

        part_images_added = 0

        for view, image_reference in (
            vehicle_part_visualizations.items()
        ):

            image_path = (
                resolve_visualization_path(
                    image_reference
                )
            )

            story.append(
                Paragraph(
                    f"<b>{safe_text(view).title()} view</b>",
                    styles["Finding"],
                )
            )

            if add_image_file(
                story,
                image_path,
            ):

                part_images_added += 1

            else:

                story.append(
                    Paragraph(
                        "Vehicle-part visualization image "
                        "is not available.",
                        styles["BodyTiny"],
                    )
                )

            story.append(
                Spacer(
                    1,
                    5 * mm,
                )
            )

        if part_images_added == 0:

            story.append(
                Paragraph(
                    "No vehicle-part visualization images were available.",
                    styles["BodySmall"],
                )
            )

        # ==============================================================
        # 8. DAMAGE-TO-PART ASSOCIATION
        # ==============================================================

        story.append(PageBreak())

        add_section_title(
            story,
            "8. Damage-to-Part Association",
        )

        if not association_confirmed:

            story.append(
                Paragraph(
                    "<b>Not confirmed.</b> The damage-to-part "
                    "association results are experimental and are "
                    "not being presented as confirmed findings.",
                    styles["Warning"],
                )
            )

            story.append(
                Spacer(
                    1,
                    4 * mm,
                )
            )

            story.append(
                Paragraph(
                    "The report can identify visible damage and "
                    "vehicle components separately, but it does not "
                    "currently make a reliable definitive statement "
                    "linking a particular damage detection to a "
                    "specific vehicle component.",
                    styles["BodySmall"],
                )
            )

        else:

            association_table = [
                [
                    "Damage",
                    "View",
                    "Vehicle part",
                    "Status",
                ]
            ]

            for record in association_records:

                if not isinstance(
                    record,
                    dict,
                ):
                    continue

                association_table.append([
                    safe_text(
                        record.get(
                            "damage_id"
                        )
                    ),
                    safe_text(
                        record.get(
                            "view"
                        )
                    ).title(),
                    safe_text(
                        record.get(
                            "vehicle_part"
                        )
                    ),
                    safe_text(
                        record.get(
                            "status"
                        )
                    ).title(),
                ])

            if len(
                association_table
            ) > 1:

                story.append(
                    make_table(
                        association_table,
                        col_widths=[
                            35 * mm,
                            35 * mm,
                            55 * mm,
                            35 * mm,
                        ],
                    )
                )

            else:

                story.append(
                    Paragraph(
                        "No association records were exported.",
                        styles["BodySmall"],
                    )
                )

        # ==============================================================
        # NOTES
        # ==============================================================

        add_section_title(
            story,
            "9. Important Notes",
        )

        notes = [
            "The report describes detections made from the supplied inspection video.",
            "Confidence values indicate model confidence and are not repair-cost estimates.",
            "The report does not determine the severity or roadworthiness of the vehicle.",
            "Vehicle-part detections identify visible components in the selected views.",
            "Damage-to-part associations are currently experimental and are not treated as confirmed findings.",
            "A physical inspection may be required to determine the actual extent of damage.",
        ]

        for note in notes:

            story.append(
                Paragraph(
                    "• " + safe_text(note),
                    styles["BodySmall"],
                )
            )

            story.append(
                Spacer(
                    1,
                    1.5 * mm,
                )
            )

        # --------------------------------------------------------------
        # NOTE:
        # There is deliberately NO "Report Files" section.
        # --------------------------------------------------------------

        generated_at = datetime.now().strftime(
            "%d %b %Y, %H:%M:%S"
        )

        story.append(
            Spacer(
                1,
                8 * mm,
            )
        )

        story.append(
            Paragraph(
                "Report generated: "
                + safe_text(
                    generated_at
                ),
                styles["BodyTiny"],
            )
        )

        # --------------------------------------------------------------
        # Build PDF
        # --------------------------------------------------------------

        doc.build(
            story,
            onFirstPage=draw_page_header_footer,
            onLaterPages=draw_page_header_footer,
        )

        return pdf_path
