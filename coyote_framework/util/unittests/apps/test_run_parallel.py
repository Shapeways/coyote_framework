import unittest
import time
from coyote_framework.util.apps.parallel import run_parallel, ErrorInProcessException

__author__ = 'justin@shapeways.com'


class TestRunParallel(unittest.TestCase):

    def test_error_capture(self):
        """Tests the error "capture" functionality of run_parallel. When an exception is raised in a process,
        the parent process will hang forever. So we should be capturing the errors and attaching them onto the
        exception thrown in the parent process.
        """

        def function_no_error():
            return 1+1

        def funtion_error():
            raise ValueError('Error in values!')

        try:
            val1, val2 = run_parallel(
                function_no_error,
                funtion_error
            )
        except Exception, e:
            self.assertIsInstance(e, ErrorInProcessException)
            self.assertEqual(1, len(e.errors))

    def test_return_value_order(self):
        """Tests that return values are returned in the order the functions are passed to run_parallel"""
        def return_first():
            time.sleep(0.0)
            return 1

        def return_second():
            time.sleep(0.1)
            return 2

        def return_third():
            time.sleep(0.2)
            return 3

        def return_fourth():
            time.sleep(0.3)
            return 4

        val1, val2, val3, val4 = run_parallel(
            return_second,
            return_first,
            return_third,
            return_fourth
        )

        self.assertEqual(val1, 2)
        self.assertEqual(val2, 1)
        self.assertEqual(val3, 3)
        self.assertEqual(val4, 4)