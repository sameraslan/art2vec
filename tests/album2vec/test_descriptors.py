"""The descriptor table is complete, consistent and sorted into the four kinds."""

from art2vec.album2vec import felt


def test_table_has_every_rym_descriptor_once() -> None:
    table = felt.table()
    assert len(table) == 176
    assert set(table.values()) == {felt.FELT, felt.TEXTURE, felt.SUBJECT, felt.POSITION}


def test_style_and_standing_words_are_out() -> None:
    table = felt.table()
    for word in ("progressive", "psychedelic", "technical", "sophisticated", "epic"):
        assert table.get(word, felt.POSITION) == felt.POSITION, word


def test_felt_words_look_like_feelings() -> None:
    words = felt.felt_words()
    for word in ("melancholic", "anxious", "playful", "nocturnal", "warm"):
        assert word in words
    for word in ("lo-fi", "acoustic", "male vocals", "death", "love"):
        assert word not in words
