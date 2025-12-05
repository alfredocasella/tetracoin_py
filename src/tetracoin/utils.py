import warnings
import functools

def deprecated(reason):
    """
    This is a decorator which can be used to mark functions
    and classes as deprecated. It will result in a warning being
    emitted when the function is used.
    """
    def decorator(func1):
        if hasattr(func1, "__name__"):
            fmt = "Call to deprecated function {name} ({reason})."
            func_name = func1.__name__
        else:
            fmt = "Call to deprecated class {name} ({reason})."
            func_name = func1.__class__.__name__

        @functools.wraps(func1)
        def new_func1(*args, **kwargs):
            warnings.simplefilter('always', DeprecationWarning)
            warnings.warn(
                fmt.format(name=func_name, reason=reason),
                category=DeprecationWarning,
                stacklevel=2
            )
            warnings.simplefilter('default', DeprecationWarning)
            return func1(*args, **kwargs)
        return new_func1
    return decorator
