import sys


class Manipulable:
    """ This class represents an object that can be manipulated. """

    def __getattr__(self, attname):
        class_ = getattr(sys.modules["pmlab_lite.log.transformations"],
                         attname)
        return class_(self)


class Filter:
    """ This class represents a filter
    that can be used to manipulate a manipulable. """

    def __call__(self, caller):
        raise NotImplementedError
