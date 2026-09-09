# Changelog

All notable changes to this project are documented here, following
[Keep a Changelog](https://keepachangelog.com/).

## [0.1.0] - 2026-09-09

### Added

- `HashStorage`, a `FileSystemStorage` that stores a file under the digest of
  its content: the upload directory is kept, the file name becomes the digest,
  and identical content is written once and returns the existing name.
- `digest=` to pick any algorithm `hashlib` accepts; the default is `md5`.
