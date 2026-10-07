"""The registry of media. One line per medium, imported on demand."""

from __future__ import annotations

from importlib import import_module

from art2vec.medium import Medium

MEDIA: dict[str, str] = {
    "album": "art2vec.album2vec.medium:AlbumMedium",
}


def load_medium(name: str) -> Medium:
    """Import and instantiate the medium registered under `name`.

    Importing lazily keeps `import art2vec` light: no audio model loads until
    an album medium is asked for. A missing optional extra surfaces as an
    ImportError that names the extra to install.
    """
    try:
        path = MEDIA[name]
    except KeyError:
        known = ", ".join(sorted(MEDIA))
        raise KeyError(f"no medium called {name!r}; known media: {known}") from None
    module_name, _, attr = path.partition(":")
    try:
        module = import_module(module_name)
    except ImportError as exc:
        raise ImportError(
            f"the {name!r} medium needs its optional dependencies: "
            f'pip install "art2vec[{name}]" ({exc})'
        ) from exc
    medium = getattr(module, attr)()
    if not isinstance(medium, Medium):
        raise TypeError(f"{path} does not implement the Medium protocol")
    return medium
