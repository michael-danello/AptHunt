"""Wrapper Utilities"""

import logging
import time
from functools import wraps


def log_time(f):

    @wraps(f)
    def decorator(*args, **kwargs):
        start = time.time()
        res = f(*args, **kwargs)
        end = time.time()
        
        logging.info("{} took {:.2f} to execute".format(f.__name__, end-start))

        return res
    
    return decorator


def delay_execution(seconds=1):
    """Delay function exectuion"""

    def decorator(f):
        
        @wraps(f)
        def decorated(*args, **kwargs):
            """Nested decorator"""
            time.sleep(seconds) 
            return f(*args, **kwargs)
        
        return decorated
    
    return decorator



        
    
