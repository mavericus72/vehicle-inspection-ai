# The dataset manager is intended to organize:
# Inspection exports and associated metadata.

import os
import json
import cv2


class DatasetManager:

    def __init__(self, root_dir):

        self.root_dir = root_dir

        self.exports_dir = os.path.join(
            root_dir,
            "exports"
        )

        self.dataset_dir = os.path.join(
            root_dir,
            "dataset"
        )

        os.makedirs(
            self.exports_dir,
            exist_ok=True
        )

        os.makedirs(
            self.dataset_dir,
            exist_ok=True
        )


    def create_export_folder(self, inspection_id):

        export_path = os.path.join(
            self.exports_dir,
            inspection_id
        )

        os.makedirs(
            export_path,
            exist_ok=True
        )

        return export_path


    def save_metadata(self, export_path, inspection):

        metadata = {

            "inspection_id":
                inspection["session_id"],

            "video_name":
                inspection["video_name"],

            "timestamp":
                inspection["start_time"],

            "coverage":
                inspection["coverage"],

            "coverage_complete":
                inspection["coverage_complete"],

            "primary_vehicle":
                inspection["primary_vehicle"]
        }


        with open(
            os.path.join(
                export_path,
                "metadata.json"
            ),
            "w"
        ) as f:

            json.dump(
                metadata,
                f,
                indent=4
            )


    def save_representative_frames(
        self,
        export_path,
        inspection
    ):

        for view, data in inspection["representative_frames"].items():

            if data["image"] is None:
                continue

            filename = f"{view}.jpg"

            cv2.imwrite(

                os.path.join(
                    export_path,
                    filename
                ),

                data["image"]
            )