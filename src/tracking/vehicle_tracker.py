# from ultralytics import YOLO
# from src.config import YOLO_DETECTOR_MODEL
# import cv2
# from src.config import FRAME_SKIP
#
#
# class VehicleTracker:
#
#     # COCO vehicle classes
#     # car = 2
#     # motorcycle = 3
#     # bus = 5
#     # truck = 7
#     VEHICLE_CLASSES = [2, 3, 5, 7]
#
#
#     def __init__(self, model_path=YOLO_DETECTOR_MODEL):  # Load the YOLO11n model from config.py
#
#         self.model = YOLO(str(model_path))
#
#     def track(self,inspection):
#
#         video_path = inspection["video_path"]
#
#         cap = cv2.VideoCapture(video_path)
#
#         if not cap.isOpened():
#             raise Exception(f"Cannot open video: {video_path}")
#
#         inspection["vehicles"] = {}
#
#         frame_idx = 0
#
#         print("Starting tracking...")
#
#         while True:
#             ret, frame = cap.read()
#             if not ret:
#                 break
#
#             if frame_idx % FRAME_SKIP == 0:
#                 inspection["frames_cache"][frame_idx] = frame.copy() # To keep a copy of the frames created during initial video processing
#
#             results = self.model.track(frame,persist=True,verbose=False)[0]
#
#             if frame_idx % 50 == 0:
#
#                 print(f"Processed frame {frame_idx}")
#
#             if (
#                 results.boxes is None
#                 or results.boxes.id is None
#             ):
#
#                 frame_idx += 1
#                 continue
#
#
#
#             for box in results.boxes:
#
#
#                 cls = int(
#                     box.cls.item()
#                 )
#
#
#                 if cls not in self.VEHICLE_CLASSES:
#                     continue
#
#
#                 track_id = int(
#                     box.id.item()
#                 )
#
#
#                 conf = float(
#                     box.conf.item()
#                 )
#
#
#                 x1, y1, x2, y2 = map(
#                     int,
#                     box.xyxy[0]
#                 )
#
#
#                 h, w = frame.shape[:2]
#
#
#                 x1 = max(0, x1)
#                 y1 = max(0, y1)
#
#                 x2 = min(w, x2)
#                 y2 = min(h, y2)
#
#
#
#                 if track_id not in inspection["vehicles"]:
#
#
#                     inspection["vehicles"][track_id] = {
#
#                         "first_seen": frame_idx,
#
#                         "last_seen": frame_idx,
#
#                         "class_id": cls,
#
#                         "frames": [],
#
#                         "bbox_history": [],
#
#                         "confidence_history": []
#                     }
#
#
#
#                 vehicle = inspection["vehicles"][track_id]
#
#
#                 vehicle["last_seen"] = frame_idx
#
#
#                 vehicle["frames"].append(
#                     frame_idx
#                 )
#
#                 vehicle["bbox_history"].append([x1,y1,x2,y2])
#                 vehicle["confidence_history"].append(conf)
#
#             frame_idx += 1
#
#         cap.release()
#
#         inspection["total_frames"] = frame_idx
#
#         print("Tracking complete.")
#
#         print("Vehicles detected:",len(inspection["vehicles"]))
#
#         return inspection

import cv2
from ultralytics import YOLO

from src.config import FRAME_SKIP, YOLO_DETECTOR_MODEL


class VehicleTracker:
    """
    Detect and track vehicles throughout an inspection video.

    Responsibilities:
        - Open the inspection video.
        - Run YOLO vehicle tracking.
        - Keep only relevant vehicle classes.
        - Store per-track frame and bounding-box history.
        - Cache useful frames for downstream inspection stages.
        - Store total video frame count.

    The inspection dictionary is used as the shared state between
    pipeline stages.
    """

    # COCO vehicle classes:
    # car = 2
    # motorcycle = 3
    # bus = 5
    # truck = 7
    VEHICLE_CLASSES = {2, 3, 5, 7}

    def __init__(
        self,
        model_path=YOLO_DETECTOR_MODEL,
    ):
        """
        Initialize the YOLO tracking model.

        Args:
            model_path:
                Path to the YOLO detection/tracking model.
        """

        self.model = YOLO(str(model_path))

    def track(self, inspection):
        """
        Track vehicles in the inspection video.

        Args:
            inspection:
                Shared inspection state dictionary.

        Returns:
            Updated inspection dictionary.

        Raises:
            KeyError:
                If inspection does not contain video_path.

            FileNotFoundError:
                If the video cannot be opened.
        """

        video_path = inspection.get("video_path")

        if not video_path:
            raise ValueError(
                "Inspection does not contain a valid 'video_path'."
            )

        cap = cv2.VideoCapture(str(video_path))

        if not cap.isOpened():
            raise FileNotFoundError(
                f"Cannot open video: {video_path}"
            )

        # Reset tracking state for this inspection.
        inspection["vehicles"] = {}

        # Make sure downstream modules always have a frame cache.
        inspection.setdefault(
            "frames_cache",
            {},
        )

        # Clear any frames from a previous run.
        inspection["frames_cache"].clear()

        frame_idx = 0

        print("\nStarting vehicle tracking...")

        try:
            while True:

                ret, frame = cap.read()

                if not ret:
                    break

                # ------------------------------------------------------
                # Run YOLO tracking
                # ------------------------------------------------------

                results = self.model.track(
                    frame,
                    persist=True,
                    verbose=False,
                )[0]

                if frame_idx % 50 == 0:
                    print(
                        f"Processed frame {frame_idx}"
                    )

                # ------------------------------------------------------
                # No tracked objects
                # ------------------------------------------------------

                if (
                    results.boxes is None
                    or results.boxes.id is None
                ):
                    frame_idx += 1
                    continue

                frame_has_vehicle = False

                # ------------------------------------------------------
                # Process tracked vehicles
                # ------------------------------------------------------

                for box in results.boxes:

                    cls = int(
                        box.cls.item()
                    )

                    if cls not in self.VEHICLE_CLASSES:
                        continue

                    track_id = int(
                        box.id.item()
                    )

                    confidence = float(
                        box.conf.item()
                    )

                    x1, y1, x2, y2 = map(
                        int,
                        box.xyxy[0].tolist(),
                    )

                    height, width = frame.shape[:2]

                    # Clamp bounding box to image boundaries.
                    x1 = max(
                        0,
                        min(x1, width - 1),
                    )

                    y1 = max(
                        0,
                        min(y1, height - 1),
                    )

                    x2 = max(
                        0,
                        min(x2, width),
                    )

                    y2 = max(
                        0,
                        min(y2, height),
                    )

                    # Ignore invalid bounding boxes.
                    if x2 <= x1 or y2 <= y1:
                        continue

                    frame_has_vehicle = True

                    # --------------------------------------------------
                    # Initialize new vehicle track
                    # --------------------------------------------------

                    if track_id not in inspection["vehicles"]:

                        inspection["vehicles"][track_id] = {
                            "first_seen": frame_idx,
                            "last_seen": frame_idx,
                            "class_id": cls,
                            "frames": [],
                            "bbox_history": [],
                            "confidence_history": [],
                        }

                    vehicle = inspection["vehicles"][track_id]

                    # --------------------------------------------------
                    # Update vehicle history
                    # --------------------------------------------------

                    vehicle["last_seen"] = frame_idx

                    vehicle["frames"].append(
                        frame_idx
                    )

                    vehicle["bbox_history"].append(
                        [
                            x1,
                            y1,
                            x2,
                            y2,
                        ]
                    )

                    vehicle["confidence_history"].append(
                        confidence
                    )

                # ------------------------------------------------------
                # Cache useful frames
                #
                # We do not cache every video frame.
                #
                # A frame is cached when:
                #   1. It contains a tracked vehicle, and
                #   2. It satisfies FRAME_SKIP.
                #
                # This keeps memory usage controlled while ensuring
                # cached frames are relevant to vehicle inspection.
                # ------------------------------------------------------

                if (
                    frame_has_vehicle
                    and frame_idx % FRAME_SKIP == 0
                ):
                    inspection["frames_cache"][
                        frame_idx
                    ] = frame.copy()

                frame_idx += 1

        finally:
            cap.release()

        # --------------------------------------------------------------
        # Store video statistics
        # --------------------------------------------------------------

        inspection["total_frames"] = frame_idx

        # Obtain FPS if possible.
        fps = cap.get(
            cv2.CAP_PROP_FPS
        )

        if fps and fps > 0:
            inspection["fps"] = float(fps)

        print("\nTracking complete.")

        print(
            "Total frames:",
            inspection["total_frames"],
        )

        print(
            "Vehicles detected:",
            len(inspection["vehicles"]),
        )

        print(
            "Cached frames:",
            len(inspection["frames_cache"]),
        )

        return inspection
