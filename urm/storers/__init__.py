import typing
from abc import ABC, abstractmethod

from ..core import KeyT


class Storer(ABC):
	__slots__ = ()

	@abstractmethod
	def get(self, parent: "_ProtoBundle", key: KeyT):
		raise NotImplementedError

	@abstractmethod
	def set(self, parent: "_ProtoBundle", key: KeyT, value: typing.Any):
		raise NotImplementedError


class Cacher(Storer):  # pylint:disable=abstract-method
	__slots__ = ()


class Saver(Storer):  # pylint:disable=abstract-method
	__slots__ = ()
