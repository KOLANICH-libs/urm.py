import typing

from .core import Dynamic, KeyT


def getPathAttr(parent: typing.Any, path: KeyT) -> typing.Any:
	v = parent
	for comp in path:
		v = getattr(v, comp)
	return v


def setPathAttr(parent: typing.Any, path: KeyT, v: typing.Any):
	o = parent
	for comp in path[:-1]:
		o = getattr(o, comp)
	setattr(o, path[-1], v)


def adaptKeyToContainers(key: KeyT) -> typing.Union[str, KeyT]:
	if len(key) == 1:
		return key[0]
	return key


def toKey(key: typing.Union[str, KeyT]) -> KeyT:
	if not isinstance(key, tuple):
		return (key,)

	return key


def resolveDynamics(parent: typing.Any, key: KeyT) -> typing.Any:
	if isinstance(key, Dynamic):
		return getPathAttr(parent, key.path)
	if isinstance(key, tuple):
		return tuple(resolveDynamics(parent, el) for el in key)
	return key
