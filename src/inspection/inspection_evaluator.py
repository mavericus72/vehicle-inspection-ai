class InspectionEvaluator:

    def __init__(self):
        pass

    def evaluate(self, inspection):

        if not isinstance(inspection, dict):
            raise TypeError(
                "inspection must be a dictionary."
            )

        report = {}

        # ==============================================================
        # INSPECTION INFORMATION
        # ==============================================================

        report["inspection_id"] = inspection.get(
            "session_id"
        )

        report["video_name"] = inspection.get(
            "video_name"
        )

        # ==============================================================
        # COVERAGE
        # ==============================================================

        report["coverage"] = inspection.get(
            "coverage",
            {}
        )

        report["coverage_complete"] = inspection.get(
            "coverage_complete",
            False
        )

        # ==============================================================
        # VIEW STATISTICS
        # ==============================================================

        report["view_counts"] = inspection.get(
            "view_counts",
            {}
        )

        # ==============================================================
        # REPRESENTATIVE FRAMES
        # ==============================================================

        report["representative_frames"] = {}

        representative_frames = inspection.get(
            "representative_frames",
            {}
        )

        for view, data in representative_frames.items():

            if not isinstance(data, dict):
                continue

            report["representative_frames"][view] = {

                "frame_id": data.get(
                    "frame_id"
                ),

                "quality": round(
                    float(
                        data.get(
                            "quality",
                            0.0
                        )
                    ),
                    3
                ),

                "available": (
                    data.get("image") is not None
                )
            }

        # ==============================================================
        # VEHICLE PARTS
        # ==============================================================

        report["vehicle_parts"] = inspection.get(
            "vehicle_parts",
            {}
        )

        # ==============================================================
        # DAMAGES
        # ==============================================================

        report["damages"] = inspection.get(
            "damages",
            {}
        )

        # ==============================================================
        # EVALUATION METADATA
        # ==============================================================

        report["evaluation_status"] = "completed"

        return report
