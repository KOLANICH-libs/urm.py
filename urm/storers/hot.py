import typing

from . import Cacher
from ..core import KeyT
from ..ProtoBundle import _ProtoBundle
from ..utils import adaptKeyToContainers


class ValueCacher(Cacher):
	__slots__ = ("value",)

	def __init__(self) -> None:
		self.value = None

	def get(self, parent: _ProtoBundle, key: KeyT):
		assert not key, "Key must be always empty for this cacher, but got " + repr(key)
		return self.value

	def set(self, parent: _ProtoBundle, key: KeyT, value: typing.Any):
		assert not key, "Key must be always empty for this cacher, but got " + repr(key)
		self.value = value


class CollectionCacher(ValueCacher):
	__slots__ = ("ctor",)

	def __init__(self, ctor) -> None:
		self.ctor = ctor
		super().__init__()

	def get(self, parent: _ProtoBundle, key: KeyT):
		return self.value[adaptKeyToContainers(key)]

	def set(self, parent: _ProtoBundle, key: KeyT, value: typing.Any):
		if self.value is None:
			self.value = self.ctor()
		self.value[adaptKeyToContainers(key)] = value


class PrefixCacher(Cacher):
	__slots__ = ("prefix",)

	def __init__(self, prefix: str = "_") -> None:
		self.prefix = prefix

	def get(self, parent: _ProtoBundle, key: KeyT) -> typing.Any:
		assert len(key) == 1, "This cacher may be used only with keys of len(key)==1, but got " + repr(key)
		return getattr(parent, self.prefix + key[0], None)

	def set(self, parent: _ProtoBundle, key: KeyT, value: typing.Any) -> None:
		assert len(key) == 1, "This cacher may be used only with keys of len(key)==1, but got " + repr(key)
		setattr(parent, self.prefix + key[0], value)
