from topik.singleton_registry import BaseRegistry

def register_model(func):
    """Decorator function to register new model with global registry of models"""
    ModelRegistry()[func.__name__] = func
    return func

class ModelRegistry(BaseRegistry):
    pass

