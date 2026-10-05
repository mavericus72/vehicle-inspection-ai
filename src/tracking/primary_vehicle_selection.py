# class PrimaryVehicleSelector:
#
#
#     def __init__(self):
#         pass
#
#
#     def select(self, inspection):
#
#         primary_vehicle = None
#
#         max_frames = 0
#
#
#         for track_id, vehicle in inspection["vehicles"].items():
#
#             num_frames = len(
#                 vehicle["frames"]
#             )
#
#
#             if num_frames > max_frames:
#
#                 max_frames = num_frames
#
#                 primary_vehicle = track_id
#
#
#         inspection["primary_vehicle"] = primary_vehicle
#
#
#         return inspection


class PrimaryVehicleSelector:
    """
    Select the primary vehicle for the inspection.

    The current baseline strategy selects the tracked vehicle
    that appears in the greatest number of video frames.

    This keeps the selection logic simple and deterministic.

    Future improvements may consider:
        - average detection confidence
        - visible duration
        - bounding-box size
        - track continuity
        - vehicle position in the frame
    """

    def __init__(self):
        """
        Initialize the primary vehicle selector.
        """
        pass

    def select(self, inspection):
        """
        Select the primary vehicle from tracked vehicles.

        Args:
            inspection:
                Shared inspection state dictionary.

        Returns:
            Updated inspection dictionary.
        """

        vehicles = inspection.get(
            "vehicles",
            {},
        )

        # --------------------------------------------------------------
        # No vehicles detected
        # --------------------------------------------------------------

        if not vehicles:
            inspection["primary_vehicle"] = None

            print(
                "No vehicles available for primary vehicle selection."
            )

            return inspection

        # --------------------------------------------------------------
        # Select vehicle with the largest number of observations
        # --------------------------------------------------------------

        primary_vehicle = None
        max_frames = 0

        for track_id, vehicle in vehicles.items():

            frames = vehicle.get(
                "frames",
                [],
            )

            num_frames = len(frames)

            if num_frames > max_frames:

                max_frames = num_frames
                primary_vehicle = track_id

        # --------------------------------------------------------------
        # Store result
        # --------------------------------------------------------------

        inspection["primary_vehicle"] = (
            primary_vehicle
        )

        if primary_vehicle is None:

            print(
                "Unable to select a primary vehicle."
            )

        else:

            print(
                "Primary vehicle selected:",
                primary_vehicle,
            )

            print(
                "Vehicle observations:",
                max_frames,
            )

        return inspection
