import typing

from transformerz.core import TransformerBase

KeyT = typing.Tuple[str, ...]
KeyMapperCallableT = typing.Callable[["_ProtoBundle", "Field", KeyT], KeyT]
SerializerMapperCallableT = typing.Callable[["_ProtoBundle"], TransformerBase]


class Dynamic:
	__slots__ = ("path",)

	def __init__(self, path: typing.Union[KeyT, str]) -> None:
		if isinstance(path, str):
			path = (path,)
		self.path = path

	def __repr__(self):
		return self.__class__.__name__ + "(" + repr(self.path) + ")"
