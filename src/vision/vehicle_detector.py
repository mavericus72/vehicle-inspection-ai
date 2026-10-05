# from ultralytics import YOLO
#
# VEHICLE_CLASSES = {2, 3, 5, 7}  # car, motorcycle, bus, truck
#
# class VehicleDetector:
#
#     def __init__(self, model_path="yolo11n.pt"):
#         self.model = YOLO(model_path)
#
#     def detect(self, frame):
#
#         results = self.model(frame, verbose=False)
#
#         detections = []
#
#         for result in results:
#
#             for box in result.boxes:
#
#                 cls = int(box.cls[0])
#
#                 if cls not in VEHICLE_CLASSES:
#                     continue
#
#                 x1, y1, x2, y2 = map(int, box.xyxy[0])
#
#                 detections.append({
#                     "bbox": (x1, y1, x2, y2),
#                     "confidence": float(box.conf[0]),
#                     "class": cls
#                 })
#
#         return detections


from ultralytics import YOLO


# COCO vehicle classes
VEHICLE_CLASSES = {
    2,  # car
    3,  # motorcycle
    5,  # bus
    7,  # truck
}


class VehicleDetector:

    def __init__(
        self,
        model_path="yolo11n.pt",
    ):
        self.model = YOLO(
            model_path
        )

    def detect(self, frame):

        results = self.model(
            frame,
            verbose=False,
        )

        detections = []

        for result in results:

            if result.boxes is None:
                continue

            for box in result.boxes:

                class_id = int(
                    box.cls[0]
                )

                if class_id not in VEHICLE_CLASSES:
                    continue

                x1, y1, x2, y2 = map(
                    int,
                    box.xyxy[0].tolist(),
                )

                confidence = float(
                    box.conf[0]
                )

                detections.append({
                    "bbox": (
                        x1,
                        y1,
                        x2,
                        y2,
                    ),
                    "confidence": confidence,
                    "class": class_id,
                })

        return detections
