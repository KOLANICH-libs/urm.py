#!/usr/bin/env python3
import typing
import sys
import unittest
from collections import OrderedDict

dict = OrderedDict

from pathlib import Path

try:
	import ujson as json
except ImportError:
	import json

from transformerz.core import TransformerBase
from transformerz.serialization.json import jsonFancySerializer
from transformerz.text import utf8Transformer

sys.path.insert(0, str(Path(__file__).parent.parent))

from urm.core import Dynamic
from urm.fields import CachedStrategy, ColdStrategy, Field, Field0D, FieldND
from urm.mappers import ColdMapper, HotMapper
from urm.mappers.key import PrefixKeyMapper, fieldNameKeyMapper
from urm.mappers.serializer import JustReturnSerializerMapper
from urm.ProtoBundle import ProtoBundle
from urm.storers.cold import FileSaver
from urm.storers.hot import CollectionCacher, PrefixCacher

ourTransformer = utf8Transformer + jsonFancySerializer

savedDataRootDir = Path(Path(__file__).parent / "testSavedDataRootDir")  # a directory where a file will reside
savedDataRootDir.mkdir(parents=True, exist_ok=True)

ourSaver = FileSaver(savedDataRootDir, "json")  # json is the extension of the files used. `ourSaver` will be populated into `saver` property in future


def constantParamsSerializerMapper(parent: ProtoBundle) -> TransformerBase:  # it will be populated into `serializer` property in future
	return ourTransformer


class Tests(unittest.TestCase):
	@staticmethod
	def createAClassWithStrategyFromGroundUp(strategy) -> ProtoBundle:
		class B(ProtoBundle):
			__slots__ = ("_scalarField",)
			scalarField = Field0D(None)
			scalarField.strategy = strategy

		return B

	def getBrandNewOurStorer(self) -> ColdMapper:
		return ColdMapper(fieldNameKeyMapper, ourSaver, constantParamsSerializerMapper)

	def getBrandNewOurCacher(self) -> HotMapper:
		return HotMapper(fieldNameKeyMapper, PrefixCacher())

	def verifyBundleWithJSONFileSaver(self, testClass: typing.Type, isCached: bool) -> None:
		A = testClass
		a = A()

		oldValue = {"a": ["b", "c"]}
		a.scalarField = oldValue
		with self.subTest("Simple round-trip"):
			self.assertEqual(a.scalarField, oldValue)

		if isCached:
			a.save()

		with self.subTest("Initial persistence"):
			fileName = savedDataRootDir / (A.scalarField.strategy.name + ".json")
			self.assertEqual(json.loads(fileName.read_text()), oldValue)

		newValue = 100500
		fileName.write_text(json.dumps(newValue))
		if isCached:
			with self.subTest("Read from cache"):
				self.assertEqual(a.scalarField, oldValue)  # we read from cache!
				a.save()

			with self.subTest("Noninvalidation by lack of write"):
				self.assertEqual(json.loads(fileName.read_text()), newValue)  # because we don't write back from the cache, if it is not invalidated by a write!

			# returning to the state with the old value everywhere ...
			a.scalarField = oldValue
			a.save()

			with self.subTest("Non-write if not requested"):
				a.scalarField = newValue
				self.assertEqual(json.loads(fileName.read_text()), oldValue)  # because not yet written back from the cache!

			with self.subTest("Update"):
				a.save()
				self.assertEqual(json.loads(fileName.read_text()), newValue)  # because only now it is written back from the cache!

		else:
			self.assertEqual(a.scalarField, newValue)  # the new value immediately available as changed in the cold storage

	def test_ColdStrategy_FileSaver_Field0D_FromGroundUp(self) -> None:
		ourStorer = self.getBrandNewOurStorer()
		coldStrategy = ColdStrategy(ourStorer)

		self.verifyBundleWithJSONFileSaver(self.createAClassWithStrategyFromGroundUp(coldStrategy), False)

	def test_CachedStrategy_FileSaver_Field0D_FromGroundUp(self):
		ourStorer = self.getBrandNewOurStorer()
		ourCacher = self.getBrandNewOurCacher()
		cachedStrategy = CachedStrategy(ourStorer, ourCacher)
		self.verifyBundleWithJSONFileSaver(self.createAClassWithStrategyFromGroundUp(cachedStrategy), True)

	def test_ColdStrategy_FileSaver_Field0D(self) -> None:
		ourStorer = self.getBrandNewOurStorer()

		class A:
			scalarField = Field0D(ourStorer)  # uncached

		self.verifyBundleWithJSONFileSaver(A, False)

	def test_CachedStrategy_FileSaver_Field0D(self):
		ourStorer = self.getBrandNewOurStorer()
		ourCacher = self.getBrandNewOurCacher()

		class B(ProtoBundle):
			__slots__ = ("_scalarField",)
			scalarField = Field0D(ourStorer, ourCacher)  # cached

		self.verifyBundleWithJSONFileSaver(B, True)

	def test_CachedStrategy_FileSaver_Field1D(self) -> None:
		vectorKeyMapper = PrefixKeyMapper()
		ourVectorStorer = ColdMapper(vectorKeyMapper, ourSaver, constantParamsSerializerMapper)
		ourVectorCacher = HotMapper(vectorKeyMapper, CollectionCacher(dict))  # our hot storage is a dict, but we can plug there any collection

		class C(ProtoBundle):
			vectorField = FieldND(ourVectorStorer, ourVectorCacher)  # cached

		c = C()
		c.vectorField["aaaa"] = 10
		c.vectorField["bbbb"] = {25: 36}
		c.vectorField["cccc"] = {"25": 36}
		c.save()
		self.assertEqual((savedDataRootDir / "aaaa.json").read_text(), str(c.vectorField["aaaa"]))
		self.assertNotEqual(json.loads((savedDataRootDir / "bbbb.json").read_text()), c.vectorField["bbbb"])  # because it is JSON!
		self.assertEqual(json.loads((savedDataRootDir / "cccc.json").read_text()), c.vectorField["cccc"])

	def test_ColdStrategy_FileSaver_Field0D_Dynamic(self) -> None:
		controlledPathKeyMapper = PrefixKeyMapper(Dynamic("name"))
		ourNameControlledStorer = ColdMapper(controlledPathKeyMapper, ourSaver, constantParamsSerializerMapper)
		ourCacher = self.getBrandNewOurCacher()

		class Pocket(ProtoBundle):
			__slots__ = ("name", "_shit")
			shit = Field0D(ourNameControlledStorer, ourCacher)

			def __init__(self, name: str):
				self.name = name

		ptchkPocket = Pocket("ptchk")
		ptchkPocket.shit = 2
		ptchkPocket.save()
		(savedDataRootDir / "ptchk.json").write_text(str(json.loads((savedDataRootDir / "ptchk.json").read_text()) - 1))
		ptchkPocket.shit = None  # invalidates cache
		self.assertEqual(ptchkPocket.shit, 1)
		ptchkPocket.shit -= 1
		self.assertEqual(json.loads((savedDataRootDir / "ptchk.json").read_text()), 1)
		ptchkPocket.save()
		self.assertEqual(json.loads((savedDataRootDir / "ptchk.json").read_text()), 0)


if __name__ == "__main__":
	unittest.main()
