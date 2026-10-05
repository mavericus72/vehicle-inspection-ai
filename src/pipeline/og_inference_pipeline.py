

class InferencePipeline:

    def __init__(
        self,
        tracker,
        selector,
        coverage_pipeline,
        frame_extractor,
        evaluator,
	report_generator
    ):
        self.tracker = tracker
        self.selector = selector
        self.coverage_pipeline = coverage_pipeline
        self.frame_extractor = frame_extractor
        self.evaluator = evaluator
	self.report_generator = report_generator


    def run(self, inspection):

        # Step 1: Track vehicles
        inspection = self.tracker.track(inspection)

        # Step 2: Select primary vehicle
        inspection = self.selector.select(inspection)

        # Step 3: Estimate coverage
        inspection = self.coverage_pipeline.run(inspection)

        # Step 4: Extract representative frames
        inspection = self.frame_extractor.extract(inspection)

        # Step 5: Generate final report
        inspection["report"] = self.evaluator.evaluate(
            inspection
        )

	inspection["user_report"] = self.report_generator.generate(
    	   inspection
	)

        return inspection