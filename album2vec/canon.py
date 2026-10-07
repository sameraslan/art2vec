"""RateYourMusic chart sheet export to Works. Append-only order; ratings never leave this module.

Not yet extracted. Source: recmyrecord `data-pipeline/rmr_catalog/` (sources, pairing, build).
"""

from __future__ import annotations

from art2vec.work import Work


def works() -> list[Work]:
    raise NotImplementedError("not yet extracted from recmyrecord rmr_catalog")
