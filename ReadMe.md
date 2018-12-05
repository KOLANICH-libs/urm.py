urm.py [![Unlicensed work](https://raw.githubusercontent.com/unlicense/unlicense.org/master/static/favicon.png)](https://unlicense.org/)
======
~~[wheel (GitLab)](https://gitlab.com/KOLANICH/urm.py/-/jobs/artifacts/master/raw/dist/urm-0.CI-py3-none-any.whl?job=build)~~
[wheel (GHA via `nightly.link`)](https://nightly.link/KOLANICH-libs/urm.py/workflows/CI/master/urm-0.CI-py3-none-any.whl)
~~![GitLab Build Status](https://gitlab.com/KOLANICH/urm.py/badges/master/pipeline.svg)
![GitLab Coverage](https://gitlab.com/KOLANICH/urm.py/badges/master/coverage.svg)~~
[![Coveralls Coverage](https://img.shields.io/coveralls/KOLANICH/urm.py.svg)](https://coveralls.io/r/KOLANICH/urm.py)
[![GitHub Actions](https://github.com/KOLANICH-libs/urm.py/workflows/CI/badge.svg)](https://github.com/KOLANICH-libs/urm.py/actions/)
[![Libraries.io Status](https://img.shields.io/librariesio/github/KOLANICH-libs/urm.py.svg)](https://libraries.io/github/KOLANICH-libs/urm.py)

Unrelational mapper.

Sometimes you need to store some data somewhen and lazily retrieve as class fields and we don't want to write lot of boilerplate code and maintain this piece of shit. Object-relational mappers solve this problem by mapping classes to database tables, objects - to rows, object hierarchy to public and foreign keys.

But sometimes we don't need to store the data in relational databases. We need to store data in entities like files, archives, remote servers using REST/GraphQL API, etc. So we generalize a bit.

This stuff utilizes my other library `transformerz` of composable 2-way transformations.

Tutorial
--------

It is [strongly](/issue/1) recommended to read the tutorial before using the lib. [`tutorial.ipynb`](./tutorial.ipynb) ([NBViewer](https://nbviewer.jupyter.org/github/KOLANICH-libs/urm.py/blob/master/tutorial.ipynb))

TL;DR. Data model
-----------------

We tie stored entities not to objects, but properties in classes. Entities are stored in underlying key-value storage.

* When we first time access a property in the class, it is loaded into a cache and then returned.
* subsequent accesses return the stuff from the cache.
* we can `save` the stuff from the cache to the storage explicitly.
* to create a storage from scratch, we put the data into a cache and then `save` it.

Then we heavily abstrage the stuff.

A `key` is a `tuple` of strings and numbers. It is an unique identifier of a piece of data. It is decoupled from the actual storage implementation. We address data by keys.

To define the way we are going to store data we need to answer to the following "orthogonal" questions:

* WHERE are we going to store it? `Saver` object is an answer. `Mapper.saver` answers the question.
* WHAT is the mapping between our internal `key`s and `key`s in the storage of this piece of data? A `key` is an answer. `Mapper.key` answers this question.

For cold storage we need to answer an additional question:

* HOW are we going to serialize the data? `transformerz.Transformer` object is an answer. `ColdMapper.serializer` answers this question.

So `Mapper` object answers the questions related to storage of values.

To create a bidirectional mapping between class properties, we need to answer the following questions:

* What pattern of access to the data should be optimized for? `FieldStrategy` subclasses are the answers.
    * `ColdStrategy` optimizes for frequent rather cheap accesses to volatile data.
        * Requires to know how we STORE the data. `ColdMapper` object is an answer. `FieldStrategy.cold` answers this question.
    * `CachedStrategy` optimizes for frequent rather expensive accesses to not very volatile data.
        * *Additionally* requires to know how we CACHE the data? `HotMapper` object is an answer. `FieldStrategy.hot` answers this question.
    * How do we create our internal `key`s? `Field` subclasses contain the answers.
