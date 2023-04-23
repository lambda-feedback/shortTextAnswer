import unittest

try:
    from .evaluation import evaluation_function
except ImportError:
    from evaluation import evaluation_function

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
    def test_returns_is_correct_true(self):
        response, answer, params = "A xor gate takes 2 inputs", "There are 2 inputs in a xor gate", dict()
        result = evaluation_function(response, answer, params)
        
        self.assertEqual(result.get("is_correct"), True)

    def test_reynolds_number_is_correct(self):
        answer, params = 'Density, Velocity, Viscosity, Length', dict()
        correct_responses = [
            'density,velocity,viscosity,length',
            'Density,Velocity,Viscosity,Length',
            'density,characteristic velocity,viscosity,characteristic length',
            'Density,Velocity,Shear viscosity,Length',
            #'density,velocity,viscosity,lengthscale',
            'density,velocity,shear viscosity,length',
            #'density,characteristic velocity,shear viscosity,characteristic lengthscale',
            #'density,velocity,shear viscosity,characteristic lengthscale',
            'density,velocity,viscosity,length scale',
            'pressure,characteristic velocity of flow,shear viscosity,characteristic length scale',
        ]

        for response in correct_responses:
            result = evaluation_function(response, answer, params)

            self.assertEqual(result.get("is_correct"), True, msg=f'Response: {response}')

    def test_reynolds_number_is_incorrect(self):
        answer, params = 'Density, Velocity, Viscosity, Length', dict()
        incorrect_responses = [
            #'density,,,',
            #'rho,u,mu,L',
            #'density,velocity,visc,',
        ]

        for response in incorrect_responses:
            result = evaluation_function(response, answer, params)

            self.assertEqual(result.get("is_correct"), False, msg=f'Response: {response}')

if __name__ == "__main__":
    unittest.main()