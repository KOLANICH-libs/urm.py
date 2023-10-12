urm.py [![Unlicensed work](https://raw.githubusercontent.com/unlicense/unlicense.org/master/static/favicon.png)](https://unlicense.org/)
======
~~[wheel (GitLab)](https://gitlab.com/KOLANICH/urm.py/-/jobs/artifacts/master/raw/dist/urm-0.CI-py3-none-any.whl?job=build)~~
~~[wheel (GHA via `nightly.link`)](https://nightly.link/KOLANICH-libs/urm.py/workflows/CI/master/urm-0.CI-py3-none-any.whl)~~
~~![GitLab Build Status](https://gitlab.com/KOLANICH/urm.py/badges/master/pipeline.svg)~~
~~![GitLab Coverage](https://gitlab.com/KOLANICH/urm.py/badges/master/coverage.svg)~~
~~[![GitHub Actions](https://github.com/KOLANICH-libs/urm.py/workflows/CI/badge.svg)](https://github.com/KOLANICH-libs/urm.py/actions/)~~
[![Libraries.io Status](https://img.shields.io/librariesio/github/KOLANICH-libs/urm.py.svg)](https://libraries.io/github/KOLANICH-libs/urm.py)
[![Code style: antiflash](https://img.shields.io/badge/code%20style-antiflash-FFF.svg)](https://codeberg.org/KOLANICH-tools/antiflash.py)

**We have moved to https://codeberg.org/KOLANICH-libs/urm.py, grab new versions there.**

Under the disguise of "better security" Micro$oft-owned GitHub has [discriminated users of 1FA passwords](https://github.blog/2023-03-09-raising-the-bar-for-software-security-github-2fa-begins-march-13/) while having commercial interest in success and wide adoption of [FIDO 1FA specifications](https://fidoalliance.org/specifications/download/) and [Windows Hello implementation](https://support.microsoft.com/en-us/windows/passkeys-in-windows-301c8944-5ea2-452b-9886-97e4d2ef4422) which [it promotes as a replacement for passwords](https://github.blog/2023-07-12-introducing-passwordless-authentication-on-github-com/). It will result in dire consequencies and is competely inacceptable, [read why](https://codeberg.org/KOLANICH/Fuck-GuanTEEnomo).

If you don't want to participate in harming yourself, it is recommended to follow the lead and migrate somewhere away of GitHub and Micro$oft. Here is [the list of alternatives and rationales to do it](https://github.com/orgs/community/discussions/49869). If they delete the discussion, there are certain well-known places where you can get a copy of it. [Read why you should also leave GitHub](https://codeberg.org/KOLANICH/Fuck-GuanTEEnomo).

---

Unrelational mapper.

Sometimes you need to store some data somewhen and lazily retrieve as class fields and we don't want to write lot of boilerplate code and maintain this piece of shit. Object-relational mappers solve this problem by mapping classes to database tables, objects - to rows, object hierarchy to public and foreign keys.

But sometimes we don't need to store the data in relational databases. We need to store data in entities like files, archives, remote servers using REST/GraphQL API, etc. So we generalize a bit.

This stuff utilizes my other library `transformerz` of composable 2-way transformations.

Tutorial
--------

It is [strongly](/issue/1) recommended to read the tutorial before using the lib. [`tutorial.ipynb`](./tutorial.ipynb)[![NBViewer](https://nbviewer.org/static/ico/ipynb_icon_16x16.png)](https://nbviewer.org/urls/codeberg.org/KOLANICH-libs/urm.py/raw/branch/master/tutorial.ipynb)

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
