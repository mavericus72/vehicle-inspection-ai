import cv2
import numpy as np


class VehiclePartVisualizer:

    def __init__(
        self,
        alpha=0.45,
        draw_bbox=True,
        draw_label=True
    ):
        """
        Visualizes vehicle part segmentation.

        Arguments:
            alpha:
                Transparency of segmentation masks.

            draw_bbox:
                Draw bounding boxes.

            draw_label:
                Draw part names and confidence.
        """
        self.alpha = alpha
        self.draw_bbox = draw_bbox
        self.draw_label = draw_label

    def _get_color(self, index):
        """
        Return a consistent color for each detection.
        """

        colors = [
            (0, 255, 0),       # Green
            (255, 0, 0),       # Blue
            (0, 255, 255),     # Yellow
            (255, 0, 255),     # Magenta
            (0, 165, 255),     # Orange
            (255, 255, 0),     # Cyan
            (128, 0, 255),     # Purple
            (0, 128, 255)      # Orange-red
        ]

        return colors[
            index % len(colors)
        ]

    def draw_mask(
        self,
        image,
        mask,
        color
    ):
        """
        Draw a segmentation mask over the image.
        """
        if mask is None:
            return image

        polygon = np.asarray(
            mask,
            dtype=np.int32
        )

        if len(polygon) < 3:
            return image

        overlay = image.copy()

        cv2.fillPoly(
            overlay,
            [polygon],
            color
        )

        image = cv2.addWeighted(
            overlay,
            self.alpha,
            image,
            1.0 - self.alpha,
            0
        )

        # Draw mask boundary

        cv2.polylines(
            image,
            [polygon],
            True,
            color,
            2
        )

        return image

    def draw_detection(
        self,
        image,
        detection,
        color
    ):
        """
        Draw one vehicle-part detection.
        """

        mask = detection.get(
            "mask"
        )

        bbox = detection.get(
            "bbox"
        )

        confidence = detection.get(
            "confidence",
            0.0
        )

        vehicle_part = detection.get(
            "vehicle_part",
            "unknown"
        )


        # ---------------------------------
        # Draw segmentation mask
        # ---------------------------------

        image = self.draw_mask(
            image,
            mask,
            color
        )


        # ---------------------------------
        # Draw bounding box
        # ---------------------------------

        if (
            self.draw_bbox
            and bbox is not None
        ):

            x1, y1, x2, y2 = map(
                int,
                bbox
            )

            cv2.rectangle(
                image,
                (x1, y1),
                (x2, y2),
                color,
                2
            )


        # ---------------------------------
        # Draw label
        # ---------------------------------

        if self.draw_label:

            if bbox is not None:

                x1 = int(bbox[0])

                y1 = int(bbox[1])

            else:

                x1 = 10

                y1 = 30


            label = (
                f"{vehicle_part} "
                f"{confidence:.2f}"
            )


            font = cv2.FONT_HERSHEY_SIMPLEX

            font_scale = 0.55

            thickness = 2


            (
                text_width,
                text_height
            ), baseline = cv2.getTextSize(
                label,
                font,
                font_scale,
                thickness
            )


            label_y = max(
                y1,
                text_height + 10
            )


            # Label background

            cv2.rectangle(
                image,

                (
                    x1,
                    label_y - text_height - 8
                ),

                (
                    x1 + text_width + 8,
                    label_y + baseline
                ),

                color,

                -1
            )


            # Label text

            cv2.putText(
                image,
                label,
                (
                    x1 + 4,
                    label_y - 4
                ),
                font,
                font_scale,
                (0, 0, 0),
                thickness,
                cv2.LINE_AA
            )


        return image


    def visualize(
        self,
        image,
        detections
    ):
        """
        Visualize all vehicle-part detections.
        """

        output = image.copy()


        for index, detection in enumerate(
            detections
        ):

            color = self._get_color(
                index
            )


            output = self.draw_detection(
                output,
                detection,
                color
            )


        return output