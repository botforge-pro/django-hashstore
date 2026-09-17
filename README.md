[![Tests](https://github.com/botforge-pro/django-hashstore/actions/workflows/tests.yml/badge.svg)](https://github.com/botforge-pro/django-hashstore/actions/workflows/tests.yml)
[![Documentation](https://github.com/botforge-pro/django-hashstore/actions/workflows/documentation.yml/badge.svg)](https://botforge-pro.github.io/django-hashstore/django_hashstore.html)

# django-hashstore

A Django file storage that names a file after the digest of its content.

Django answers a name collision by inventing a new name. Save the same bytes
ten times and ten files sit on disk — `photo.jpg`, `photo_x7Kd91a.jpg`, and so
on. The suffix is random, so it also travels into whatever records the stored
name: a database row, a request body, a recorded HTTP fixture. Two runs of the
same code never agree on it.

This storage makes the name the content. The directory the upload path
produced is kept, the file name becomes the digest, and identical bytes
resolve to one file that is written once.

```python
from django.db import models
from django_hashstore import HashStorage

class Voice(models.Model):
    audio = models.FileField(upload_to='voices/', storage=HashStorage())
```

```python
>>> voice.audio.save('anything.ogg', ContentFile(b'...'))
'voices/9f2a...c1.ogg'
```

Save the same bytes again under any name and the same path comes back, with
no second copy on disk.

## As the default storage

```python
STORAGES = {
    'default': {'BACKEND': 'django_hashstore.HashStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
}
```

## Options

`HashStorage` takes everything `FileSystemStorage` takes, plus `digest`, the
name of any algorithm `hashlib` accepts. The default is `md5`, chosen for
speed: the digest answers "have I already stored these bytes", never "is this
file trustworthy". Where the stored name is published to people who might
craft input for it, pass `digest='sha256'`.

```python
HashStorage(location='/srv/media', digest='sha256')
```

## What to know before using it

**Files are shared.** Two rows holding identical content point at one file, so
deleting either row's file takes it away from the other. Where content is
deleted rather than accumulated, keep the ordinary storage.

**The name is not the upload name.** Anything that recovers a human-readable
title from the stored path stops working. Keep the original name in a column
of its own.

## Install

```
pip install git+https://github.com/botforge-pro/django-hashstore@v0.1.0
```

## Documentation

The [API reference](https://botforge-pro.github.io/django-hashstore/django_hashstore.html) is generated from the public Python API and deployed by GitHub Actions.

## Develop

```
make install
make test
make lint
```

Requires Python 3.10+ and Django 5.1+, which is where `allow_overwrite`
arrived: a content-addressed store has to be allowed to write over a name,
because the name means the bytes are already the ones being written.
