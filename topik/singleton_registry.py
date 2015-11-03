from six import with_metaclass


class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class BaseRegistry(with_metaclass(Singleton, dict)):
    pass


def base_register_decorator(registry, func):
    """Decorator function to register new model with global registry of models.

    registry should be the instance of the individual registry to use.

    This function is meant to be used with functools.partial, such that
    the registry is not generally explicitly specified when registering functions.
    """
    registry[func.__name__] = func
    return func