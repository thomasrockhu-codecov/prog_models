# Copyright © 2021 United States Government as represented by the Administrator of the National Aeronautics and Space Administration.  All Rights Reserved.

import unittest
from prog_models.sim_result import SimResult, LazySimResult

class TestSimResult(unittest.TestCase):
    def test_sim_result(self):
        NUM_ELEMENTS = 5
        time = list(range(NUM_ELEMENTS))
        state = [i * 2.5 for i in range(NUM_ELEMENTS)]
        result = SimResult(time, state)
        self.assertListEqual(list(result), state)
        self.assertListEqual(result.times, time)
        for i in range(5):
            self.assertEqual(result.time(i), time[i])
            self.assertEqual(result[i], state[i])

        try:
            tmp = result[NUM_ELEMENTS]
            self.fail("Should be out of range error")
        except IndexError:
            pass

        try:
            tmp = result.time(NUM_ELEMENTS)
            self.fail("Should be out of range error")
        except IndexError:
            pass
    
    def test_pickle(self):
        NUM_ELEMENTS = 5
        time = list(range(NUM_ELEMENTS))
        state = [i * 2.5 for i in range(NUM_ELEMENTS)]
        result = SimResult(time, state)
        import pickle
        pickle.dump(result, open('model_test.pkl', 'wb'))
        result2 = pickle.load(open('model_test.pkl', 'rb'))
        self.assertEqual(result, result2)

    def test_pickle_lazy(self):
        def f(x):
            return x * 2
        NUM_ELEMENTS = 5
        time = list(range(NUM_ELEMENTS))
        state = [i * 2.5 for i in range(NUM_ELEMENTS)]
        lazy_result = LazySimResult(f, time, state) # Ordinary LazySimResult with f, time, state
        sim_result = SimResult(time, state) # Ordinary SimResult with time,state

        # Casting LazySimResult to  SimResult? or rather, building a new obj with manipulated time,state
        converted_lazy_result = SimResult(lazy_result.times, lazy_result.data)
        self.assertNotEqual(sim_result, converted_lazy_result) # converted is not the same as the original SimResult

        import pickle # try pickle'ing
        pickle.dump(converted_lazy_result, open('model_test.pkl', 'wb'))
        pickle_converted_result = pickle.load(open('model_test.pkl', 'rb'))
        self.assertEqual(converted_lazy_result, pickle_converted_result)
    
    def test_cached_sim_result(self):
        def f(x):
            return x * 2
        NUM_ELEMENTS = 5
        time = list(range(NUM_ELEMENTS))
        state = [i * 2.5 for i in range(NUM_ELEMENTS)]
        result = LazySimResult(f, time, state)
        self.assertFalse(result.is_cached())
        self.assertListEqual(result.times, time)
        for i in range(5):
            self.assertEqual(result.time(i), time[i])
            self.assertEqual(result[i], state[i]*2)
        self.assertTrue(result.is_cached())

        try:
            tmp = result[NUM_ELEMENTS]
            self.fail("Should be out of range error")
        except IndexError:
            pass

        try:
            tmp = result.time(NUM_ELEMENTS)
            self.fail("Should be out of range error")
        except IndexError:
            pass

        # Catch bug that occured where lazysimresults weren't actually different
        # This occured because the underlying arrays of time and state were not copied (see PR #158)
        result = LazySimResult(f, time, state)
        result2 = LazySimResult(f, time, state)
        self.assertTrue(result == result2)
        self.assertEqual(len(result), len(result2))
        result.extend(LazySimResult(f, time, state))
        self.assertFalse(result == result2)
        self.assertNotEqual(len(result), len(result2))

# This allows the module to be executed directly
def run_tests():
    unittest.main()
    
def main():
    # This ensures that the directory containing ProgModelTemplate is in the python search directory
    import sys
    from os.path import dirname, join
    sys.path.append(join(dirname(__file__), ".."))

    l = unittest.TestLoader()
    runner = unittest.TextTestRunner()
    print("\n\nTesting Sim Result")
    result = runner.run(l.loadTestsFromTestCase(TestSimResult)).wasSuccessful()

    if not result:
        raise Exception("Failed test")

if __name__ == '__main__':
    main()
