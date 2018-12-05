import typing
from pathlib import Path

from . import Saver
from ..core import Dynamic, KeyT
from ..ProtoBundle import _ProtoBundle
from ..utils import resolveDynamics


class FileSaver(Saver):
	__slots__ = ("root", "ext")

	def __init__(self, root: typing.Union[Dynamic, Path], ext: str = None) -> None:
		self.root = root
		self.ext = ext

	def getFSPath(self, parent: _ProtoBundle, key: KeyT) -> Path:  # pylint:disable=unused-argument
		root = resolveDynamics(parent, self.root)
		ext = resolveDynamics(parent, self.ext)
		if ext is not None:
			return root._make_child(key[:-1])._make_child((".".join((key[-1], ext)),))
		return root._make_child(key)

	def get(self, parent: _ProtoBundle, key: KeyT):
		return self.getFSPath(parent, key).read_bytes()

	def set(self, parent: _ProtoBundle, key: KeyT, value: typing.Any) -> int:
		p = self.getFSPath(parent, key)
		p.parent.mkdir(parents=True, exist_ok=True)
		return p.write_bytes(value)
