# from collections import deque
# # Deque uses only recent no. of predictions.Eg (deque(max_lent(10)) - retain only 10 recent predictions
#
# class CoverageEstimator:
#
#     def __init__(
#         self,
#         confidence_threshold=0.60,
#         min_observations=5,
#         smoothing_window=10,
#         vote_threshold=2.5
#     ):
# # confidence_threshold = Minimum confidence required to accept a view prediction
# # min_observations= Number of stable observations required before marking a view as covered
# # smoothing_window= Number of recent predictions used for temporal voting
# # vote_threshold= Minimum sum of accumulated confidence_scores required for a stable view
#
#         self.confidence_threshold = confidence_threshold
#         self.min_observations = min_observations
#         self.vote_threshold = vote_threshold
# 	    # self.smoothing_window = smoothing_window
#         self.history = deque(maxlen=smoothing_window)	# I don't need to remember the number 10 separately. I only need to use it to configure my deque
#
#     def update(
#         self,
#         inspection,
#         prediction,
#         frame_idx
#     ):
#
#         # Normalize predicted label
#         view = prediction["view"].lower().strip()
#         confidence = prediction["confidence"]
#
#         # Ignore weak predictions
#         if confidence < self.confidence_threshold:
#             return None
#
#         # Store both view and confidence
#         self.history.append({
#             "view": view,
#             "confidence": confidence
#         })	# We need confidence weighted voting. So we take view and confidence
#
#
#         # Confidence-weighted temporal voting
#
#         votes = {}
#
#         for item in self.history:
#
#             votes[item["view"]] = (
#                 votes.get(item["view"], 0.0)
#                 + item["confidence"]
#             )
#
#         stable_view = max(
#             votes,
#             key=votes.get
#         )
#
#         stable_score = votes[stable_view]
#
#         # Ignore unstable predictions
#         if stable_score < self.vote_threshold:
#             return None
#
#
#         # Store history
#
#         inspection["view_history"].append({
#
#             "frame": frame_idx,
#             "raw_view": view,
#             "stable_view": stable_view,
#             "confidence": confidence
#
#         })
#
#         inspection["view_counts"][stable_view] += 1
#
#         inspection["view_confidences"][stable_view].append(
#             confidence
#         )
#
#
#         # Representative frame
#
#         best = inspection["best_views"][stable_view]
#
#         if confidence > best["confidence"]:
#
#             best["confidence"] = confidence
#             best["frame"] = frame_idx
#
#         # Coverage estimation
#
#         if (
#             inspection["view_counts"][stable_view]
#             >= self.min_observations):
#
#             inspection["coverage"][stable_view] = True
#
#         inspection["coverage_complete"] = all(
#             inspection["coverage"].values()
#         )
#
#         return stable_view


from collections import deque


class CoverageEstimator:

    VIEWS = [
        "front",
        "rear",
        "left",
        "right",
    ]

    def __init__(
        self,
        confidence_threshold=0.60,
        min_observations=5,
        smoothing_window=10,
        vote_threshold=2.5,
    ):
        """
        Estimate vehicle-view coverage using
        confidence-weighted temporal voting.

        Args:
            confidence_threshold:
                Minimum classifier confidence required
                for a prediction to participate.

            min_observations:
                Number of stable observations required
                before a view is considered covered.

            smoothing_window:
                Number of recent predictions retained
                for temporal voting.

            vote_threshold:
                Minimum accumulated confidence score
                required for a stable view.
        """

        self.confidence_threshold = (
            confidence_threshold
        )

        self.min_observations = (
            min_observations
        )

        self.vote_threshold = (
            vote_threshold
        )

        self.smoothing_window = (
            smoothing_window
        )

        self.history = deque(
            maxlen=smoothing_window
        )

        self._active_session_id = None


    def reset(self):
        """
        Reset temporal prediction history.
        """

        self.history.clear()


    def update(
        self,
        inspection,
        prediction,
        frame_idx,
    ):
        """
        Process one view-classification prediction.

        Returns:
            Stable view name if a stable view is
            established, otherwise None.
        """

        # ----------------------------------------------------------
        # RESET WHEN A NEW INSPECTION STARTS
        # ----------------------------------------------------------

        session_id = inspection.get(
            "session_id"
        )

        if (
            self._active_session_id
            != session_id
        ):

            self.reset()

            self._active_session_id = (
                session_id
            )


        # ----------------------------------------------------------
        # VALIDATE PREDICTION
        # ----------------------------------------------------------

        if not prediction:
            return None

        if "view" not in prediction:
            return None

        if "confidence" not in prediction:
            return None


        # ----------------------------------------------------------
        # NORMALIZE PREDICTION
        # ----------------------------------------------------------

        view = str(
            prediction["view"]
        ).lower().strip()

        try:

            confidence = float(
                prediction["confidence"]
            )

        except (
            TypeError,
            ValueError,
        ):

            return None


        if view not in self.VIEWS:
            return None


        # ----------------------------------------------------------
        # IGNORE WEAK PREDICTIONS
        # ----------------------------------------------------------

        if (
            confidence
            < self.confidence_threshold
        ):
            return None


        # ----------------------------------------------------------
        # STORE PREDICTION
        # ----------------------------------------------------------

        self.history.append({

            "view": view,

            "confidence": confidence,

        })


        # ----------------------------------------------------------
        # CONFIDENCE-WEIGHTED TEMPORAL VOTING
        # ----------------------------------------------------------

        votes = {}

        for item in self.history:

            item_view = item["view"]

            item_confidence = (
                item["confidence"]
            )

            votes[item_view] = (
                votes.get(
                    item_view,
                    0.0,
                )
                + item_confidence
            )


        if not votes:
            return None


        # ----------------------------------------------------------
        # SELECT STABLE VIEW
        # ----------------------------------------------------------

        stable_view = max(
            votes,
            key=votes.get,
        )

        stable_score = votes[
            stable_view
        ]


        # ----------------------------------------------------------
        # IGNORE UNSTABLE PREDICTIONS
        # ----------------------------------------------------------

        if (
            stable_score
            < self.vote_threshold
        ):
            return None


        # ----------------------------------------------------------
        # STORE VIEW HISTORY
        # ----------------------------------------------------------

        inspection.setdefault(
            "view_history",
            []
        )

        inspection[
            "view_history"
        ].append({

            "frame": frame_idx,

            "raw_view": view,

            "stable_view": stable_view,

            "confidence": confidence,

            "stable_score": stable_score,

        })


        # ----------------------------------------------------------
        # UPDATE VIEW COUNTS
        # ----------------------------------------------------------

        inspection.setdefault(
            "view_counts",
            {
                view: 0
                for view in self.VIEWS
            },
        )

        inspection[
            "view_counts"
        ][stable_view] += 1


        # ----------------------------------------------------------
        # UPDATE CONFIDENCE HISTORY
        # ----------------------------------------------------------

        inspection.setdefault(
            "view_confidences",
            {
                view: []
                for view in self.VIEWS
            },
        )

        inspection[
            "view_confidences"
        ][stable_view].append(
            confidence
        )


        # ----------------------------------------------------------
        # UPDATE BEST VIEW
        # ----------------------------------------------------------

        inspection.setdefault(
            "best_views",
            {
                view: {
                    "frame": None,
                    "confidence": 0.0,
                }
                for view in self.VIEWS
            },
        )

        best = inspection[
            "best_views"
        ][stable_view]


        if confidence > best[
            "confidence"
        ]:

            best[
                "confidence"
            ] = confidence

            best[
                "frame"
            ] = frame_idx


        # ----------------------------------------------------------
        # UPDATE COVERAGE
        # ----------------------------------------------------------

        inspection.setdefault(
            "coverage",
            {
                view: False
                for view in self.VIEWS
            },
        )


        if (
            inspection[
                "view_counts"
            ][stable_view]
            >= self.min_observations
        ):

            inspection[
                "coverage"
            ][stable_view] = True


        # ----------------------------------------------------------
        # UPDATE COMPLETE STATUS
        # ----------------------------------------------------------

        inspection[
            "coverage_complete"
        ] = all(
            inspection[
                "coverage"
            ].values()
        )


        return stable_view
