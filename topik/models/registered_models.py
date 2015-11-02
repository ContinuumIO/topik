from six import with_metaclass

class ModelRegistry:
    class __ModelRegistry:
        def __init__(self, cls):
            if cls is not None:
                self.registered_models = {cls.__name__: cls}
            else:
                self.registered_models = {}

        def add(self, cls):
            self.registered_models[cls.__name__] = cls

        def __getitem__(self, cls_name):
            return self.registered_models[cls_name]

    instance = None

    def __init__(self, cls=None):
        if not ModelRegistry.instance:
            ModelRegistry.instance = ModelRegistry.__ModelRegistry(cls)
        elif cls is not None:
            ModelRegistry.instance.add(cls)

    def __getitem__(self, cls_name):
        return getitem(self.instance, cls_name)

    @classmethod
    def get_registry(cls):
        if cls.instance:
            return cls.instance.registered_models
        else:
            raise ImpossibleError('ModelRegistry has not yet been instantiated')

def register_model(cls):
    """Decorator function to register new model with global registry of models"""
    ModelRegistry(cls)
    return cls
