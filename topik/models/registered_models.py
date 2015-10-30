from six import with_metaclass

class Singleton(type):

    def __init__(self, *args, **kwargs):
        super(Singleton, self).__init__(*args, **kwargs)
        self._registered_models = {}


class ModelRegistry(with_metaclass(Singleton)):
    def add(self, cls):
        """Decorator function to register new model with global registry of models"""
        if cls.__name__ not in self._registered_models:
            self._registered_models[cls.__name__] = cls

    def __getitem__(self, cls_name):
        if cls_name in self._registered_models:
            return self._registered_models[cls_name]

def register_model(cls):
    """Decorator function to register new model with global registry of models"""
    ModelRegistry().add(cls)
    return cls
'''

registered_models = {}

def register_model(cls):
    """Decorator function to register new model with global registry of models"""
    if cls.__name__ not in registered_models:
        registered_models[cls.__name__] = cls
    return cls
'''
