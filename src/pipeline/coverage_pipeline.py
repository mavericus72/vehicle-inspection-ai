# # import cv2 (Not needed since we don't need to open the video)
# # from src.config import FRAME_SKIP # To edit FRAME_SKIP value
# #
# # class CoveragePipeline:
# #
# #     def __init__(
# #         self,
# #         classifier,
# #         estimator
# #     ):
# #
# #         self.classifier = classifier
# #         self.estimator = estimator
# #
# #     def run(self, inspection):
# #
# #         primary_vehicle = inspection["primary_vehicle"]
# #
# #         if primary_vehicle is None:
# #
# #             print("No primary vehicle selected.")
# #
# #             return inspection
# #
# #         # video_path = inspection["video_path"] (Since we don't need to open the video)
# #         #
# #         # cap = cv2.VideoCapture(video_path) (Since we don't need to open the video)
# #
# #         vehicle = inspection["vehicles"][primary_vehicle]
# #         frames_cache = inspection["frames_cache"] # Using the cached frames to make processing faster
# #
# #         # FRAME_SKIP = 10  # Process every 10th frame and not all frames
# #
# #         frames = vehicle["frames"][::FRAME_SKIP] # Process every 10th frame and not all frames as per config.py
# #         bboxes = vehicle["bbox_history"][::FRAME_SKIP]
# #
# #         for frame_idx, bbox in zip(
# #                 frames,
# #                 bboxes
# #         ):
# #
# #         # for frame_idx, bbox in zip(
# #         #     vehicle["frames"],
# #         #     vehicle["bbox_history"]
# #         # ):
# #
# #             # Move video pointer to required frame (Replacing the entire code as it takes each frame again and again)
# #             # cap.set(
# #             #     cv2.CAP_PROP_POS_FRAMES,
# #             #     frame_idx
# #             # )
# #             #
# #             # ret, frame = cap.read()
# #             #
# #             # if not ret:
# #             #     continue
# #
# #             frame = frames_cache.get(frame_idx)
# #
# #             if frame is None:
# #                 continue
# #
# #             x1, y1, x2, y2 = bbox
# #
# #             vehicle_crop = frame[
# #                 y1:y2,
# #                 x1:x2
# #             ]
# #
# #             if vehicle_crop.size == 0:
# #                 continue
# #
# #             prediction = self.classifier.predict(
# #                 vehicle_crop
# #             )
# #             print(
# #                 f"Frame {frame_idx} | "
# #                 f"View: {prediction['view']} | "
# #                 f"Confidence: {prediction['confidence']:.3f}"
# #             )
# #
# #             self.estimator.update(
# #                 inspection,
# #                 prediction,
# #                 frame_idx
# #             )
# #
# #         # cap.release() (Since we don't need to open the video)
# #
# #         return inspection



# 29-07-2026 edit
from src.inspection.coverage_estimator import CoverageEstimator


class CoveragePipeline:
    """
    Vehicle-view coverage pipeline.

    Responsibilities:
        - Read frames belonging to the primary vehicle.
        - Run vehicle-view classification.
        - Pass predictions to CoverageEstimator.
        - Maintain temporal coverage state.

    This pipeline does NOT:
        - track vehicles
        - select the primary vehicle
        - extract representative frames
        - detect damage
        - detect vehicle parts
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
        view_classifier,
        coverage_estimator,
    ):
        self.view_classifier = view_classifier
        self.coverage_estimator = coverage_estimator

    def run(self, inspection):
        """
        Estimate vehicle-view coverage for the
        selected primary vehicle.
        """

        primary_vehicle = inspection.get(
            "primary_vehicle"
        )

        if primary_vehicle is None:
            print(
                "Coverage estimation skipped: "
                "no primary vehicle selected."
            )

            return inspection

        vehicle = inspection.get(
            "vehicles",
            {}
        ).get(
            primary_vehicle
        )

        if vehicle is None:
            print(
                "Coverage estimation skipped: "
                "primary vehicle data not found."
            )

            return inspection

        frames_cache = inspection.get(
            "frames_cache",
            {}
        )

        vehicle_frames = vehicle.get(
            "frames",
            []
        )

        print(
            f"\nEstimating vehicle-view coverage "
            f"for vehicle {primary_vehicle}..."
        )

        processed = 0
        stable_predictions = 0

        # ----------------------------------------------------------
        # Process only cached frames belonging to
        # the selected primary vehicle.
        # ----------------------------------------------------------

        for frame_idx in vehicle_frames:

            frame = frames_cache.get(
                frame_idx
            )

            if frame is None:
                continue

            try:

                prediction = (
                    self.view_classifier.predict(
                        frame
                    )
                )

            except Exception as exc:

                print(
                    f"View classification failed "
                    f"for frame {frame_idx}: "
                    f"{type(exc).__name__}: {exc}"
                )

                continue

            processed += 1

            stable_view = (
                self.coverage_estimator.update(
                    inspection,
                    prediction,
                    frame_idx,
                )
            )

            if stable_view is not None:

                stable_predictions += 1

        # ----------------------------------------------------------
        # Final coverage state
        # ----------------------------------------------------------

        inspection["coverage_complete"] = all(
            inspection.get(
                "coverage",
                {}
            ).get(view, False)
            for view in self.VIEWS
        )

        # ----------------------------------------------------------
        # Logging
        # ----------------------------------------------------------

        print(
            f"Coverage frames processed: "
            f"{processed}"
        )

        print(
            f"Stable view predictions: "
            f"{stable_predictions}"
        )

        print(
            "Coverage:"
        )

        for view in self.VIEWS:

            covered = inspection.get(
                "coverage",
                {}
            ).get(
                view,
                False
            )

            count = inspection.get(
                "view_counts",
                {}
            ).get(
                view,
                0
            )

            print(
                f"  {view:<6}: "
                f"covered={covered}, "
                f"observations={count}"
            )

        print(
            "Coverage complete:",
            inspection["coverage_complete"]
        )

        return inspection
