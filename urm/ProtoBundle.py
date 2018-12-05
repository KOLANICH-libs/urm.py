import typing
from abc import ABC, ABCMeta

from .fields import Field, FieldND, CachedStrategy


class _ProtoBundle(ABC):
	__slots__ = ()
	__SAVED_ATTRS__ = frozenset()


class ProtoBundleMeta(ABCMeta):
	__slots__ = ()

	def __new__(cls: typing.Type["ProtoBundleMeta"], className: str, parents: typing.Tuple[type, ...], attrs: typing.Dict[str, typing.Any], *args, **kwargs) -> typing.Type["_ProtoBundle"]:
		attrs = type(attrs)(attrs)
		savedAttrs = []
		attsToSetParent = []
		for k, v in attrs.items():
			if isinstance(v, Field):
				if isinstance(v.strategy, CachedStrategy):
					savedAttrs.append(k)
		if savedAttrs:
			attrs["__SAVED_ATTRS__"] = parents[0].__SAVED_ATTRS__ | frozenset(savedAttrs)
		res = super().__new__(cls, className, parents, attrs, *args, **kwargs)
		return res


class ProtoBundle(_ProtoBundle, metaclass=ProtoBundleMeta):
	__slots__ = ()

	def _saveProp(self, propName: str) -> None:
		prop = getattr(self.__class__, propName)
		prop.strategy.save(self)

	def save(self, propName: typing.Optional[str] = None) -> None:
		if propName is None:
			for a in self.__class__.__SAVED_ATTRS__:
				self._saveProp(a)
		else:
			self._saveProp(propName)
