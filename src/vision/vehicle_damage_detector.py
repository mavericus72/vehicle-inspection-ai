# # Vehicle Damage Detector
#
# from ultralytics import YOLO
# import numpy as np
#
#
# class VehicleDamageDetector:
#
#     def __init__(
#         self,
#         model_path,
#         confidence_threshold=0.30
#     ):
#         """
#         Vehicle damage segmentation using YOLO.
#
#         Responsibilities:
#             - Load YOLO segmentation model
#             - Run damage inference
#             - Extract damage class
#             - Extract confidence
#             - Extract bounding box
#             - Extract segmentation polygon
#             - Calculate polygon mask area
#
#         This module does NOT:
#             - determine vehicle view
#             - map vehicle sides
#             - perform vehicle-part mapping
#             - visualize detections
#             - generate reports
#         """
#
#         self.model = YOLO(
#             model_path
#         )
#
#         self.confidence_threshold = (
#             confidence_threshold
#         )
#
#
#     def predict(self, image):
#         """
#         Run vehicle damage detector
#
#         Args:
#             image:
#                 Input vehicle image/frame.
#
#         Returns:
#             List of damage detection dictionaries.
#         """
#
#         results = self.model(
#             image,
#             verbose=False
#         )[0]
#
#         detections = []
#
#         boxes = results.boxes
#         masks = results.masks
#
#
#         # -----------------------------------------
#         # No detections
#         # -----------------------------------------
#
#         if boxes is None:
#
#             return detections
#
#
#         # -----------------------------------------
#         # Process detections
#         # -----------------------------------------
#
#         for i, box in enumerate(boxes):
#
#             # -------------------------------------
#             # Confidence
#             # -------------------------------------
#
#             confidence = float(
#                 box.conf.item()
#             )
#
#
#             # -------------------------------------
#             # Confidence filtering
#             # -------------------------------------
#
#             if confidence < self.confidence_threshold:
#
#                 continue
#
#
#             # -------------------------------------
#             # Class ID
#             # -------------------------------------
#
#             class_id = int(
#                 box.cls.item()
#             )
#
#
#             # -------------------------------------
#             # Raw damage class
#             # -------------------------------------
#
#             raw_damage = self.model.names[
#                 class_id
#             ]
#
#
#             # -------------------------------------
#             # Bounding box
#             # -------------------------------------
#
#             x1, y1, x2, y2 = map(
#                 float,
#                 box.xyxy[0].tolist()
#             )
#
#             bbox = [
#                 x1,
#                 y1,
#                 x2,
#                 y2
#             ]
#
#
#             # -------------------------------------
#             # Segmentation mask
#             # -------------------------------------
#
#             mask = None
#
#             if masks is not None:
#
#                 mask = masks.xy[i]
#
#
#             # -------------------------------------
#             # Mask area
#             # -------------------------------------
#
#             mask_area = (
#                 self._calculate_polygon_area(
#                     mask
#                 )
#             )
#
#
#             # -------------------------------------
#             # Detection dictionary
#             # -------------------------------------
#
#             detections.append({
#
#                 "raw_damage": raw_damage,
#
#                 "class_id": class_id,
#
#                 "confidence": confidence,
#
#                 "bbox": bbox,
#
#                 "mask": mask,
#
#                 "mask_area": mask_area
#
#             })
#
#
#         return detections
#
#
#     @staticmethod
#     def _calculate_polygon_area(
#         polygon
#     ):
#         """
#         Calculate polygon area using the
#         shoelace formula.
#         """
#
#         if polygon is None:
#
#             return 0.0
#
#
#         polygon = np.asarray(
#             polygon,
#             dtype=np.float32
#         )
#
#
#         if len(polygon) < 3:
#
#             return 0.0
#
#
#         x = polygon[:, 0]
#
#         y = polygon[:, 1]
#
#
#         area = 0.5 * abs(
#             np.sum(
#                 x * np.roll(y, -1)
#                 -
#                 y * np.roll(x, -1)
#             )
#         )
#
#
#         return float(area)



from ultralytics import YOLO
import numpy as np


class VehicleDamageDetector:
    """
    YOLO-based vehicle damage segmentation detector.

    Responsibilities:
        - Load the YOLO segmentation model
        - Run damage inference
        - Extract damage class
        - Extract confidence
        - Extract bounding box
        - Extract segmentation polygon
        - Calculate polygon area

    This module does NOT:
        - determine vehicle view
        - determine vehicle side
        - map damage to vehicle parts
        - perform multi-frame fusion
        - estimate severity
        - visualize detections
        - generate reports
    """

    def __init__(
        self,
        model_path,
        confidence_threshold=0.30,
    ):
        self.model = YOLO(model_path)

        self.confidence_threshold = float(
            confidence_threshold
        )

    def predict(self, image):
        """
        Run vehicle damage segmentation.

        Args:
            image:
                Input BGR/RGB image as a NumPy array.

        Returns:
            List of damage detection dictionaries.
        """

        if image is None:
            return []

        results = self.model(
            image,
            verbose=False,
        )

        if not results:
            return []

        result = results[0]

        boxes = result.boxes
        masks = result.masks

        detections = []

        # ----------------------------------------------------------
        # No detections
        # ----------------------------------------------------------

        if boxes is None or len(boxes) == 0:
            return detections

        # ----------------------------------------------------------
        # Process detections
        # ----------------------------------------------------------

        for i, box in enumerate(boxes):

            # ------------------------------------------------------
            # Confidence
            # ------------------------------------------------------

            confidence = float(
                box.conf.item()
            )

            if confidence < self.confidence_threshold:
                continue

            # ------------------------------------------------------
            # Class
            # ------------------------------------------------------

            class_id = int(
                box.cls.item()
            )

            raw_damage = self.model.names.get(
                class_id,
                str(class_id),
            )

            # ------------------------------------------------------
            # Bounding box
            # ------------------------------------------------------

            x1, y1, x2, y2 = map(
                float,
                box.xyxy[0].tolist(),
            )

            bbox = [
                x1,
                y1,
                x2,
                y2,
            ]

            # ------------------------------------------------------
            # Segmentation mask
            # ------------------------------------------------------

            mask = None

            if (
                masks is not None
                and i < len(masks.xy)
            ):
                mask = masks.xy[i]

            # ------------------------------------------------------
            # Mask area
            # ------------------------------------------------------

            mask_area = self._calculate_polygon_area(
                mask
            )

            # ------------------------------------------------------
            # Detection record
            # ------------------------------------------------------

            detections.append(
                {
                    "raw_damage": raw_damage,
                    "class_id": class_id,
                    "confidence": confidence,
                    "bbox": bbox,
                    "mask": mask,
                    "mask_area": mask_area,
                }
            )

        return detections

    @staticmethod
    def _calculate_polygon_area(polygon):
        """
        Calculate polygon area using the shoelace formula.

        Returns:
            float: Polygon area in pixels².
        """

        if polygon is None:
            return 0.0

        polygon = np.asarray(
            polygon,
            dtype=np.float32,
        )

        if polygon.ndim != 2:
            return 0.0

        if polygon.shape[0] < 3:
            return 0.0

        x = polygon[:, 0]
        y = polygon[:, 1]

        area = 0.5 * abs(
            np.sum(
                x * np.roll(y, -1)
                - y * np.roll(x, -1)
            )
        )

        return float(area)
