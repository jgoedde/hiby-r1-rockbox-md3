import pytest
from md3.variants import VARIANTS, select


def test_eight_variants():
    assert [v.name for v in VARIANTS] == [
        "MD3-Dark-Orange",
        "MD3-Dark-Blue",
        "MD3-Dark-Green",
        "MD3-Dark-Pink",
        "MD3-Light-Orange",
        "MD3-Light-Blue",
        "MD3-Light-Green",
        "MD3-Light-Pink",
    ]


def test_select_defaults_to_all():
    assert select(None) == VARIANTS
    assert select([]) == VARIANTS


def test_select_accepts_short_and_full_names_in_any_case():
    assert [v.name for v in select(["Light-Blue", "md3-dark-pink"])] == ["MD3-Light-Blue", "MD3-Dark-Pink"]


def test_select_rejects_unknown_names_listing_the_valid_ones():
    with pytest.raises(ValueError, match="MD3-Dark-Orange"):
        select(["Light-Purple"])
