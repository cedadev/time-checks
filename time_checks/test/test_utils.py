"""
test_utils.py
=============

Tests for the `utils.py` module.
"""

from time_checks import utils


def test_str_to_anytime_successes():
    for dt in ("1999-01-01", "1999", "199901010000", "1999-01-01T00:00:00.000"):
        resp = utils.str_to_anytime(dt)
        assert(resp._components == (1999, 1, 1, 0, 0, 0, 0))


def test_str_to_anytime_failures():
    for dt in ("01/01/2017", "", 1999):
        try:
            resp = utils.str_to_anytime(dt)
            worked = True
        except:
            worked = False

        if worked:
            raise Exception("DateTimeAnyTime object created from invalid value: {}".format(dt))

