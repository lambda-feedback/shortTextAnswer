import unittest
try:
    from .evaluation import evaluation_function, Param
except ImportError:
    from evaluation import evaluation_function, Param

class TestEvaluationFunction(unittest.TestCase):
    """
    TestCase Class to test the evaluation function.
    ---
    This test suite validates the correctness of `evaluation_function()` by checking:
    - Whether it correctly identifies correct and incorrect responses.
    - Whether it can handle keystring constraints.
    - Whether it can enforce exact matches.
    - Whether it processes responses efficiently and correctly.

    The function is evaluated using an LLM-based semantic comparison.
    """

    @classmethod
    def setUpClass(cls):
        """Initialize a shared Param instance for LLM setup."""
        cls.param = Param()

    def test_basic_correct_response(self):
        """Test if semantically similar responses are marked correct."""
        response = ["Density", "Velocity", "Viscosity", "Length"]
        answer = ["Density", "Velocity", "Viscosity", "Length"]
        result = evaluation_function(response, answer, self.param)

        self.assertTrue(result.get("is_correct"))

    def test_basic_incorrect_response(self):
        """Test if semantically different responses are marked incorrect."""
        response = ["Mass", "Speed", "Friction", "Force"]
        answer = ["Density", "Velocity", "Viscosity", "Length"]
        result = evaluation_function(response, answer, self.param)

        self.assertFalse(result.get("is_correct"))

    def test_partial_match(self):
        """Test if a response too short is marked incorrect."""
        response = ["Density", "Velocity", "Viscosity"]
        answer = ["Density", "Velocity", "Viscosity", "Length"]

        self.param.response_num_required = 4
        result = evaluation_function(response, answer, self.param)
        self.param.response_num_required = 0
        
        self.assertFalse(result.get("is_correct"))


    def test_synonyms_match(self):
        """Test if abbriviations are correctly identified."""
        response = ['velocity']
        answer = ['speed']
        result = evaluation_function(response, answer, self.param)

        self.assertTrue(result.get("is_correct"))

    def test_exact_match_requirement(self):
        """Test enforcing exact match on keystrings."""
        response = ["density", "speed", "viscosity", "length"]
        answer = ["Density", "Velocity", "Viscosity", "Length"]

        result = evaluation_function(response, answer, self.param)
        self.assertTrue(result.get("is_correct"))

    def test_should_not_contain(self):
        """Test if a response with a prohibited keyword fails."""
        response = ["density", "velocity", "viscosity", "length", "direction"]
        answer = ["Density", "Velocity", "Viscosity", "Length"]

        result = evaluation_function(response, answer, self.param)
        self.assertFalse(result.get("is_correct"))


    def test_negation_handling(self):
        """Test how the model handles negation."""
        response = ["not light blue", "dark blue"]
        answer = ["light blue"]

        result = evaluation_function(response, answer, self.param)

        self.assertFalse(result.get("is_correct"))

    def test_performance(self):
        """Ensure that processing time is reasonable."""
        response = ["Density", "Velocity", "Viscosity", "Length"]
        answer = ["Density", "Velocity", "Viscosity", "Length"]

        result = evaluation_function(response, answer, self.param)
        processing_time = result.get("result", {}).get("processing_time", 0)

        self.assertLess(processing_time, 5, msg="Evaluation function should run efficiently.")

if __name__ == "__main__":
    unittest.main()