import hashlib
from pathlib import PurePosixPath

from django.core.files.base import File
from django.core.files.storage import FileSystemStorage


class HashStorage(FileSystemStorage):
    """A file storage that names a file after the digest of its content.

    Django's default storage answers a name collision by inventing a new
    name: save the same bytes ten times and ten files sit on disk under
    `photo.jpg`, `photo_x7Kd91a.jpg` and so on. The suffix is random, so it
    also travels into anything that records the stored name, and two runs of
    the same code never agree on it.

    Here the name is the content. The directory the upload path produced is
    kept, the file name becomes the digest, and identical bytes therefore
    resolve to one file that is written once. A second save of the same
    content returns the existing name without touching the disk.

    The digest is chosen for speed, not for resisting an adversary: it
    answers "have I already stored these bytes", never "is this file
    trustworthy". Pass `digest=` for another algorithm from `hashlib`.
    """

    def __init__(self, *args, digest: str = 'md5', **kwargs) -> None:
        self.digest = digest
        # Overwriting is safe here and only here: the name is derived from the
        # content, so a concurrent writer is writing the same bytes. It also
        # removes the retry loop the parent runs on FileExistsError, which
        # would never end for a storage whose `get_available_name` answers
        # with the same name every time.
        kwargs['allow_overwrite'] = True
        super().__init__(*args, **kwargs)

    def get_available_name(self, name: str, max_length: int | None = None) -> str:
        """Never invent an alternative name: an occupied name holds the very
        content being saved, so the right answer is to use it."""
        return name

    def hashed_name(self, name: str, content: File) -> str:
        path = PurePosixPath(name)
        return str(path.with_name(f'{self.content_digest(content)}{path.suffix}'))

    def content_digest(self, content: File) -> str:
        digest = hashlib.new(self.digest)
        for chunk in content.chunks():
            digest.update(chunk)
        content.seek(0)
        return digest.hexdigest()

    def _save(self, name: str, content: File) -> str:
        name = self.hashed_name(name, content)
        if self.exists(name):
            return name
        return super()._save(name, content)
