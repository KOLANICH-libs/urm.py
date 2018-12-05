import typing

from ..core import KeyT
from ..utils import resolveDynamics, toKey


class PrefixKeyMapper:
	__slots__ = ("prefix",)

	def __init__(self, *prefix: typing.Tuple[str]) -> None:
		self.prefix = tuple(prefix)

	def __call__(self, parent: "_ProtoBundle", field: "Field", key: KeyT) -> KeyT:
		return toKey(resolveDynamics(parent, self.prefix)) + toKey(key)


class PostfixKeyMapper:
	__slots__ = ("postfix",)

	def __init__(self, *postfix):
		self.postfix = postfix

	def __call__(self, parent: "_ProtoBundle", field: "Field", key: KeyT) -> KeyT:
		return toKey(key) + toKey(resolveDynamics(parent, self.postfix))


def fieldNameKeyMapper(parent: "_ProtoBundle", field: "Field", key: KeyT) -> KeyT:  # pylint:disable=unused-argument
	return toKey(field.name) + toKey(key)
