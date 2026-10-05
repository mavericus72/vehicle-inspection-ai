from datetime import datetime


def create_inspection_session():
    """
    Create the initial inspection state.

    This object is passed through the inspection pipeline and gradually
    populated by tracking, coverage estimation, representative-frame
    extraction, damage detection, evaluation, and report generation.
    """

    session_id = datetime.now().strftime(
        "INS_%Y%m%d_%H%M%S"
    )

    inspection = {
        "session_id": session_id,

        "video_name": "",

        "video_path": "",

        "start_time": datetime.now().isoformat(),

        "total_frames": 0,

        "fps": 0,

        # --------------------------------------------------------------
        # Vehicle tracking
        # --------------------------------------------------------------

        "vehicles": {},

        # --------------------------------------------------------------
        # Temporary frame storage
        # --------------------------------------------------------------

        "frames_cache": {},

        # --------------------------------------------------------------
        # Selected inspection vehicle
        # --------------------------------------------------------------

        "primary_vehicle": None,

        # --------------------------------------------------------------
        # Coverage
        # --------------------------------------------------------------

        "coverage": {
            "front": False,
            "rear": False,
            "left": False,
            "right": False,
        },

        # --------------------------------------------------------------
        # Raw view classification history
        # --------------------------------------------------------------

        "view_history": [],

        # --------------------------------------------------------------
        # Stable view counts
        # --------------------------------------------------------------

        "view_counts": {
            "front": 0,
            "rear": 0,
            "left": 0,
            "right": 0,
        },

        # --------------------------------------------------------------
        # View confidence history
        # --------------------------------------------------------------

        "view_confidences": {
            "front": [],
            "rear": [],
            "left": [],
            "right": [],
        },

        # --------------------------------------------------------------
        # Best quality frames per view
        # --------------------------------------------------------------

        "best_views": {
            "front": {
                "frame": None,
                "confidence": 0.0,
            },
            "rear": {
                "frame": None,
                "confidence": 0.0,
            },
            "left": {
                "frame": None,
                "confidence": 0.0,
            },
            "right": {
                "frame": None,
                "confidence": 0.0,
            },
        },

        # --------------------------------------------------------------
        # Extracted representative frames
        # --------------------------------------------------------------

        "representative_frames": {
            "front": {
                "frame_id": None,
                "image": None,
                "quality": 0.0,
            },
            "rear": {
                "frame_id": None,
                "image": None,
                "quality": 0.0,
            },
            "left": {
                "frame_id": None,
                "image": None,
                "quality": 0.0,
            },
            "right": {
                "frame_id": None,
                "image": None,
                "quality": 0.0,
            },
        },

        # --------------------------------------------------------------
        # Vehicle-part detection / segmentation results
        # --------------------------------------------------------------

        "vehicle_parts": {
            "front": [],
            "rear": [],
            "left": [],
            "right": [],
        },

        # --------------------------------------------------------------
        # Damage detection results
        # --------------------------------------------------------------

        "damages": {
            "front": [],
            "rear": [],
            "left": [],
            "right": [],
        },

        # --------------------------------------------------------------
        # Damage visualizations
        # --------------------------------------------------------------

        "damage_visualizations": {
            "front": {},
            "rear": {},
            "left": {},
            "right": {},
        },

        # --------------------------------------------------------------
        # Vehicle-part visualizations
        # --------------------------------------------------------------

        "vehicle_part_visualizations": {
            "front": None,
            "rear": None,
            "left": None,
            "right": None,
        },

        # --------------------------------------------------------------
        # Experimental damage-to-part association
        # --------------------------------------------------------------

        "damage_part_associations": {
            "confirmed": False,
            "records": [],
        },

        # --------------------------------------------------------------
        # Evaluation report
        # --------------------------------------------------------------

        "report": {},

        # --------------------------------------------------------------
        # Final generated report
        # --------------------------------------------------------------

        "final_report": {},

        "final_report_export": {},

        "final_report_pdf": {},

        # --------------------------------------------------------------
        # User-facing report
        # --------------------------------------------------------------

        "user_report": {},

        # --------------------------------------------------------------
        # Coverage status
        # --------------------------------------------------------------

        "coverage_complete": False,}

    return inspection
    



# from datetime import datetime
#
# def create_inspection_session():
#     session_id = datetime.now().strftime("INS_%Y%m%d_%H%M%S")
#
#     inspection = {
#         "session_id": session_id,
#         "video_name": "",
#         "video_path": "",
#         "start_time": datetime.now().isoformat(),
#         "total_frames": 0,
#         "fps": 0,
#
#         # Vehicle tracking
#         "vehicles": {},
#
#     	# Frame storage for representative frame extraction
#         # Its purpose is to temporarily store selected video frames that may be useful later.
#         "frames_cache": {},
#
# 	    # Selected inspection vehicle
#         "primary_vehicle": None,    # If we put 0 instead of None, it can be confusing with a numeric value
#
#         # Coverage
#         "coverage": {
#             "front": False,
#             "rear": False,
#             "left": False,
#             "right": False
#         },  # We write False and not None because we have not discovered the view yet.
#
# 	# Raw view classification history
#         "view_history": [],
#
# 	# Stable view counts
#         "view_counts": {
#             "front": 0,
#             "rear": 0,
#             "left": 0,
#             "right": 0
#         },
#
# 	# View confidence history
#         "view_confidences": {
#             "front": [],
#             "rear": [],
#             "left": [],
#             "right": []
#         },
#
# 	# Best quality frames per view
#         "best_views": {
#             "front": {"frame": None, "confidence": 0.0},
#             "rear": {"frame": None, "confidence": 0.0},
#             "left": {"frame": None, "confidence": 0.0},
#             "right": {"frame": None, "confidence": 0.0}
#         },
#
# 	# Extracted representative frames
#         "representative_frames": {
#             "front": {"frame_id": None, "image": None, "quality": 0.0},
#             "rear": {"frame_id": None, "image": None, "quality": 0.0},
#             "left": {"frame_id": None, "image": None, "quality": 0.0},
#             "right": {"frame_id": None, "image": None, "quality": 0.0}
#         },
#
# 	# Vehicle exterior part segmentation results
#         #
#         # Filled by:
#         # VehiclePartSegmenter
#         # PartMapper
#         # VehiclePartExtractor
#         #
#         "vehicle_parts": {
#             "front": [],
#             "rear": [],
#             "left": [],
#             "right": []
#         },
#
# 	# Damage detection and tracking results
#         #
#         # Filled by:
#         # Damage Detector
#         # Damage Tracker
#         # Multi-frame Fusion
#         #
#         "damages": {
#             "front": [],
#             "rear": [],
#             "left": [],
#             "right": []
#         },
#
# 	# Generate Final report
#         "report": {},
#
# 	# Coverage status
#         "coverage_complete": False
#     }
#
#     return inspection