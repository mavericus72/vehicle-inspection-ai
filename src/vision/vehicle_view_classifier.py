from ultralytics import YOLO


class VehicleViewClassifier:
    """
    Wrapper around a YOLO11 Classification model for
    vehicle view prediction.

    The trained model's LEFT/RIGHT convention is reversed
    relative to the convention used by the inspection pipeline.

    Therefore:

        model "left"  -> pipeline "right"
        model "right" -> pipeline "left"

    FRONT and REAR remain unchanged.
    """

    def __init__(self, model_path):

        self.model = YOLO(model_path)


    def predict(self, image):

        result = self.model(
            image,
            verbose=False
        )[0]

        probs = result.probs

        class_id = int(
            probs.top1
        )

        confidence = float(
            probs.top1conf
        )

        class_name = result.names[
            class_id
        ]

        # ---------------------------------------------
        # Normalize vehicle-view convention
        # ---------------------------------------------
        view = class_name.lower().strip()

        if view == "left":

            view = "right"

        elif view == "right":

            view = "left"

        # ---------------------------------------------
        # Return normalized result
        # ---------------------------------------------
        return {
            "view": view,
            "confidence": confidence
        }
