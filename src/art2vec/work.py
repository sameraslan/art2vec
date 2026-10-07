"""A work of art, as the core knows it: identity and plain metadata, nothing about reception."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Work:
    """One work in a medium's canon.

    `id` is the medium's stable key as a string (for albums, the RateYourMusic
    id). `extras` holds medium-specific strings a later step needs (store
    links, a release id); it is left out of equality and hashing. Ratings,
    vote counts and chart positions never appear here: the canon may read
    them, but it does not pass them on (FRAMEWORK.md, Rule 1).
    """

    id: str
    title: str
    creator: str
    year: int | None
    medium: str
    extras: dict[str, str] = field(default_factory=dict, compare=False, hash=False)
