import functools
import traceback

def catch_exceptions(job_func, cancel_on_failure=False, logger=None):
    @functools.wraps(job_func)
    def wrapper(*args, **kwargs):
        try:
            return job_func(*args, **kwargs)
        except:
            if logger:
                logger.error(traceback.format_exc())
            else:
                print(traceback.format_exc())

            if cancel_on_failure:
                return schedule.CancelJob

    return wrapper
