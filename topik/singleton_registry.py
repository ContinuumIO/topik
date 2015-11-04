"""Topik uses a modular design at each step in the topic modeling process, to support
future extension.  One of the core concepts here is that we provide registries for each
step that can be extended through registration using a decorator.

The general pattern for using this registry is to subclass BaseRegistry, and then
create a new decorator that uses that registry:

register = functools.partial(_base_register_decorator, RegistrySubclass())

we keep the name as simply register across all files for simplicity, but the register decorator
in each folder is using a different registry specific to that folder.  See the _registry.py module
in each folder.
"""





def _base_register_decorator(registry, func):
    """Decorator function to register new model with global registry of models.

    registry should be the instance of the individual registry to use.

    This function is meant to be used with functools.partial, such that
    the registry is not generally explicitly specified when registering functions.
    """
    registry[func.__name__] = func
    return func