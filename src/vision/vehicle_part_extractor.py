# # Create Vehicle Part Extractor
# class VehiclePartExtractor:
#
#     def __init__(
#         self,
#         segmenter,
#         mapper
#     ):
#         """
#         Connect the vehicle part segmenter
#         with the part mapper.
#         """
#
#         self.segmenter = segmenter
#
#         self.mapper = mapper
#
#
#     def extract(
#         self,
#         frame,
#         view
#     ):
#         """
#         Extract and semantically map vehicle parts.
#
#         Args:
#             frame:
#                 Input vehicle image.
#
#             view:
#                 Camera orientation.
#
#                 Examples:
#                     "front"
#                     "rear"
#
#         Returns:
#             List of mapped detections.
#         """
#
#         # -----------------------------------------
#         # Run segmentation
#         # -----------------------------------------
#
#         detections = self.segmenter.predict(
#             frame
#         )
#
#
#         mapped_parts = []
#
#
#         # -----------------------------------------
#         # Process every detection
#         # -----------------------------------------
#
#         for detection in detections:
#
#             raw_part = detection[
#                 "raw_part"
#             ]
#
#
#             bbox = detection.get(
#                 "bbox"
#             )
#
#
#             # -------------------------------------
#             # Map raw part to vehicle part
#             # -------------------------------------
#
#             mapped_name = self.mapper.map_part(
#                 raw_part,
#                 view,
#                 bbox,
#                 frame.shape
#             )
#
#
#             # -------------------------------------
#             # Add mapped name
#             # -------------------------------------
#
#             detection[
#                 "vehicle_part"
#             ] = mapped_name
#
#
#             mapped_parts.append(
#                 detection
#             )
#
#
#         return mapped_parts


# ======================================================================
# VEHICLE PART EXTRACTOR
# ======================================================================

from src.config import INSPECTION_OUTPUT_DIR

import copy


class VehiclePartExtractor:
    """
    Extract vehicle parts from a representative vehicle frame
    and map raw model classes to vehicle-specific semantic names.

    Pipeline:

        frame
          ↓
        VehiclePartSegmenter
          ↓
        raw detections
          ↓
        PartMapper
          ↓
        vehicle-specific detections

    Example:

        raw_part = "mirror"
        view = "front"
        bbox = [100, 120, 180, 220]

        ↓

        vehicle_part = "right_mirror"
    """

    def __init__(
        self,
        segmenter,
        mapper,
    ):
        """
        Parameters
        ----------
        segmenter:
            Vehicle-part segmentation model/object.

            Expected interface:

                segmenter.predict(frame)

            Expected return:

                list[dict]

        mapper:
            PartMapper instance.

            Expected interface:

                mapper.map_part(
                    part_name,
                    view,
                    bbox,
                    image_shape
                )
        """

        if segmenter is None:
            raise ValueError(
                "segmenter must not be None."
            )

        if mapper is None:
            raise ValueError(
                "mapper must not be None."
            )

        self.segmenter = segmenter
        self.mapper = mapper


    # ------------------------------------------------------------------
    # EXTRACT
    # ------------------------------------------------------------------

    def extract(
        self,
        frame,
        view,
    ):
        """
        Extract and semantically map vehicle parts.

        Parameters
        ----------
        frame:
            Input vehicle image.

            Expected to be a NumPy image with:

                frame.shape

        view:
            Vehicle camera orientation.

            Expected examples:

                "front"
                "rear"
                "left"
                "right"

        Returns
        -------
        list[dict]
            Vehicle-part detection records.

        Each record is expected to contain:

            vehicle_part
            raw_part
            class_id
            confidence
            bbox
            mask
        """

        # --------------------------------------------------------------
        # VALIDATE FRAME
        # --------------------------------------------------------------

        if frame is None:
            return []

        if not hasattr(frame, "shape"):
            raise TypeError(
                "frame must provide a valid .shape attribute."
            )


        # --------------------------------------------------------------
        # NORMALIZE VIEW
        # --------------------------------------------------------------

        if view is not None:
            view = str(view).lower().strip()


        # --------------------------------------------------------------
        # RUN VEHICLE-PART SEGMENTATION
        # --------------------------------------------------------------

        detections = self.segmenter.predict(
            frame
        )


        if detections is None:
            return []


        if not isinstance(
            detections,
            (list, tuple)
        ):
            raise TypeError(
                "segmenter.predict(frame) must return "
                "a list or tuple of detection dictionaries."
            )


        mapped_parts = []


        # --------------------------------------------------------------
        # PROCESS DETECTIONS
        # --------------------------------------------------------------

        for detection in detections:

            if not isinstance(
                detection,
                dict
            ):
                continue


            # ----------------------------------------------------------
            # COPY DETECTION
            # ----------------------------------------------------------

            record = copy.deepcopy(
                detection
            )


            # ----------------------------------------------------------
            # RAW PART
            # ----------------------------------------------------------

            raw_part = record.get(
                "raw_part"
            )

            if raw_part is None:
                raw_part = record.get(
                    "class_name"
                )

            if raw_part is None:
                raw_part = record.get(
                    "name"
                )

            if raw_part is None:
                continue


            raw_part = str(
                raw_part
            ).lower().strip()


            record["raw_part"] = raw_part


            # ----------------------------------------------------------
            # BOUNDING BOX
            # ----------------------------------------------------------

            bbox = record.get(
                "bbox"
            )


            # ----------------------------------------------------------
            # MAP RAW PART → VEHICLE-SPECIFIC PART
            # ----------------------------------------------------------

            mapped_name = self.mapper.map_part(
                raw_part,
                view,
                bbox,
                frame.shape,
            )


            record["vehicle_part"] = (
                mapped_name
            )


            # ----------------------------------------------------------
            # ENSURE STANDARD FIELDS EXIST
            # ----------------------------------------------------------

            if "class_id" not in record:
                record["class_id"] = None

            if "confidence" not in record:
                record["confidence"] = None

            if "bbox" not in record:
                record["bbox"] = None

            if "mask" not in record:
                record["mask"] = None


            # ----------------------------------------------------------
            # SOURCE VIEW
            # ----------------------------------------------------------

            record["view"] = view


            # ----------------------------------------------------------
            # APPEND
            # ----------------------------------------------------------

            mapped_parts.append(
                record
            )


        return mapped_parts
