"""
test_multifile_time_checks.py
=============================

Tests for the checks in the `multifile_time_checks.py` module.
"""

import os

from netCDF4 import Dataset

from time_checks.multifile_time_checks import *
from time_checks.test.mock_netcdf import MockNCDataset

from time_checks import settings

# INCLUDE MockNCDataset in supported settings
settings.supported_datasets.append(MockNCDataset)

CMIP5_DATA_DIR = "test_data/cmip5"


def _call_common_multifile_check(file_list):
    """
    Creates a set of Dataset objects from file list, calls multifile
    check and returns result.

    :param file_list: A list of file names
    :return: Result from multifile check [boolean]
    """
    paths = [os.path.join(CMIP5_DATA_DIR, fname) for fname in file_list]
    datasets = []

    for fpath in paths:
        print fpath
        datasets.append(Dataset(fpath))
    
    result = check_multifile_temporal_continuity(datasets, time_index_in_name=-1)[0]
    return result


def test_check_multifile_temporal_continuity_monthly_success_1():
    file_names = ['tas_Amon_HadGEM2-ES_historical_r1i1p1_185912-188411.nc',
                  'tas_Amon_HadGEM2-ES_historical_r1i1p1_188412-190911.nc',
                  'tas_Amon_HadGEM2-ES_historical_r1i1p1_190912-193411.nc',
                  'tas_Amon_HadGEM2-ES_historical_r1i1p1_193412-195911.nc',
                  'tas_Amon_HadGEM2-ES_historical_r1i1p1_195912-198411.nc',
                  'tas_Amon_HadGEM2-ES_historical_r1i1p1_198412-200511.nc']

    result = _call_common_multifile_check(file_names)
    assert(result is True)


def test_check_multifile_temporal_continuity_monthly_fail_1():
    file_names = ['tas_Amon_HadGEM2-ES_historical_r1i1p1_185912-188411.nc',
                  # Missing files here
                  'tas_Amon_HadGEM2-ES_historical_r1i1p1_198412-200511.nc']

    result = _call_common_multifile_check(file_names)
    assert(result is False)


def test_check_multifile_temporal_continuity_day_success_1():
    file_names = ['ua_day_IPSL-CM5A-LR_historical_r1i1p1_19500101-19591231.nc',
                  'ua_day_IPSL-CM5A-LR_historical_r1i1p1_19600101-19691231.nc',
                  'ua_day_IPSL-CM5A-LR_historical_r1i1p1_19700101-19791231.nc',
                  'ua_day_IPSL-CM5A-LR_historical_r1i1p1_19800101-19891231.nc',
                  'ua_day_IPSL-CM5A-LR_historical_r1i1p1_19900101-19991231.nc',
                  'ua_day_IPSL-CM5A-LR_historical_r1i1p1_20000101-20051231.nc']

    result = _call_common_multifile_check(file_names)
    assert(result is True)


def test_check_multifile_temporal_continuity_day_fail_1():
    file_names = ['ua_day_IPSL-CM5A-LR_historical_r1i1p1_19500101-19591231.nc',
                  # Missing file here
                  'ua_day_IPSL-CM5A-LR_historical_r1i1p1_19700101-19791231.nc']

    result = _call_common_multifile_check(file_names)
    assert(result is False)


def test_check_multifile_temporal_continuity_yearly_success_1():
    file_names = ['o2_Oyr_HadGEM2-CC_piControl_r1i1p1_1860-1959.nc',
                  'o2_Oyr_HadGEM2-CC_piControl_r1i1p1_1960-2059.nc',
                  'o2_Oyr_HadGEM2-CC_piControl_r1i1p1_2060-2099.nc']

    result = _call_common_multifile_check(file_names)
    assert(result is True)


def test_check_multifile_temporal_continuity_yearly_fail_1():
    file_names = ['o2_Oyr_HadGEM2-CC_piControl_r1i1p1_1860-1959.nc',
                  # Missing file here
                  'o2_Oyr_HadGEM2-CC_piControl_r1i1p1_2060-2099.nc'
                  ]

    result = _call_common_multifile_check(file_names)
    assert(result is False)


def test_check_multifile_temporal_continuity_6hr_success_1():
    file_names = ['psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2079120106-2080120100.nc',
                  'psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2080120106-2081120100.nc',
                  'psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2081120106-2082120100.nc',
                  'psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2082120106-2083120100.nc',
                  'psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2083120106-2084120100.nc',
                  'psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2084120106-2085120100.nc',
                  'psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2085120106-2086120100.nc',
                  'psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2086120106-2087120100.nc',
                  'psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2087120106-2088120100.nc',
                  'psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2088120106-2089120100.nc',
                  'psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2089120106-2090120100.nc',
                  'psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2090120106-2091120100.nc',
                  'psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2091120106-2092120100.nc',
                  'psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2092120106-2093120100.nc',
                  'psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2093120106-2094120100.nc',
                  'psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2094120106-2095120100.nc',
                  'psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2095120106-2096120100.nc',
                  'psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2096120106-2097120100.nc',
                  'psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2097120106-2098120100.nc',
                  'psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2098120106-2099120100.nc',
                  'psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2099120106-2100010100.nc']

    result = _call_common_multifile_check(file_names)
    assert(result is True)


def test_check_multifile_temporal_continuity_6hr_fail_1():
    file_names = ['psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2079120106-2080120100.nc',
                  'psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2080120106-2081120100.nc',
                  # Missing files here
                  'psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2098120106-2099120100.nc',
                  'psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_2099120106-2100010100.nc']

    result = _call_common_multifile_check(file_names)
    assert(result is False)


def test_check_multifile_temporal_continuity_TypeError_success_1():
    file_names = ['tas_day_CMCC-CM_piControl_r1i1p1_15810101-15811231.nc',
                  'tas_day_CMCC-CM_piControl_r1i1p1_15820101-15821231.nc',
                  'tas_day_CMCC-CM_piControl_r1i1p1_15830101-15831231.nc',
                  ]

    result = _call_common_multifile_check(file_names)
    assert(result is True)


def test_check_multifile_temporal_continuity_ValueError_success_1():
    file_names = ['tas_Amon_ACCESS1-3_piControl_r1i1p1_025001-049912.nc',
                  'tas_Amon_ACCESS1-3_piControl_r1i1p1_050001-074912.nc',
                  ]

    result = _call_common_multifile_check(file_names)
    assert (result is True)


def test_check_multifile_temporal_continuity_julian_success():
    file_names = ['tas_Amon_GFDL-CM2p1_historical_r1i1p1_200101-200512.nc',
                  'tas_Amon_GFDL-CM2p1_historical_r1i1p1_200601-201012.nc',
                  'tas_Amon_GFDL-CM2p1_historical_r1i1p1_201101-201512.nc',
                  'tas_Amon_GFDL-CM2p1_historical_r1i1p1_201601-202012.nc',
                  'tas_Amon_GFDL-CM2p1_historical_r1i1p1_202101-202512.nc',
                  'tas_Amon_GFDL-CM2p1_historical_r1i1p1_202601-203012.nc',
                  'tas_Amon_GFDL-CM2p1_historical_r1i1p1_203101-203512.nc',
                  'tas_Amon_GFDL-CM2p1_historical_r1i1p1_203601-204012.nc']

    result = _call_common_multifile_check(file_names)
    assert(result is True)

