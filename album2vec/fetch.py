"""Download clips into the artefact cache; YouTube full-length audio into windows.

Audio is decoded in memory and never written outside the cache, never committed,
never shipped. Not yet extracted. Source: recmyrecord `data-pipeline/rmr_audio/embed.py`
(download half), `fulllength.py`, `windows.py`.
"""

from __future__ import annotations

from collections.abc import Sequence

from art2vec.work import Work


def clips(works: Sequence[Work]) -> None:
    raise NotImplementedError("not yet extracted from recmyrecord rmr_audio")
