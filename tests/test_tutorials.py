# Copyright © 2021 United States Government as represented by the Administrator of the National Aeronautics and Space Administration.  All Rights Reserved.

import unittest
import warnings
import importlib.util


class TestTutorials(unittest.TestCase):

    def test_tutorial_ipynb(self):
        if importlib.util.find_spec('testbook') is None:
            warnings.warn('testbook not installed')
        else:
            from testbook import testbook
            with testbook('./tutorial.ipynb', execute=True) as tb:
                self.assertEqual(tb.__class__.__name__, "TestbookNotebookClient")

def main():
    l = unittest.TestLoader()
    runner = unittest.TextTestRunner()
    print("\n\nTesting Tutorials")
    result = runner.run(l.loadTestsFromTestCase(TestTutorials)).wasSuccessful()

    if not result:
        raise Exception("Failed test") 

if __name__ == '__main__':
    main()
    