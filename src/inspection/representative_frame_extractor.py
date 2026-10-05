# # Create Representative Frame Extractor
# # import cv2 (Not needed as we use cached frames)
# class RepresentativeFrameExtractor:
#
#     def __init__(self, quality_evaluator):
#
#         self.quality_evaluator = quality_evaluator
#
#     def extract(self, inspection):
#
#         primary_vehicle = inspection["primary_vehicle"]
#
#         if primary_vehicle is None: # Set it up as a gaurd clause
#             print("No primary vehicle")
#             return inspection
#
#         frames_cache = inspection["frames_cache"] # Use it to process faster
#
#         # video_path = inspection["video_path"]
#
#         # cap = cv2.VideoCapture(video_path)
#
#         vehicle_data = inspection["vehicles"][primary_vehicle]
#
#         frame_bbox_map = dict(zip(vehicle_data["frames"], vehicle_data["bbox_history"]))
#
#         for item in inspection["view_history"]:
#
#             frame_id = item["frame"]
#
#             view = item["stable_view"]
#
#             confidence = item["confidence"]
#
#             if frame_id not in frame_bbox_map:
#                 continue
#
#             # Move video to required frame
#             # cap.set(cv2.CAP_PROP_POS_FRAMES, frame_id)
#             #
#             # ret, frame = cap.read()
#             #
#             # if not ret:
#             #     continue
#
#             frame = frames_cache.get(frame_id)
#
#             if frame is None:
#                 continue
#
#
#             x1, y1, x2, y2 = frame_bbox_map[frame_id]
#
#             # Safety clipping
#             h, w = frame.shape[:2]
#
#             x1 = max(0, x1)
#             y1 = max(0, y1)
#
#             x2 = min(w, x2)
#             y2 = min(h, y2)
#
#             crop = frame[
#                 y1:y2,
#                 x1:x2]
#
#             if crop.size == 0:
#                 continue
#
#             quality = self.quality_evaluator.calculate(crop, confidence)
#
#             current = inspection["representative_frames"][view]
#
#             if quality > current["quality"]:
#
#                 current["frame_id"] = frame_id
#
#                 current["image"] = crop.copy()
#
#                 current["quality"] = quality
#
#         # cap.release()
#
#         return inspection


class RepresentativeFrameExtractor:
    """
    Extract the best representative vehicle frame for each
    stable vehicle view.

    The extractor:

        - Uses cached frames.
        - Uses the primary vehicle's bounding-box history.
        - Crops the primary vehicle.
        - Evaluates crop quality.
        - Keeps the highest-quality crop for each view.

    This module does NOT:

        - classify vehicle views
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

    def __init__(self, quality_evaluator):
        """
        Initialize the representative-frame extractor.

        Args:
            quality_evaluator:
                FrameQualityEvaluator instance used to score
                candidate vehicle crops.
        """

        if quality_evaluator is None:
            raise ValueError(
                "quality_evaluator cannot be None."
            )

        self.quality_evaluator = quality_evaluator

    def extract(self, inspection):
        """
        Extract the highest-quality representative frame
        for each available vehicle view.

        Args:
            inspection:
                Shared inspection state dictionary.

        Returns:
            Updated inspection dictionary.
        """

        # ----------------------------------------------------------
        # PRIMARY VEHICLE
        # ----------------------------------------------------------

        primary_vehicle = inspection.get(
            "primary_vehicle"
        )

        if primary_vehicle is None:

            print(
                "Representative frame extraction "
                "skipped: no primary vehicle."
            )

            return inspection

        # ----------------------------------------------------------
        # GET PRIMARY VEHICLE DATA
        # ----------------------------------------------------------

        vehicles = inspection.get(
            "vehicles",
            {}
        )

        vehicle_data = vehicles.get(
            primary_vehicle
        )

        if vehicle_data is None:

            print(
                "Representative frame extraction "
                "skipped: primary vehicle data missing."
            )

            return inspection

        # ----------------------------------------------------------
        # FRAME CACHE
        # ----------------------------------------------------------

        frames_cache = inspection.get(
            "frames_cache",
            {}
        )

        if not frames_cache:

            print(
                "Representative frame extraction "
                "skipped: frame cache is empty."
            )

            return inspection

        # ----------------------------------------------------------
        # BUILD FRAME → BBOX LOOKUP
        # ----------------------------------------------------------

        frames = vehicle_data.get(
            "frames",
            []
        )

        bbox_history = vehicle_data.get(
            "bbox_history",
            []
        )

        if not frames:

            print(
                "Representative frame extraction "
                "skipped: primary vehicle has no frames."
            )

            return inspection

        if len(frames) != len(bbox_history):

            print(
                "Warning: vehicle frame history and "
                "bounding-box history have different lengths. "
                "Only matching entries will be used."
            )

        frame_bbox_map = {}

        for frame_id, bbox in zip(
            frames,
            bbox_history
        ):
            frame_bbox_map[frame_id] = bbox

        # ----------------------------------------------------------
        # INITIALIZE REPRESENTATIVE FRAME STORAGE
        # ----------------------------------------------------------

        representative_frames = {}

        existing_frames = inspection.get(
            "representative_frames",
            {}
        )

        for view in self.VIEWS:

            existing = existing_frames.get(
                view,
                {}
            )

            representative_frames[view] = {
                "frame_id": existing.get(
                    "frame_id"
                ),
                "image": existing.get(
                    "image"
                ),
                "quality": float(
                    existing.get(
                        "quality",
                        0.0
                    )
                ),
            }

        # ----------------------------------------------------------
        # PROCESS STABLE VIEW PREDICTIONS
        # ----------------------------------------------------------

        view_history = inspection.get(
            "view_history",
            []
        )

        if not view_history:

            print(
                "Representative frame extraction "
                "skipped: no view history available."
            )

            inspection[
                "representative_frames"
            ] = representative_frames

            return inspection

        candidates_processed = 0
        candidates_selected = 0

        for item in view_history:

            if not isinstance(item, dict):
                continue

            # ------------------------------------------------------
            # FRAME ID
            # ------------------------------------------------------

            frame_id = item.get(
                "frame"
            )

            if frame_id is None:
                continue

            # ------------------------------------------------------
            # VIEW
            # ------------------------------------------------------

            view = str(
                item.get(
                    "stable_view",
                    ""
                )
            ).lower().strip()

            if view not in self.VIEWS:
                continue

            # ------------------------------------------------------
            # CLASSIFICATION CONFIDENCE
            # ------------------------------------------------------

            confidence = item.get(
                "confidence",
                0.0
            )

            try:
                confidence = float(
                    confidence
                )
            except (
                TypeError,
                ValueError,
            ):
                continue

            # ------------------------------------------------------
            # FRAME MUST HAVE A BBOX
            # ------------------------------------------------------

            bbox = frame_bbox_map.get(
                frame_id
            )

            if bbox is None:
                continue

            if not isinstance(
                bbox,
                (list, tuple)
            ):
                continue

            if len(bbox) != 4:
                continue

            # ------------------------------------------------------
            # FRAME MUST EXIST IN CACHE
            # ------------------------------------------------------

            frame = frames_cache.get(
                frame_id
            )

            if frame is None:
                continue

            if not hasattr(
                frame,
                "shape"
            ):
                continue

            if frame.size == 0:
                continue

            candidates_processed += 1

            # ------------------------------------------------------
            # GET VEHICLE BOUNDING BOX
            # ------------------------------------------------------

            try:

                x1, y1, x2, y2 = map(
                    int,
                    bbox
                )

            except (
                TypeError,
                ValueError,
            ):
                continue

            # ------------------------------------------------------
            # SAFETY CLIPPING
            # ------------------------------------------------------

            height, width = (
                frame.shape[:2]
            )

            x1 = max(
                0,
                min(x1, width)
            )

            y1 = max(
                0,
                min(y1, height)
            )

            x2 = max(
                0,
                min(x2, width)
            )

            y2 = max(
                0,
                min(y2, height)
            )

            # ------------------------------------------------------
            # VALIDATE BBOX
            # ------------------------------------------------------

            if x2 <= x1 or y2 <= y1:
                continue

            # ------------------------------------------------------
            # CROP PRIMARY VEHICLE
            # ------------------------------------------------------

            crop = frame[
                y1:y2,
                x1:x2
            ]

            if crop.size == 0:
                continue

            # ------------------------------------------------------
            # CALCULATE QUALITY
            # ------------------------------------------------------

            try:

                quality = float(
                    self.quality_evaluator.calculate(
                        crop,
                        confidence
                    )
                )

            except Exception as exc:

                print(
                    f"Frame quality calculation "
                    f"failed for frame {frame_id}: "
                    f"{type(exc).__name__}: {exc}"
                )

                continue

            # ------------------------------------------------------
            # KEEP BEST FRAME FOR THIS VIEW
            # ------------------------------------------------------

            current = representative_frames[
                view
            ]

            current_quality = float(
                current.get(
                    "quality",
                    0.0
                )
            )

            if quality > current_quality:

                current[
                    "frame_id"
                ] = frame_id

                current[
                    "image"
                ] = crop.copy()

                current[
                    "quality"
                ] = quality

                candidates_selected += 1

        # ----------------------------------------------------------
        # STORE RESULTS
        # ----------------------------------------------------------

        inspection[
            "representative_frames"
        ] = representative_frames

        # ----------------------------------------------------------
        # LOG RESULTS
        # ----------------------------------------------------------

        print(
            "\nRepresentative frames:"
        )

        for view in self.VIEWS:

            data = representative_frames[
                view
            ]

            frame_id = data.get(
                "frame_id"
            )

            quality = float(
                data.get(
                    "quality",
                    0.0
                )
            )

            available = (
                data.get("image") is not None
            )

            print(
                f"  {view:<6}: "
                f"available={available}, "
                f"frame={frame_id}, "
                f"quality={quality:.3f}"
            )

        print(
            "Representative-frame candidates "
            f"processed: {candidates_processed}"
        )

        print(
            "Representative frames selected: "
            f"{candidates_selected}"
        )

        return inspection
