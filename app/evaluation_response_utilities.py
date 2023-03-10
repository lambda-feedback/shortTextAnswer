class EvaluationResponse:
    def __init__(self):
        self.is_correct = False
        self._feedback = []
        self._feedback_tags = {}
        self.latex = ""
        self.result = {}

    def get_feedback(self, tag):
        return self._feedback_tags.get(tag, None)

    def add_feedback(self, tag, feedback):
        self._feedback.append(feedback)
        self._feedback_tags.update({tag: len(self._feedback)-1})

    def _serialise_feedback(self) -> str:
        return "<br>".join(x[1] if isinstance(x, tuple) else x for x in self._feedback)

    def serialise(self, include_test_data=False) -> dict:
        out = dict(is_correct=self.is_correct, feedback=self._serialise_feedback(), tags=self._feedback_tags, result=self.result)
        if self.latex:
            out.update(dict(response_latex=self.latex))
        return out
