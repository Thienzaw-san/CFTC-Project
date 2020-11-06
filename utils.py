from timeit import default_timer as timer
from datetime import timedelta


def func_name():
    import traceback
    return traceback.extract_stack(None, 2)[0][2]


def timeit(method):
    def timed(*args, **kw):
        ts = timer()
        result = method(*args, **kw)
        te = timer()
        print('ran', method.__name__, 'in', timedelta(seconds=te - ts))
        return result
    return timed

