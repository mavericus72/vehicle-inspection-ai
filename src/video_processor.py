import cv2

from vehicle_detector import VehicleDetector


class VideoProcessor:

    def __init__(self):

        self.detector = VehicleDetector()

    def process(self, input_path, output_path):

        cap = cv2.VideoCapture(input_path)

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        writer = cv2.VideoWriter(
            output_path,
            cv2.VideoWriter_fourcc(*'mp4v'),
            fps,
            (width, height)
        )

        while cap.isOpened():

            success, frame = cap.read()

            if not success:
                break

            detections = self.detector.detect(frame)

            for det in detections:

                x1, y1, x2, y2 = det["bbox"]

                cv2.rectangle(
                    frame,
                    (x1, y1),
                    (x2, y2),
                    (0,255,0),
                    2
                )

                cv2.putText(
                    frame,
                    f"{det['confidence']:.2f}",
                    (x1, y1-10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0,255,0),
                    2
                )

            writer.write(frame)

        cap.release()
        writer.release()