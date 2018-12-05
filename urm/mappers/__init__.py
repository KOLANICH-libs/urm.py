import typing
from abc import ABC, abstractmethod

from ..core import KeyMapperCallableT, SerializerMapperCallableT, KeyT
from ..storers import Storer, Saver, Cacher


class Mapper(ABC):
	"""Groups mapping required for storage of the data."""

	__slots__ = ("key", "storer")

	def __init__(self, keyMapper: KeyMapperCallableT, storer: Storer) -> None:
		self.key = keyMapper
		self.storer = storer

	def load(self, parent: "_ProtoBundle", field: "Field", key: KeyT) -> typing.Any:
		path = self.key(parent, field, key)
		rawRes = self.storer.get(parent, path)
		return rawRes

	def save(self, parent: "_ProtoBundle", field: "Field", key: KeyT, value: typing.Any) -> None:
		path = self.key(parent, field, key)
		self.storer.set(parent, path, value)


class HotMapper(Mapper):
	"""Groups mapping required for caching of the data."""

	__slots__ = ()

	def __init__(self, keyMapper: KeyMapperCallableT, storer: Cacher) -> None:
		super().__init__(keyMapper, storer)


class ColdMapper(Mapper):
	"""Groups mapping required for COLD storage of the data."""

	__slots__ = ("serializer",)

	def __init__(self, keyMapper: KeyMapperCallableT, storer: Saver, serializerMapper: SerializerMapperCallableT) -> None:
		super().__init__(keyMapper, storer)
		self.key = keyMapper
		self.serializer = serializerMapper

	def load(self, parent: "_ProtoBundle", field: "Field", key: KeyT) -> typing.Any:
		rawRes = super().load(parent, field, key)
		ser = self.serializer(parent)
		return ser.process(rawRes)

	def save(self, parent: "_ProtoBundle", field: "Field", key: KeyT, value: typing.Any) -> None:
		ser = self.serializer(parent)
		rawRes = ser.unprocess(value)
		super().save(parent, field, key, rawRes)
