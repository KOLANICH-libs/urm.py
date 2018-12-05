import typing
from abc import ABC, abstractmethod

from .core import KeyT
from .mappers import ColdMapper, HotMapper


class FieldStrategy(ABC):
	"""Defines a storage-backed field in a class."""

	__slots__ = ("name", "cold")

	def __init__(self, cold: ColdMapper, name: typing.Optional[str] = None) -> None:
		self.name = name
		self.cold = cold

	@abstractmethod
	def get(self, parent: "_ProtoBundle", key: KeyT) -> typing.Any:
		raise NotImplementedError

	@abstractmethod
	def set(self, parent: "_ProtoBundle", key: KeyT, newV: typing.Any) -> None:
		raise NotImplementedError


class ColdStrategy(FieldStrategy):
	"""Defines a storage-backed uncached immediately-written field in a class."""

	__slots__ = ()

	def get(self, parent: "_ProtoBundle", key: KeyT) -> typing.Any:
		return self.cold.load(parent, self, key)

	def set(self, parent: "_ProtoBundle", key: KeyT, newV: typing.Any) -> None:
		self.cold.save(parent, self, key, newV)


class CachedStrategy(FieldStrategy):
	"""Defines a storage-backed cached field in a class."""

	__slots__ = ("hot", "modified")

	def __init__(self, cold: ColdMapper, hot: HotMapper, name: typing.Optional[str] = None) -> None:
		super().__init__(cold, name)
		self.hot = hot
		self.modified = set()

	def get(self, parent: "_ProtoBundle", key: KeyT) -> typing.Any:
		res = self.hot.load(parent, self, key)
		if res is None:
			res = self.cold.load(parent, self, key)
			self.hot.save(parent, self, key, res)
		return res

	def set(self, parent: "_ProtoBundle", key: KeyT, newV: typing.Any) -> None:
		self.hot.save(parent, self, key, newV)
		self.modified |= {key}

	def _saveItem(self, parent: "_ProtoBundle", key: KeyT) -> None:
		res = self.hot.load(parent, self, key)
		self.cold.save(parent, self, key, res)

	def save(self, parent: "_ProtoBundle", key: KeyT = None) -> None:
		if key is not None:
			self._saveItem(parent, key)
			self.modified -= {key}
		else:
			self._saveAll(parent)

	def _saveAll(self, parent: "_ProtoBundle") -> None:
		for key in self.modified:
			self._saveItem(parent, key)
		self.modified = type(self.modified)()


class _Field:
	__slots__ = ("strategy",)

	def __init__(self, strategy) -> None:
		self.strategy = strategy

	def __set_name__(self, owner: typing.Type["_ProtoBundle"], name: str) -> None:
		if self.strategy.name is None:
			self.strategy.name = name

	def save(self, parent: "_ProtoBundle"):
		return self.strategy.save(parent)


class Field(_Field):
	__slots__ = ()

	def __init__(self, cold: ColdMapper, hot: HotMapper = None, name: typing.Optional[str] = None) -> None:
		if hot is None:
			strategy = ColdStrategy(cold, name)
		else:
			strategy = CachedStrategy(cold, hot, name)
		super().__init__(strategy)


class Field0D(Field):
	__slots__ = ()

	def __get__(self, inst: "_ProtoBundle", cls: typing.Optional[typing.Type["_ProtoBundle"]] = None) -> typing.Any:
		if inst is not None:
			return self.strategy.get(inst, ())
		else:
			return self

	def __set__(self, inst: "_ProtoBundle", newV: typing.Any) -> None:
		if inst is not None:
			self.strategy.set(inst, (), newV)


class FieldNDAccessor:
	__slots__ = ("strategy", "parent")

	def __init__(self, strategy, parent):
		self.strategy = strategy
		self.parent = parent

	def __getitem__(self, key: KeyT) -> typing.Any:
		return self.strategy.get(self.parent, key)

	def __setitem__(self, key: KeyT, newV: typing.Any) -> None:
		self.strategy.set(self.parent, key, newV)


class FieldND(Field):
	__slots__ = ()

	def __get__(self, inst: "_ProtoBundle", cls=None) -> typing.Any:
		if inst is not None:
			return FieldNDAccessor(self.strategy, inst)
		else:
			return self

	def __set__(self, inst: "_ProtoBundle", newV: typing.Any) -> None:
		raise NotImplementedError
