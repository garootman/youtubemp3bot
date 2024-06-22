import pytest

from tgmediabot.assist import drilldown


def test_drilldown():
    assert drilldown({}, "a") == {}
    assert drilldown({}, None) == {}
    assert drilldown({"a": 1}, "a") == 1

    deep_dict = {"a": {"b": {"c": 1}}}
    assert drilldown(deep_dict, ["a", "b", "c"]) == 1
    assert drilldown(deep_dict, ["a", "b", "d"]) == None
    assert drilldown(deep_dict, ["a", "b"]) == {"c": 1}
    assert drilldown(deep_dict, ["a", "b", "c", "d"]) == None
    assert drilldown(deep_dict, ["a", "z"]) == None

    deep_list = [1, [2, [3, 4]]]
    assert drilldown(deep_list, [1, 1]) == [3, 4]
    assert drilldown(deep_list, [1, 1, 1]) == 4
    assert drilldown(deep_list, [1, 1, 2]) == None


if __name__ == "__main__":
    test_drilldown()
