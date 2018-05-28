import sys

__all__ = ['pn']


# class Filter:
#
# 	def __call__(self, caller):
# 		raise NotImplemented
#
# class Manipulable:
#
# 	def __init__(self, name: str):
# 		self.name = name
# 		print("New Manipulable ", name)
#
# 	def __getattr__(self, attname):
# 		print("__getattr__")
# 		class_ = getattr(sys.modules[__name__], attname)
# 		print("class_ ", class_)
# 		return class_(self)