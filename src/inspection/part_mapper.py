# # Create Part Mapper
# class PartMapper:
#
#     def map_part(
#         self,
#         part_name,
#         view,
#         bbox=None,
#         image_shape=None
#     ):
#         """
#         Map a raw vehicle-part name to a
#         vehicle-specific part name.
#
#         Example:
#
#             mirror
#                 ↓
#             right_mirror
#         """
#
#         # -----------------------------------------
#         # Clean inputs
#         # -----------------------------------------
#
#         if part_name is None:
#             return "unknown"
#
#
#         part_name = str(
#             part_name
#         ).lower().strip()
#
#
#         if view is not None:
#
#             view = str(
#                 view
#             ).lower().strip()
#
#
#         # -----------------------------------------
#         # Side-specific parts
#         # -----------------------------------------
#
#         side_specific_parts = {
#
#             "mirror",
#
#             "front_door",
#
#             "rear_door",
#
#             "front_fender",
#
#             "rear_quarter_panel",
#
#             "headlight",
#
#             "taillight",
#
#             "front_wheel",
#
#             "rear_wheel"
#
#         }
#
#
#         # -----------------------------------------
#         # Parts without left/right identity
#         # -----------------------------------------
#
#         if part_name not in side_specific_parts:
#
#             return part_name
#
#
#         # -----------------------------------------
#         # Cannot determine side
#         # -----------------------------------------
#
#         if (
#             bbox is None
#             or image_shape is None
#         ):
#
#             return part_name
#
#
#         # -----------------------------------------
#         # Bounding box
#         # -----------------------------------------
#
#         x1, y1, x2, y2 = bbox
#
#
#         height, width = image_shape[:2]
#
#
#         # -----------------------------------------
#         # Detection center
#         # -----------------------------------------
#
#         center_x = (
#             x1 + x2
#         ) / 2.0
#
#
#         image_center_x = (
#             width / 2.0
#         )
#
#
#         # -----------------------------------------
#         # Determine image side
#         # -----------------------------------------
#
#         if center_x < image_center_x:
#
#             image_side = "left"
#
#         else:
#
#             image_side = "right"
#
#
#         # -----------------------------------------
#         # FRONT VIEW
#         # -----------------------------------------
#
#         if view == "front":
#
#             # Image-left is vehicle-right
#             # Image-right is vehicle-left
#
#             if image_side == "left":
#
#                 vehicle_side = "right"
#
#             else:
#
#                 vehicle_side = "left"
#
#
#         # -----------------------------------------
#         # REAR VIEW
#         # -----------------------------------------
#
#         elif view == "rear":
#
#             # Image-left is vehicle-left
#             # Image-right is vehicle-right
#
#             vehicle_side = image_side
#
#
#         # -----------------------------------------
#         # Other views
#         # -----------------------------------------
#
#         else:
#
#             # Horizontal image position is not
#             # sufficient for side views.
#
#             return part_name
#
#
#         # -----------------------------------------
#         # Final semantic name
#         # -----------------------------------------
#
#         return f"{vehicle_side}_{part_name}"


class PartMapper:
    """
    Map raw vehicle-part detections to semantic vehicle-part names.

    The mapper uses:

        - raw model part name
        - vehicle view
        - detection bounding box
        - image dimensions

    to determine side-specific vehicle parts when possible.

    Example:

        raw part:
            mirror

        front-view detection on image-left:
            right_mirror
    """

    VIEWS = {
        "front",
        "rear",
        "left",
        "right",
    }

    SIDE_SPECIFIC_PARTS = {
        "mirror",
        "front_door",
        "rear_door",
        "front_fender",
        "rear_quarter_panel",
        "headlight",
        "taillight",
        "front_wheel",
        "rear_wheel",
    }

    def map_part(
        self,
        part_name,
        view,
        bbox=None,
        image_shape=None,
    ):
        """
        Map a raw vehicle-part name to a semantic
        vehicle-part name.

        Args:
            part_name:
                Raw class name produced by the vehicle-part model.

            view:
                Normalized vehicle view:
                    front
                    rear
                    left
                    right

            bbox:
                Detection bounding box:
                    [x1, y1, x2, y2]

            image_shape:
                Image shape, normally:
                    (height, width, channels)

        Returns:
            Semantic vehicle-part name.
        """

        # ----------------------------------------------------------
        # CLEAN PART NAME
        # ----------------------------------------------------------

        if part_name is None:
            return "unknown"

        part_name = str(
            part_name
        ).lower().strip()

        if not part_name:
            return "unknown"

        # ----------------------------------------------------------
        # CLEAN VIEW
        # ----------------------------------------------------------

        if view is not None:

            view = str(
                view
            ).lower().strip()

        # ----------------------------------------------------------
        # PARTS THAT DO NOT REQUIRE SIDE MAPPING
        # ----------------------------------------------------------

        if part_name not in self.SIDE_SPECIFIC_PARTS:
            return part_name

        # ----------------------------------------------------------
        # SIDE CANNOT BE DETERMINED
        # ----------------------------------------------------------

        if bbox is None or image_shape is None:
            return part_name

        # ----------------------------------------------------------
        # VALIDATE BOUNDING BOX
        # ----------------------------------------------------------

        if not isinstance(
            bbox,
            (list, tuple)
        ):
            return part_name

        if len(bbox) != 4:
            return part_name

        try:

            x1, y1, x2, y2 = map(
                float,
                bbox
            )

        except (
            TypeError,
            ValueError,
        ):

            return part_name

        # ----------------------------------------------------------
        # VALIDATE IMAGE SHAPE
        # ----------------------------------------------------------

        try:

            height, width = image_shape[:2]

            height = float(height)
            width = float(width)

        except (
            TypeError,
            ValueError,
        ):

            return part_name

        if width <= 0 or height <= 0:
            return part_name

        # ----------------------------------------------------------
        # DETECTION CENTER
        # ----------------------------------------------------------

        center_x = (
            x1 + x2
        ) / 2.0

        image_center_x = (
            width / 2.0
        )

        # ----------------------------------------------------------
        # DETERMINE IMAGE SIDE
        # ----------------------------------------------------------

        if center_x < image_center_x:

            image_side = "left"

        else:

            image_side = "right"

        # ----------------------------------------------------------
        # FRONT VIEW
        # ----------------------------------------------------------

        if view == "front":

            # When looking at the front of the vehicle:
            #
            # image-left  = vehicle-right
            # image-right = vehicle-left

            if image_side == "left":

                vehicle_side = "right"

            else:

                vehicle_side = "left"

        # ----------------------------------------------------------
        # REAR VIEW
        # ----------------------------------------------------------

        elif view == "rear":

            # When looking at the rear of the vehicle:
            #
            # image-left  = vehicle-left
            # image-right = vehicle-right

            vehicle_side = image_side

        # ----------------------------------------------------------
        # SIDE VIEWS
        # ----------------------------------------------------------

        else:

            # For left/right views, horizontal image position
            # alone does not reliably establish the semantic
            # vehicle side.
            #
            # Therefore preserve the raw part name rather than
            # making an unsupported assumption.

            return part_name

        # ----------------------------------------------------------
        # FINAL SEMANTIC NAME
        # ----------------------------------------------------------

        return (
            f"{vehicle_side}_{part_name}"
        )
