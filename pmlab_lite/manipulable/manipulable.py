import sys


class Manipulable:
    """ This class represents an object that can be manipulated. """

    def __getattr__(self, attname):
        class_ = getattr(sys.modules[__name__], attname)
        return class_(self)