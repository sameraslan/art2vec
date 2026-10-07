"""The sound block: Discogs-EffNet per clip, mean per album; centring and PCA live in the transform.

Leak note: Discogs-EffNet was trained to predict Discogs genres and styles
(album2vec/FRAMEWORK.md section 3). Not yet extracted. Source: recmyrecord
`data-pipeline/rmr_audio/embed.py` (model half) and `rmr_pipeline/audio.py` (transform).
"""

from __future__ import annotations

from collections.abc import Sequence

from art2vec.medium import Block, LeakNote
from art2vec.work import Work

LEAK = LeakNote(saw="Discogs genre and style labels (Discogs-EffNet training targets)")


def block(works: Sequence[Work]) -> Block:
    raise NotImplementedError("not yet extracted from recmyrecord")
