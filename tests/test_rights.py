import pytest

from athanor.rights import RightsJoiner


def test_rights_joiner_rejects_missing_reception():
    joiner = RightsJoiner()
    with pytest.raises(ValueError, match="reception"):
        joiner.join({"row_id": "a1", "rights": "PD"}, reception=None)
