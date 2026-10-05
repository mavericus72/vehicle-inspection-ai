# import time
# from src.inspection.report_generator import ReportGenerator

#
#
# class InferencePipeline:
#
#     def __init__(
#         self,
#         tracker,
#         selector,
#         coverage_pipeline,
#         frame_extractor,
#         damage_pipeline,
#         evaluator,
#         report_generator,
#     ):
#         self.tracker = tracker
#         self.selector = selector
#         self.coverage_pipeline = coverage_pipeline
#         self.frame_extractor = frame_extractor
#         self.damage_pipeline = damage_pipeline
#         self.evaluator = evaluator
#         self.report_generator = report_generator
#
#     def run(self, inspection):
#
#         start = time.time()
#
#         print("\nStarting vehicle tracking...")
#         inspection = self.tracker.track(inspection)
#
#         print(
#             "Tracking time:",
#             round(time.time() - start, 2),
#             "seconds"
#         )
#
#         start = time.time()
#
#         print("\nSelecting primary vehicle...")
#         inspection = self.selector.select(inspection)
#
#         print(
#             "Selection time:",
#             round(time.time() - start, 2),
#             "seconds"
#         )
#
#         start = time.time()
#
#         print("\nEstimating coverage...")
#         inspection = self.coverage_pipeline.run(inspection)
#
#         print(
#             "Coverage time:",
#             round(time.time() - start, 2),
#             "seconds"
#         )
#
#         start = time.time()
#
#         print("\nExtracting representative frames...")
#         inspection = self.frame_extractor.extract(inspection)
#
#         print(
#             "Frame extraction time:",
#             round(time.time() - start, 2),
#             "seconds"
#         )
#
#         start = time.time()
#
#         print("\nDetecting vehicle damage...")
#         inspection = self.damage_pipeline.run(inspection)
#
#         print(
#             "Damage detection time:",
#             round(time.time() - start, 2),
#             "seconds"
#         )
#
#         start = time.time()
#
#         print("\nGenerating report...")
#         inspection["report"] = self.evaluator.evaluate(
#             inspection
#         )
#
#         print(
#             "Report time:",
#             round(time.time() - start, 2),
#             "seconds"
#         )
#
#         inspection["user_report"] = (
#             self.report_generator.generate(
#                 inspection
#             )
#         )
#
#         return inspection

# src/pipeline/inference_pipeline.py

import time


class InferencePipeline:
    """
    Main vehicle-inspection inference orchestration pipeline.

    Execution order:

        1. Vehicle tracking
        2. Primary vehicle selection
        3. Coverage estimation
        4. Representative-frame extraction
        5. Vehicle-part extraction
        6. Damage detection
        7. Inspection evaluation
        8. JSON/PDF report generation

    This class only orchestrates the pipeline components.
    It does not implement computer-vision models itself.
    """

    def __init__(
        self,
        tracker,
        selector,
        coverage_pipeline,
        frame_extractor,
        part_pipeline,
        damage_pipeline,
        evaluator,
        report_generator,
    ):
        self.tracker = tracker
        self.selector = selector
        self.coverage_pipeline = coverage_pipeline
        self.frame_extractor = frame_extractor
        self.part_pipeline = part_pipeline
        self.damage_pipeline = damage_pipeline
        self.evaluator = evaluator
        self.report_generator = report_generator

    # ------------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------------

    def _validate_components(self):
        """
        Make sure all required pipeline components are available.
        """

        components = {
            "tracker": self.tracker,
            "selector": self.selector,
            "coverage_pipeline": self.coverage_pipeline,
            "frame_extractor": self.frame_extractor,
            "part_pipeline": self.part_pipeline,
            "damage_pipeline": self.damage_pipeline,
            "evaluator": self.evaluator,
            "report_generator": self.report_generator,
        }

        missing = [
            name
            for name, component in components.items()
            if component is None
        ]

        if missing:
            raise ValueError(
                "Missing pipeline components: "
                + ", ".join(missing)
            )

    # ------------------------------------------------------------------
    # RUN
    # ------------------------------------------------------------------

    def run(self, inspection):
        """
        Execute the complete vehicle-inspection pipeline.

        Parameters
        ----------
        inspection : dict
            Inspection session state created by
            create_inspection_session().

        Returns
        -------
        dict
            Updated inspection state containing:

                - tracking information
                - primary vehicle
                - coverage
                - representative frames
                - vehicle parts
                - damage detections
                - evaluation report
                - generated JSON/PDF report references
        """

        if not isinstance(inspection, dict):
            raise TypeError(
                "inspection must be a dictionary."
            )

        self._validate_components()

        pipeline_start = time.time()

        # ==============================================================
        # 1. VEHICLE TRACKING
        # ==============================================================

        start = time.time()

        print("\n" + "=" * 70)
        print("1. VEHICLE TRACKING")
        print("=" * 70)

        inspection = self.tracker.track(
            inspection
        )

        print(
            "Tracking time:",
            round(time.time() - start, 2),
            "seconds",
        )

        # ==============================================================
        # 2. PRIMARY VEHICLE SELECTION
        # ==============================================================

        start = time.time()

        print("\n" + "=" * 70)
        print("2. PRIMARY VEHICLE SELECTION")
        print("=" * 70)

        inspection = self.selector.select(
            inspection
        )

        print(
            "Selection time:",
            round(time.time() - start, 2),
            "seconds",
        )

        # ==============================================================
        # 3. COVERAGE ESTIMATION
        # ==============================================================

        start = time.time()

        print("\n" + "=" * 70)
        print("3. COVERAGE ESTIMATION")
        print("=" * 70)

        inspection = self.coverage_pipeline.run(
            inspection
        )

        print(
            "Coverage time:",
            round(time.time() - start, 2),
            "seconds",
        )

        # ==============================================================
        # 4. REPRESENTATIVE FRAME EXTRACTION
        # ==============================================================

        start = time.time()

        print("\n" + "=" * 70)
        print("4. REPRESENTATIVE FRAME EXTRACTION")
        print("=" * 70)

        inspection = self.frame_extractor.extract(
            inspection
        )

        print(
            "Frame extraction time:",
            round(time.time() - start, 2),
            "seconds",
        )

        # ==============================================================
        # 5. VEHICLE-PART EXTRACTION
        # ==============================================================

        start = time.time()

        print("\n" + "=" * 70)
        print("5. VEHICLE-PART EXTRACTION")
        print("=" * 70)

        inspection = self.part_pipeline.run(
            inspection
        )

        print(
            "Vehicle-part extraction time:",
            round(time.time() - start, 2),
            "seconds",
        )

        # ==============================================================
        # 6. DAMAGE DETECTION
        # ==============================================================

        start = time.time()

        print("\n" + "=" * 70)
        print("6. DAMAGE DETECTION")
        print("=" * 70)

        inspection = self.damage_pipeline.run(
            inspection
        )

        print(
            "Damage detection time:",
            round(time.time() - start, 2),
            "seconds",
        )

        # ==============================================================
        # 7. INSPECTION EVALUATION
        # ==============================================================

        start = time.time()

        print("\n" + "=" * 70)
        print("7. INSPECTION EVALUATION")
        print("=" * 70)

        evaluation_report = self.evaluator.evaluate(
            inspection
        )

        inspection["report"] = evaluation_report

        print(
            "Evaluation time:",
            round(time.time() - start, 2),
            "seconds",
        )

        # ==============================================================
        # 8. REPORT GENERATION
        # ==============================================================

        start = time.time()

        print("\n" + "=" * 70)
        print("8. REPORT GENERATION")
        print("=" * 70)

        report_result = self.report_generator.generate(
            inspection
        )

        inspection["user_report"] = report_result

        print(
            "Report generation time:",
            round(time.time() - start, 2),
            "seconds",
        )

        # ==============================================================
        # PIPELINE COMPLETE
        # ==============================================================

        total_time = time.time() - pipeline_start

        print("\n" + "=" * 70)
        print("INFERENCE PIPELINE COMPLETE")
        print("=" * 70)

        print(
            "Total pipeline time:",
            round(total_time, 2),
            "seconds",
        )

        return inspection
