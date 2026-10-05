# # Create Vehicle Part Segmenter
# from ultralytics import YOLO
# import numpy as np
#
#
# class VehiclePartSegmenter:
#
#     def __init__(
#         self,
#         model_path,
#         confidence_threshold=0.30
#     ):
#         """
#         Vehicle part segmentation using YOLO.
#
#         Responsibilities:
#             - Load YOLO model
#             - Run inference
#             - Extract class
#             - Extract confidence
#             - Extract bounding box
#             - Extract segmentation mask
#             - Calculate mask area
#
#         This module does NOT perform left/right mapping.
#         """
#
#         self.model = YOLO(model_path)
#
#         self.confidence_threshold = confidence_threshold
#
#
#     def predict(self, image):
#         """
#         Run vehicle-part segmentation.
#
#         Args:
#             image:
#                 Input image/frame.
#
#         Returns:
#             List of detection dictionaries.
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
#
#         masks = results.masks
#
#
#         # -----------------------------------------
#         # No detections
#         # -----------------------------------------
#
#         if boxes is None:
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
#             # Raw YOLO class
#             # -------------------------------------
#
#             raw_part = self.model.names[
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
#                 mask = masks.xy[i]
#
#
#             # -------------------------------------
#             # Mask area
#             # -------------------------------------
#
#             mask_area = self._calculate_polygon_area(
#                 mask
#             )
#
#
#             # -------------------------------------
#             # Detection dictionary
#             # -------------------------------------
#
#             detections.append({
#
#                 "raw_part": raw_part,
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
#     def _calculate_polygon_area(polygon):
#         """
#         Calculate polygon area using the
#         shoelace formula.
#         """
#
#         if polygon is None:
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


# ======================================================================
# VEHICLE PART SEGMENTER
# ======================================================================

from ultralytics import YOLO
import numpy as np


class VehiclePartSegmenter:
    """
    Vehicle-part segmentation using Ultralytics YOLO.

    Responsibilities:
        - Load the vehicle-part segmentation model.
        - Run inference.
        - Extract class ID.
        - Extract raw class name.
        - Extract confidence.
        - Extract bounding box.
        - Extract segmentation polygon.
        - Calculate segmentation-mask area.

    This module does NOT:
        - determine left/right vehicle side
        - perform semantic vehicle-part mapping
        - associate damage with parts
        - generate reports
    """

    def __init__(
        self,
        model_path,
        confidence_threshold=0.30,
    ):
        """
        Parameters
        ----------
        model_path : str
            Path to the trained YOLO segmentation weights.

        confidence_threshold : float
            Minimum confidence required for a detection.
        """

        if not model_path:
            raise ValueError(
                "model_path must be provided."
            )

        if not (
            0.0
            <= confidence_threshold
            <= 1.0
        ):
            raise ValueError(
                "confidence_threshold must be between 0.0 and 1.0."
            )

        self.model = YOLO(
            model_path
        )

        self.confidence_threshold = (
            float(confidence_threshold)
        )


    # ------------------------------------------------------------------
    # PREDICT
    # ------------------------------------------------------------------

    def predict(self, image):
        """
        Run vehicle-part segmentation.

        Parameters
        ----------
        image:
            Input image/frame as a NumPy array or another image format
            supported by Ultralytics YOLO.

        Returns
        -------
        list[dict]
            Detection dictionaries with the following fields:

                raw_part
                class_id
                confidence
                bbox
                mask
                mask_area
        """

        if image is None:
            return []


        # --------------------------------------------------------------
        # RUN YOLO
        # --------------------------------------------------------------

        results = self.model(
            image,
            verbose=False,
        )


        if not results:
            return []


        result = results[0]


        detections = []


        # --------------------------------------------------------------
        # GET BOXES
        # --------------------------------------------------------------

        boxes = result.boxes


        # --------------------------------------------------------------
        # NO DETECTIONS
        # --------------------------------------------------------------

        if boxes is None:
            return detections


        # --------------------------------------------------------------
        # GET MASKS
        # --------------------------------------------------------------

        masks = result.masks


        # --------------------------------------------------------------
        # PROCESS DETECTIONS
        # --------------------------------------------------------------

        for i, box in enumerate(boxes):

            # ----------------------------------------------------------
            # CONFIDENCE
            # ----------------------------------------------------------

            try:

                confidence = float(
                    box.conf.item()
                )

            except Exception:

                continue


            # ----------------------------------------------------------
            # CONFIDENCE FILTER
            # ----------------------------------------------------------

            if confidence < self.confidence_threshold:
                continue


            # ----------------------------------------------------------
            # CLASS ID
            # ----------------------------------------------------------

            try:

                class_id = int(
                    box.cls.item()
                )

            except Exception:

                continue


            # ----------------------------------------------------------
            # CLASS NAME
            # ----------------------------------------------------------

            raw_part = self._get_class_name(
                class_id
            )


            # ----------------------------------------------------------
            # BOUNDING BOX
            # ----------------------------------------------------------

            try:

                coordinates = (
                    box.xyxy[0]
                    .tolist()
                )

                x1, y1, x2, y2 = map(
                    float,
                    coordinates
                )

                bbox = [
                    x1,
                    y1,
                    x2,
                    y2,
                ]

            except Exception:

                bbox = None


            # ----------------------------------------------------------
            # SEGMENTATION MASK
            # ----------------------------------------------------------

            mask = None

            if masks is not None:

                try:

                    if i < len(masks.xy):

                        mask = np.asarray(
                            masks.xy[i],
                            dtype=np.float32
                        )

                except Exception:

                    mask = None


            # ----------------------------------------------------------
            # MASK AREA
            # ----------------------------------------------------------

            mask_area = (
                self._calculate_polygon_area(
                    mask
                )
            )


            # ----------------------------------------------------------
            # BUILD DETECTION RECORD
            # ----------------------------------------------------------

            detection = {
                "raw_part": raw_part,

                "class_id": class_id,

                "confidence": confidence,

                "bbox": bbox,

                "mask": mask,

                "mask_area": mask_area,
            }


            detections.append(
                detection
            )


        return detections


    # ------------------------------------------------------------------
    # CLASS NAME
    # ------------------------------------------------------------------

    def _get_class_name(
        self,
        class_id,
    ):
        """
        Resolve YOLO class ID to the raw model class name.
        """

        names = self.model.names


        if isinstance(
            names,
            dict
        ):

            return str(
                names.get(
                    class_id,
                    class_id
                )
            )


        if isinstance(
            names,
            (list, tuple)
        ):

            if (
                0
                <= class_id
                < len(names)
            ):

                return str(
                    names[class_id]
                )


        return str(
            class_id
        )


    # ------------------------------------------------------------------
    # MASK AREA
    # ------------------------------------------------------------------

    @staticmethod
    def _calculate_polygon_area(
        polygon
    ):
        """
        Calculate polygon area using the shoelace formula.

        Parameters
        ----------
        polygon : array-like or None
            Polygon coordinates in:

                [[x1, y1],
                 [x2, y2],
                 ...]

        Returns
        -------
        float
            Polygon area in pixel².
        """

        if polygon is None:
            return 0.0


        polygon = np.asarray(
            polygon,
            dtype=np.float32
        )


        if (
            polygon.ndim != 2
            or polygon.shape[1] != 2
            or len(polygon) < 3
        ):
            return 0.0


        x = polygon[:, 0]

        y = polygon[:, 1]


        area = 0.5 * abs(
            np.sum(
                x * np.roll(
                    y,
                    -1
                )
                -
                y * np.roll(
                    x,
                    -1
                )
            )
        )


        return float(
            area
        )
