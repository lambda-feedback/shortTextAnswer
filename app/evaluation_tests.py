import unittest

try:
    from .evaluation import evaluation_function
except ImportError:
    from evaluation import evaluation_function

try:
    from .nlp_evaluation_tests import TestEvaluationFunction as NLPTestEvaluationFunction
except ImportError:
    from nlp_evaluation_tests import TestEvaluationFunction as NLPTestEvaluationFunction

try:
    from .slm_evaluation_tests import TestEvaluationFunction as SLMTestEvaluationFunction
except ImportError:
    from slm_evaluation_tests import TestEvaluationFunction as SLMTestEvaluationFunction

class TestEvaluationFunction(unittest.TestCase):
    """
        TestCase Class used to test the algorithm.
        ---
        Tests are used here to check that the algorithm written 
        is working as it should. 
        
        It's best practise to write these tests first to get a 
        kind of 'specification' for how your algorithm should 
        work, and you should run these tests before committing 
        your code to AWS.

        Read the docs on how to use unittest here:
        https://docs.python.org/3/library/unittest.html

        Use evaluation_function() to check your algorithm works 
        as it should.
    """

    def test_combined_evaluation_nlp(self):
        response, answer, params = "light blue", "not light blue", dict(evaluation_type="nlp")
        result = evaluation_function(response, answer, params)

        self.assertEqual(result.get_is_correct(), False, msg=f'{result.serialise()}, Answer: {answer}')

    def test_combined_evaluation_slm(self):
        response, answer, params = "light blue", "not light blue", dict(evaluation_type="slm")
        result = evaluation_function(response, answer, params)
        
        print(result.serialise())
        self.assertEqual(result.get_is_correct(), False, msg=f'{result.serialise()}, Answer: {answer}')

def load_tests(loader, tests, pattern):
    """
    Used to filter out which tests to run, if commented out then all unittests in the project will run.
    To run unittests:
        `python -m unittest app.evaluation_tests`
    """
    suite = unittest.TestSuite()
    
    # Add tests from submodules of unittest
    # suite.addTests(loader.loadTestsFromTestCase(NLPTestEvaluationFunction))
    # suite.addTests(loader.loadTestsFromTestCase(SLMTestEvaluationFunction))
    suite.addTests(loader.loadTestsFromTestCase(TestEvaluationFunction))
    
    return suite

if __name__ == '__main__':
    unittest.main()