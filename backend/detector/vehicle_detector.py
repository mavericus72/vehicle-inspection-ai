
from ultralytics import YOLO

class VehicleDetector:

    VEHICLE_CLASSES = {
        "car",
        "truck",
        "bus",
        "motorcycle"
    }

    def __init__(self):
        self.model = YOLO("yolo11n.pt")

    def detect(self, image):

        results = self.model(image)

        detections = []

        for result in results:

            for box in result.boxes:

                class_id = int(box.cls[0])

                class_name = result.names[class_id]

                if class_name not in self.VEHICLE_CLASSES:
                    continue

                detections.append({
                    "class": class_name,
                    "confidence": float(box.conf[0]),
                    "bbox": box.xyxy[0].tolist()
                })

        return detections
    