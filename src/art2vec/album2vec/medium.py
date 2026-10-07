"""AlbumMedium: canon, fetch, encode (sound; later words) and describe (felt)."""

from __future__ import annotations

from collections.abc import Sequence

from art2vec.medium import Block
from art2vec.work import Work


class AlbumMedium:
    name = "album"
    version = "0.0.1"  # bumps when the encoder, the artefact or descriptors.csv changes

    def canon(self) -> list[Work]:
        from art2vec.album2vec import canon

        return canon.works()

    def fetch(self, works: Sequence[Work]) -> None:
        from art2vec.album2vec import fetch

        fetch.clips(works)

    def encode(self, works: Sequence[Work]) -> list[Block]:
        from art2vec.album2vec import sound

        return [sound.block(works)]  # the words block joins once built

    def describe(self, works: Sequence[Work]) -> Block:
        from art2vec.album2vec import felt

        return felt.block(works)
