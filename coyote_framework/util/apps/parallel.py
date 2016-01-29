from multiprocessing import Process, Queue
import warnings


class ErrorInProcessException(RuntimeError):
    """Exception raised when one or more parallel processes raises an exception"""

    def  __init__(self, message, errors, *args, **kwargs):
        self.message = message
        self.errors = errors
        super(ErrorInProcessException, self).__init__(message, *args, **kwargs)

    def __repr__(self):
        return '{}({}, {})'.format(self.__class__.__name__, self.message, self.errors)


def run_parallel(*functions):
    """Runs a series of functions in parallel. Return values are ordered by the order in which their functions
    were passed.

        >>> val1, val2 = run_parallel(
        >>>     lambda: 1 + 1
        >>>     lambda: 0
        >>> )

    If an exception is raised within one of the processes, that exception will be caught at the process
    level and raised by the parent process as an ErrorInProcessException, which will track all errors raised in all
    processes.

    You can catch the exception raised for more details into the process exceptions:

        >>> try:
        >>>     val1, val2 = run_parallel(fn1, fn2)
        >>> except ErrorInProcessException, e:
        >>>     print.e.errors

    @param functions: The functions to run specified as individual arguments
    @return: List of results for those functions. Unpacking is recommended if you do not need to iterate over the
    results as it enforces the number of functions you pass in.

        >>> val1, val2 = run_parallel(fn1, fn2, fn3)  # Will raise an error
        >>> vals = run_parallel(fn1, fn2, fn3)  # Will not raise an error

    @raise: ErrorInProcessException
    """
    def target(fn):
        def wrapped(results_queue, error_queue, index):
            result = None
            try:
                result = fn()
            except Exception, e:  # Swallow errors or else the process will hang
                error_queue.put(e)
                warnings.warn('Exception raised in parallel threads: {}'.format(e))
            results_queue.put((index, result))
        return wrapped

    errors = Queue()
    queue = Queue()

    jobs = list()
    for i, function in enumerate(functions):
        jobs.append(Process(target=target(function), args=(queue, errors, i)))

    [job.start() for job in jobs]
    [job.join() for job in jobs]

    # Get the results in the queue and put them back in the order in which the function was specified in the args
    results = [queue.get() for _ in jobs]
    results = sorted(results, key=lambda x: x[0])

    if not errors.empty():
        error_list = list()
        while not errors.empty():
            error_list.append(errors.get())
        raise ErrorInProcessException('Exceptions raised in parallel threads: {}'.format(error_list), errors=error_list)
    return [r[1] for r in results]