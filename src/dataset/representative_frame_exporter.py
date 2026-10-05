# This only saves representatives images.
import os
import cv2


class RepresentativeFrameExporter:

    def __init__(self, output_dir):

        self.output_dir = output_dir

        os.makedirs(
            self.output_dir,
            exist_ok=True
        )


    def export(self, inspection, inspection_id):

        saved_files = []

        for view, data in inspection["representative_frames"].items():

            image = data["image"]

            if image is None:
                continue

            frame_id = data["frame_id"]

            filename = (
                f"{inspection_id}_"
                f"{view}_"
                f"frame_{frame_id}.jpg"
            )

            save_path = os.path.join(
                self.output_dir,
                filename
            )

            cv2.imwrite(
                save_path,
                image
            )

            saved_files.append(save_path)

        return saved_files