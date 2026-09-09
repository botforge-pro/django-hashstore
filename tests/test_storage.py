import hashlib
from pathlib import Path

import pytest
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage

from django_hashstore import HashStorage

CONTENT = b'the same bytes every time'


@pytest.fixture
def storage(tmp_path: Path) -> HashStorage:
    return HashStorage(location=str(tmp_path))


def test_the_name_is_the_digest_of_the_content(storage: HashStorage, tmp_path: Path) -> None:
    name = storage.save('spots/1/voices/anything.ogg', ContentFile(CONTENT))

    assert name == f'spots/1/voices/{hashlib.md5(CONTENT).hexdigest()}.ogg'
    assert (tmp_path / name).read_bytes() == CONTENT


def test_the_same_content_is_stored_once(storage: HashStorage, tmp_path: Path) -> None:
    first = storage.save('a.ogg', ContentFile(CONTENT))
    second = storage.save('a.ogg', ContentFile(CONTENT))

    assert first == second
    assert [path.name for path in tmp_path.iterdir()] == [Path(first).name]


def test_the_same_content_under_another_upload_name_keeps_its_directory(
    storage: HashStorage,
) -> None:
    here = storage.save('here/a.ogg', ContentFile(CONTENT))
    there = storage.save('there/b.ogg', ContentFile(CONTENT))

    assert Path(here).parent.name == 'here'
    assert Path(there).parent.name == 'there'
    assert Path(here).name == Path(there).name


def test_different_content_gets_different_names(storage: HashStorage) -> None:
    first = storage.save('a.ogg', ContentFile(b'one'))
    second = storage.save('a.ogg', ContentFile(b'two'))

    assert first != second


def test_django_would_have_kept_both_copies(tmp_path: Path) -> None:
    # The behaviour this storage exists to replace, pinned so the difference
    # is visible rather than asserted from memory.
    plain = FileSystemStorage(location=str(tmp_path))

    plain.save('a.ogg', ContentFile(CONTENT))
    plain.save('a.ogg', ContentFile(CONTENT))

    assert len(list(tmp_path.iterdir())) == 2


def test_the_digest_can_be_chosen(tmp_path: Path) -> None:
    storage = HashStorage(location=str(tmp_path), digest='sha256')

    name = storage.save('a.ogg', ContentFile(CONTENT))

    assert name == f'{hashlib.sha256(CONTENT).hexdigest()}.ogg'


def test_a_file_without_an_extension_keeps_none(storage: HashStorage) -> None:
    assert storage.save('a', ContentFile(CONTENT)) == hashlib.md5(CONTENT).hexdigest()


def test_the_content_is_readable_after_the_digest_is_taken(storage: HashStorage) -> None:
    # The digest walks the file to its end; a save that forgot to rewind
    # would write an empty file and still return a plausible name.
    name = storage.save('a.ogg', ContentFile(CONTENT))

    assert storage.open(name).read() == CONTENT
