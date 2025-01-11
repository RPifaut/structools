import time
import logging
logging.basicConfig(level=logging.INFO)


def timer(func):

    """
    Decorator to time the execution time of a function.
    """

    def wrapper(*args, **kwargs):
        logging.info(f"Running function {func.__name__}")
        start = time.time()
        res = func(*args, **kwargs)
        end = time.time()
        exec_time = end - start
        logging.info(f"Execution completed. Elapsed time= {exec_time:.10f} s")

        return res
    
    return wrapper
