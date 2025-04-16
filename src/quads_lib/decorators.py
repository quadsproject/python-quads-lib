def returns(resource_type):
    """
    Decorator to annotate methods with the resource type they return.
    """

    def decorator(func):
        func._returns = resource_type
        return func

    return decorator
