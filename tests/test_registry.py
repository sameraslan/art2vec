import numpy as np
import pytest

from art2vec import MEDIA, Block, LeakNote, Medium, Work, load_medium


def test_every_registered_medium_implements_the_protocol() -> None:
    for name in MEDIA:
        medium = load_medium(name)
        assert isinstance(medium, Medium)
        assert medium.name == name
        assert medium.version


def test_unknown_medium_names_the_known_ones() -> None:
    with pytest.raises(KeyError, match="album"):
        load_medium("sculpture")


def test_work_is_hashable_and_extras_do_not_count() -> None:
    a = Work("1", "t", "c", 1970, "album", {"link": "x"})
    b = Work("1", "t", "c", 1970, "album", {"link": "y"})
    assert a == b and hash(a) == hash(b)


def test_block_normalises_dtypes_and_rejects_misaligned_rows() -> None:
    leak = LeakNote(saw="nothing")
    block = Block("x", "content", "album", [1, 2], np.zeros((2, 4)), "m", "v", leak)
    assert block.ids.dtype.kind == "U" and block.vectors.dtype == np.float32
    with pytest.raises(ValueError):
        Block("x", "content", "album", ["1", "2"], np.zeros((3, 4)), "m", "v", leak)
    with pytest.raises(ValueError):
        Block("x", "content", "album", ["1", "1"], np.zeros((2, 4)), "m", "v", leak)
