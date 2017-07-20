"""
test_file_time_checks.py
========================

Tests for the checks in the `file_time_checks.py` module.
"""

from netCDF4 import Dataset

from time_checks.file_time_checks import *
from time_checks.test.mock_netcdf import MockNCDataset



def test_check_file_name_time_format_fail_1():
    eg_names = [
        "mrsos_day_HadGEM2-ES_historical_r1i1p1_19991201-2005.nc",
        "hopeful",
        "20040101011.nc"
    ]

    for fname in eg_names:
        mock_ds = MockNCDataset(fname)
        assert(check_file_name_time_format(mock_ds) == False)


def test_check_file_name_time_format_success_1():
    eg_names = ["mrsos_day_HadGEM2-ES_historical_r1i1p1_19991201-20051130.nc"]

    for fname in eg_names:
        mock_ds = MockNCDataset(fname)
        assert(check_file_name_time_format(mock_ds) == True)


def test_check_file_name_matches_time_var_success_1():
    ds = Dataset('/badc/cmip5/data/cmip5/output1/MOHC/HadGEM2-ES/historical/day/land/day/r1i1p1/latest/mrsos/mrsos_day_HadGEM2-ES_historical_r1i1p1_19991201-20051130.nc')
    assert(check_file_name_matches_time_var(ds, time_index_in_name=-1, tolerance='days:1') == True)


def test_check_file_name_matches_time_var_fail_1():
    ds = Dataset('/badc/cmip5/data/cmip5/output1/MOHC/HadGEM2-ES/historical/day/land/day/r1i1p1/latest/mrsos/mrsos_day_HadGEM2-ES_historical_r1i1p1_19991201-20051130.nc')
    assert(check_file_name_matches_time_var(ds, time_index_in_name=-1, tolerance='hours:1') == False)

