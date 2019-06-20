class Namespace:

    def __init__(self, **kwargs) -> None:
        """
        Init the namespace object
        :param kwargs: Keyword args
        """
        for attr in self.attrs:
            setattr(self, attr, kwargs.get(attr))
