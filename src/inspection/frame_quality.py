# # Create Frame Quality Evaluation
# # Why do we need a Frame Quality Evaluator instead of ?
#
# # A blurry frame may have high classification confidence but provide poor
# # visual information for downstream tasks such as segmentation and damage detection.
# import cv2
# class FrameQualityEvaluator:
#     def __init__(self): # However, it could become useful later if you want configurable parameters such as:confidence_weight,size_weight, blur_weight
#         pass
#
#     def calculate(self,vehicle_crop,confidence):
#
#         # Image size score
#         height, width = vehicle_crop.shape[:2] # We don't need the BGR color channels so restrict it to 2
#         area = height * width
#         size_score = min(area / (300 * 300),1.0)    # Calculate the size score, but never allow it to exceed 1
#         # 300 * 300 That's an engineering assumption.
#
#         # Blur score
#         gray = cv2.cvtColor(vehicle_crop,cv2.COLOR_BGR2GRAY)     # Convert color image to grayscale
#         blur_score = cv2.Laplacian(gray,cv2.CV_64F).var()   # Laplacian is used to measure sharpness/blur
#         blur_score = min(blur_score / 500,1.0)
#         # A larger Laplacian variance generally
#         # indicates more pronounced edges/sharpness, while a smaller value generally indicates more blur.
#
#         # Combined score
#         quality = (
#             confidence * 0.5 +  # confidence → model's confidence about the VIEW. Classification confidence = 50%
#             size_score * 0.3 +  # size_score → how large the VEHICLE CROP is. Vehicle crop size = 30%
#             blur_score * 0.2)   # blur_score → how SHARP the vehicle crop is.Image sharpness = 20%
#             # 0.5/0.3/0.2 - selected randomly and can be adjusted.
#         return quality
#         # For future we can also measure, exposure, brightness, contrast, etc apart from these scores.
#         # In future, instead of Laplace operator, use brenner gradient.

import cv2


class FrameQualityEvaluator:
    """
    Evaluate the visual quality of a vehicle crop.

    The current quality score combines:

        - view-classification confidence: 50%
        - vehicle crop size:             30%
        - image sharpness:               20%

    The resulting score is normalized approximately to [0, 1].

    This evaluator is intentionally simple. It is used to select
    representative frames and is not intended to determine whether
    an image is suitable for human inspection.
    """

    def __init__(
        self,
        confidence_weight=0.5,
        size_weight=0.3,
        blur_weight=0.2,
        target_size=300,
        sharpness_reference=500.0,
    ):
        """
        Initialize the frame quality evaluator.

        Args:
            confidence_weight:
                Weight assigned to view-classification confidence.

            size_weight:
                Weight assigned to vehicle crop size.

            blur_weight:
                Weight assigned to image sharpness.

            target_size:
                Reference dimension used for calculating the
                crop-size score.

            sharpness_reference:
                Reference Laplacian variance used to normalize
                the sharpness score.
        """

        total_weight = (
            confidence_weight
            + size_weight
            + blur_weight
        )

        if total_weight <= 0:
            raise ValueError(
                "Frame quality weights must sum to a positive value."
            )

        self.confidence_weight = (
            confidence_weight / total_weight
        )

        self.size_weight = (
            size_weight / total_weight
        )

        self.blur_weight = (
            blur_weight / total_weight
        )

        self.target_size = float(target_size)

        self.sharpness_reference = float(
            sharpness_reference
        )

        if self.target_size <= 0:
            raise ValueError(
                "target_size must be greater than zero."
            )

        if self.sharpness_reference <= 0:
            raise ValueError(
                "sharpness_reference must be greater than zero."
            )

    def calculate(
        self,
        vehicle_crop,
        confidence,
    ):
        """
        Calculate a normalized frame-quality score.

        Args:
            vehicle_crop:
                Cropped vehicle image as a NumPy/OpenCV image.

            confidence:
                Vehicle-view classification confidence.

        Returns:
            Float quality score approximately in the range [0, 1].
        """

        if vehicle_crop is None:
            return 0.0

        if not hasattr(vehicle_crop, "shape"):
            return 0.0

        if vehicle_crop.size == 0:
            return 0.0

        # ----------------------------------------------------------
        # Classification confidence
        # ----------------------------------------------------------

        try:
            confidence = float(confidence)
        except (TypeError, ValueError):
            confidence = 0.0

        confidence = max(
            0.0,
            min(confidence, 1.0),
        )

        # ----------------------------------------------------------
        # Vehicle crop size
        # ----------------------------------------------------------

        height, width = vehicle_crop.shape[:2]

        if height <= 0 or width <= 0:
            return 0.0

        area = height * width

        reference_area = (
            self.target_size
            * self.target_size
        )

        size_score = min(
            area / reference_area,
            1.0,
        )

        # ----------------------------------------------------------
        # Image sharpness
        # ----------------------------------------------------------

        try:
            if len(vehicle_crop.shape) == 2:
                gray = vehicle_crop

            elif vehicle_crop.shape[2] == 3:
                gray = cv2.cvtColor(
                    vehicle_crop,
                    cv2.COLOR_BGR2GRAY,
                )

            elif vehicle_crop.shape[2] == 4:
                gray = cv2.cvtColor(
                    vehicle_crop,
                    cv2.COLOR_BGRA2GRAY,
                )

            else:
                return 0.0

        except (cv2.error, IndexError):
            return 0.0

        laplacian_variance = cv2.Laplacian(
            gray,
            cv2.CV_64F,
        ).var()

        blur_score = min(
            laplacian_variance
            / self.sharpness_reference,
            1.0,
        )

        # ----------------------------------------------------------
        # Combined quality score
        # ----------------------------------------------------------

        quality = (
            confidence
            * self.confidence_weight
            +
            size_score
            * self.size_weight
            +
            blur_score
            * self.blur_weight
        )

        return float(
            max(
                0.0,
                min(quality, 1.0),
            )
        )
