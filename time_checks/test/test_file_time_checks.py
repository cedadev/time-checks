"""
test_file_time_checks.py
========================

Tests for the checks in the `file_time_checks.py` module.
"""

from netCDF4 import Dataset

from time_checks.file_time_checks import *
from time_checks.test.mock_netcdf import MockNCDataset
from time_checks import settings

# INCLUDE MockNCDataset in supported settings
settings.supported_datasets.append(MockNCDataset)

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


def test_check_time_format_matches_frequency_success_1():

    eg_names = ['mrsos_day_HadGEM2-ES_historical_r1i1p1_19991201-20051130.nc',
                'mrsos_Oyr_HadGEM2-ES_historical_r1i1p1_1999-2005.nc',
                'mrsos_Amon_HadGEM2-ES_historical_r1i1p1_199912-200511.nc',
                'mrsos_3hr_HadGEM2-ES_historical_r1i1p1_199912010101-200511300101.nc',
                'mrsos_6hrLev_HadGEM2-ES_historical_r1i1p1_1999120101-2005113001.nc',
                ]

    for fname in eg_names:
        mock_ds = MockNCDataset(fname)
        assert(check_time_format_matches_frequency(mock_ds, frequency_index=1, time_index_in_name=-1) == True)


def test_check_time_format_matches_frequency_fail_1():
    
    eg_names = ['mrsos_Oyr_HadGEM2-ES_historical_r1i1p1_19991201-20051130.nc',
                'mrsos_3hr_HadGEM2-ES_historical_r1i1p1_1999-2005.nc',
                'mrsos_6hrLev_HadGEM2-ES_historical_r1i1p1_199912-200511.nc',
                'mrsos_day_HadGEM2-ES_historical_r1i1p1_1999120101-2005113001.nc',
                'mrsos_Amon_HadGEM2-ES_historical_r1i1p1_199912010101-200511300101.nc',
                ]

    for fname in eg_names:
        mock_ds = MockNCDataset(fname)
        assert(check_time_format_matches_frequency(mock_ds, frequency_index=1, time_index_in_name=-1) == False)


def test_check_regular_time_axis_increments_success_1():
    ds = Dataset('/badc/cmip5/data/cmip5/output1/MOHC/HadGEM2-ES/historical/day/land/day/r1i1p1/latest/mrsos/mrsos_day_HadGEM2-ES_historical_r1i1p1_19991201-20051130.nc')
    assert(check_regular_time_axis_increments(ds, frequency_index=1) == True)


def test_check_regular_time_axis_increments_fail_1():
    pass


def test_check_valid_temporal_element_success_1():
    eg_names = ['mrsos_day_HadGEM2-ES_historical_r1i1p1_19991201-20051130.nc',
                'mrsos_Oyr_HadGEM2-ES_historical_r1i1p1_1999-2005.nc',
                'mrsos_Amon_HadGEM2-ES_historical_r1i1p1_199912-200511.nc',
                'mrsos_3hr_HadGEM2-ES_historical_r1i1p1_199912010101-200511300101.nc',
                'mrsos_6hrLev_HadGEM2-ES_historical_r1i1p1_1999120101-2005113001.nc',
                ]

    for fname in eg_names:
        mock_ds = MockNCDataset(fname)
        assert(check_valid_temporal_element(mock_ds, time_index_in_name=-1) == True)



def test_check_valid_temporal_element_fail_1():
    eg_names = ['mrsos_day_HadGEM2-ES_historical_r1i1p1_19991201-20051132.nc',
                'mrsos_Oyr_HadGEM2-ES_historical_r1i1p1_1999-4005.nc',
                'mrsos_Amon_HadGEM2-ES_historical_r1i1p1_199900-200513.nc',
                'mrsos_3hr_HadGEM2-ES_historical_r1i1p1_199912010100-200511300160.nc',
                'mrsos_6hrLev_HadGEM2-ES_historical_r1i1p1_1999120100-2005113024.nc',
                ]

    for fname in eg_names:
        mock_ds = MockNCDataset(fname)
        assert(check_valid_temporal_element(mock_ds, time_index_in_name=-1) == False)


def test_check_multifile_temporal_continutity_success_1():
    eg_names = ['tas_Amon_HadGEM2-ES_historical_r1i1p1_185912-188411.nc',
                'tas_Amon_HadGEM2-ES_historical_r1i1p1_188412-190911.nc',
                'tas_Amon_HadGEM2-ES_historical_r1i1p1_190912-193411.nc',
                'tas_Amon_HadGEM2-ES_historical_r1i1p1_193412-195911.nc',
                'tas_Amon_HadGEM2-ES_historical_r1i1p1_195912-198411.nc',
                'tas_Amon_HadGEM2-ES_historical_r1i1p1_198412-200511.nc']

    mock_dss = []
    for fname in eg_names:
        mock_dss.append(MockNCDataset(fname))

    assert(check_multifile_temporal_continutity(mock_dss, time_index_in_name=-1) == True)

def test_check_multifile_temporal_continutity_fail_1():
    eg_names = ['tas_Amon_HadGEM2-ES_historical_r1i1p1_185912-188411.nc',
                'tas_Amon_HadGEM2-ES_historical_r1i1p1_188412-190911.nc',
                'tas_Amon_HadGEM2-ES_historical_r1i1p1_190912-193411.nc',
                'tas_Amon_HadGEM2-ES_historical_r1i1p1_193412-195911.nc',
                'tas_Amon_HadGEM2-ES_historical_r1i1p1_195912-198411.nc',
                'tas_Amon_HadGEM2-ES_historical_r1i1p1_198512-200511.nc']

    mock_dss = []
    for fname in eg_names:
        mock_dss.append(MockNCDataset(fname))

    assert(check_multifile_temporal_continutity(mock_dss, time_index_in_name=-1) == False)
#
#
# def test_check_multifile_temporal_completeness_success_1():
#     pass
#
#
# def test_check_multifile_temporal_completeness_fail_1():
#     pass


