class Namespace(dict):

    def __init__(self, **kwargs) -> None:
        """
        Init the namespace object
        :param kwargs: Keyword args
        """
        self.attrs.append("Error")
        for attr in self.attrs:
            setattr(self, attr, kwargs.get(attr))

    def __repr__(self):
        return str(self.__dict__)

    def __str__(self):
        return self.__class__.__name__
