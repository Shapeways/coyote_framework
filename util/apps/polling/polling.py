import time

__author__ = 'justin'


def poll(function, step=0.5, timeout=3, ignore_exceptions=(), exception_message='', message_builder=None,
         args=(), kwargs=None, ontimeout=()):
    """Calls the function until bool(return value) is truthy

    @param step: Wait time between each function call
    @param timeout: Max amount of time that will elapse. If the function is in progress when timeout has passed, the
    function will be allowed to complete.
    @type ignore_exceptions: tuple
    @param ignore_exceptions: A tuple of exceptions that will be ignored if they are raised
    @param exception_message: The message that will be raised as an AssertionError if the function never
    returns bool(True)
    @param ontimeout: On timeout, execute the functions in order, but do not fail if execution fails
    @return: True
    """
    # Validate usage
    try:
        iter(ontimeout)
    except TypeError:
        raise ValueError('Please specify an iterable of callable functions for ontimeout')

    kwargs = kwargs or dict()

    end_time = time.time() + timeout
    while True:
        try:
            value = function(*args, **kwargs)
            if bool(value):
                return value
        except ignore_exceptions:
            pass
        time.sleep(step)
        if time.time() > end_time:
            break

    # Execute the callbacks
    for fn in ontimeout:
        try:
            fn(),
        except:
            continue

    if message_builder:
        exception_message = message_builder(*args, **kwargs)

    raise AssertionError(exception_message)