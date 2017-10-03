"""
test_utils.py
=============

Tests for the `utils.py` module.
"""

from time_checks import utils
from datetime import timedelta

def test_get_nc_datetime_calendars_success():
    x = utils.get_nc_datetime(29, "days since 2000-02-01 00:00:00", calendar="360_day")
    assert(x.timetuple()[:6] == (2000, 2, 30, 0, 0, 0))

    x = utils.get_nc_datetime(29, "days since 1999-02-01 00:00:00", calendar="standard")
    assert(x.timetuple()[:6] == (1999, 3, 2, 0, 0, 0))

    x = utils.get_nc_datetime(28, "days since 1999-02-01 00:00:00", calendar="366_day")
    assert(x.timetuple()[:6] == (1999, 2, 29, 0, 0, 0))


def test_str_to_anytime_successes():
    for dt in ("1999-01-01", "1999", "199901010000", "1999-01-01T00:00:00.000"):
        resp = utils.str_to_anytime(dt)
        assert(resp._components == (1999, 1, 1, 0, 0, 0, 0))


def test_str_to_anytime_microsecond():
    dt = "1999-01-01T00:00:00.012"
    resp = utils.str_to_anytime(dt)
    assert(resp._components == (1999, 1, 1, 0, 0, 0, 12))


def test_str_to_anytime_failures():
    for dt in ("01/01/2017", "", 1999):
        try:
            resp = utils.str_to_anytime(dt)
            worked = True
        except:
            worked = False

        if worked:
            raise Exception("DateTimeAnyTime object created from invalid value: {}".format(dt))


def test_add_to_netcdf_datetime_success():
    x = utils.get_nc_datetime(27, "days since 1999-02-01 00:00:00", calendar="360_day")
    # Set time delta, test that sending seconds and microseconds is optional
    deltas = [(2.5,), (2.5, 0), (2.5, 0, 0)]

    for delta in deltas:
        d = timedelta(*delta)
        res = x + d
        assert(str(res) == "1999-02-30 12:00:00")


def test_time_series_daily_360_day_success():
    start = utils.str_to_anytime("1999-01-01T00:00:00")
    end = utils.str_to_anytime("1999-02-30T00:00:00")
    ts = utils.TimeSeries(start, end, (1, "day"), calendar="360_day")
    s = ts.series
    assert(len(s) == 60)
    assert(str(s[0]) == "1999-01-01 00:00:00")
    assert(str(s[-1]) == "1999-02-30 00:00:00")


def test_time_series_daily_standard_success():
    start = utils.str_to_anytime("1999-01-01T00:00:00")
    end = utils.str_to_anytime("1999-03-02T00:00:00")
    ts = utils.TimeSeries(start, end, (1, "day"), calendar="standard")
    s = ts.series
    assert(len(s) == 61)
    assert(str(s[0]) == "1999-01-01 00:00:00")
    assert(str(s[-1]) == "1999-03-02 00:00:00")


def test_time_series_6_hourly_standard_success():
    start = utils.str_to_anytime("1999-01-01T00:00:00")
    end = utils.str_to_anytime("1999-03-02T18:00:00")
    ts = utils.TimeSeries(start, end, (6, "hour"), calendar="standard")
    s = ts.series
    assert(len(s) == 244)
    assert(str(s[0]) == "1999-01-01 00:00:00")
    assert(str(s[-1]) == "1999-03-02 18:00:00")