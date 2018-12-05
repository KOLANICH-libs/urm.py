import typing

from transformerz.core import TransformerBase

from ..core import Dynamic
from ..utils import resolveDynamics


class JustReturnSerializerMapper:
	__slots__ = ("res",)

	def __init__(self, res: typing.Union[TransformerBase, Dynamic]) -> None:
		self.res = res

	def __call__(self, parent: "_ProtoBundle") -> TransformerBase:
		return resolveDynamics(parent, self.res)
