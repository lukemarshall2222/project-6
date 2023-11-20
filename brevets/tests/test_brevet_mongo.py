'''
Luke Marshall
test suite for brevet_mongo module'''

from brevet_mongo import get_controls, insert_controls
import nose

def test_insert_controls():
    dist = 0
    open = "2021-01-01T00:00"
    close = "2021-01-01T01:00"
    _id = insert_controls('300', "2021-01-01T00:00", [{"dist":dist,
                                                       "open": open,
                                                       "close": close}])

    assert isinstance(_id, str)

def test_get_controls():
    brevet_dist_check = '300'
    datetime_check = "2021-01-01T00:00"
    dist_check = 0
    open_check = "2021-01-01T00:00"
    close_check = "2021-01-01T01:00"
    result = get_controls()
    assert result[0] == brevet_dist_check
    assert result[1] == datetime_check
    assert result[2][0]["dist"] == dist_check
    assert result[2][0]["open"] == open_check
    assert result[2][0]["close"] == close_check

