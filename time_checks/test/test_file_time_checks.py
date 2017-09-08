"""
test_file_time_checks.py
========================

Tests for the checks in the `file_time_checks.py` module.
"""

from netCDF4 import Dataset

from time_checks.file_time_checks import *
from time_checks.multiFile_time_checks import *
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
    eg_names = ["mrsos_yr_HadGEM2-ES_historical_r1i1p1_1999-2005.nc",
                "mrsos_mon_HadGEM2-ES_historical_r1i1p1_199912-200511.nc",
                "mrsos_day_HadGEM2-ES_historical_r1i1p1_19991201-20051130.nc",
                "mrsos_3hr_HadGEM2-ES_historical_r1i1p1_199912010101-200511302359.nc",
                "mrsos_6hr_HadGEM2-ES_historical_r1i1p1_199912010304-200511300501.nc"]

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

    eg_names = ['mrsos_Oyr_HadGEM2-ES_historical_r1i1p1_1999-2005.nc',
                'mrsos_Amon_HadGEM2-ES_historical_r1i1p1_199912-200511.nc',
                'mrsos_day_HadGEM2-ES_historical_r1i1p1_19991201-20051130.nc',
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
    eg_names = ['mrsos_Oyr_HadGEM2-ES_historical_r1i1p1_1999-2005.nc',
                'mrsos_Amon_HadGEM2-ES_historical_r1i1p1_199912-200511.nc',
                'mrsos_day_HadGEM2-ES_historical_r1i1p1_19991201-20051130.nc',
                'mrsos_3hr_HadGEM2-ES_historical_r1i1p1_199912010101-200511300101.nc',
                'mrsos_6hrLev_HadGEM2-ES_historical_r1i1p1_1999120101-2005113001.nc',
                ]

    for fname in eg_names:
        mock_ds = MockNCDataset(fname)
        assert(check_valid_temporal_element(mock_ds, time_index_in_name=-1) == True)



def test_check_valid_temporal_element_fail_1():
    eg_names = ['mrsos_Oyr_HadGEM2-ES_historical_r1i1p1_1999-4005.nc',
                'mrsos_Amon_HadGEM2-ES_historical_r1i1p1_199900-200513.nc',
                'mrsos_day_HadGEM2-ES_historical_r1i1p1_19991201-20051132.nc',
                'mrsos_3hr_HadGEM2-ES_historical_r1i1p1_199912010100-200511300160.nc',
                'mrsos_6hrLev_HadGEM2-ES_historical_r1i1p1_1999120100-2005113024.nc',
                ]

    for fname in eg_names:
        mock_ds = MockNCDataset(fname)
        assert(check_valid_temporal_element(mock_ds, time_index_in_name=-1) == False)


def test_check_multifile_temporal_continutity_success_1():

    yearly_names = ['tas_Oyr_HadGEM2-ES_historical_r1i1p1_1984-2005.nc',
                    'tas_Oyr_HadGEM2-ES_historical_r1i1p1_1859-1884.nc',
                    'tas_Oyr_HadGEM2-ES_historical_r1i1p1_1940-1983.nc',
                    'tas_Oyr_HadGEM2-ES_historical_r1i1p1_1885-1939.nc']

    monthly_names = ['tas_Amon_HadGEM2-ES_historical_r1i1p1_198501-200511.nc',
                     'tas_Amon_HadGEM2-ES_historical_r1i1p1_185912-188411.nc',
                     'tas_Amon_HadGEM2-ES_historical_r1i1p1_190912-193406.nc',
                     'tas_Amon_HadGEM2-ES_historical_r1i1p1_193407-195909.nc',
                     'tas_Amon_HadGEM2-ES_historical_r1i1p1_188412-190911.nc',
                     'tas_Amon_HadGEM2-ES_historical_r1i1p1_195910-198412.nc']

    ####
    #    NEEDS CALENDAR SUPPORT
    #    360 day
    #    no leap
    #
    ####
    daily_names = [
                   'tas_day_HadGEM2-ES_historical_r1i1p1_18840101-19091212.nc',
                   'tas_day_HadGEM2-ES_historical_r1i1p1_19091213-19341130.nc',
                   'tas_day_HadGEM2-ES_historical_r1i1p1_19341201-19591231.nc',
                   'tas_day_HadGEM2-ES_historical_r1i1p1_19600101-19841130.nc',
                   'tas_day_HadGEM2-ES_historical_r1i1p1_19841201-20051130.nc',
                   ]

    ####
    #    NEEDS DAYS PER MONTH CALENDAR SUPPORT
    #    360 day
    #    no leap
    #
    ####
    three_hourly_names = [
                         'tas_3hr_HadGEM2-ES_historical_r1i1p1_190001010000-190001010300.nc',
                         'tas_3hr_HadGEM2-ES_historical_r1i1p1_190001010600-190001012359.nc',
                         'tas_3hr_HadGEM2-ES_historical_r1i1p1_190001020259-190001022359.nc',
                         ]

    six_hourly_names = [
        'tas_6hr_HadGEM2-ES_historical_r1i1p1_190001010000-190001010600.nc',
        'tas_6hr_HadGEM2-ES_historical_r1i1p1_190001011200-190001012359.nc',
        'tas_6hr_HadGEM2-ES_historical_r1i1p1_190001020559-190001030000.nc',
        'tas_6hr_HadGEM2-ES_historical_r1i1p1_190001030600-190001050000.nc',
    ]


    for fnames in [yearly_names, monthly_names, daily_names, three_hourly_names, six_hourly_names]:
        mock_dss = []
        for fname in fnames:
            mock_dss.append(MockNCDataset(fname))

        assert(check_multifile_temporal_continutity(mock_dss, time_index_in_name=-1) == True)

def test_check_multifile_temporal_continutity_fail_1():

    """
    Look for gaps
    :return:
    """

    yearly_names = ['tas_Oyr_HadGEM2-ES_historical_r1i1p1_1984-2005.nc',
                    'tas_Oyr_HadGEM2-ES_historical_r1i1p1_1859-1884.nc',
                    'tas_Oyr_HadGEM2-ES_historical_r1i1p1_1941-1983.nc',
                    'tas_Oyr_HadGEM2-ES_historical_r1i1p1_1885-1939.nc']

    monthly_names = ['tas_Amon_HadGEM2-ES_historical_r1i1p1_188412-190911.nc',
                     'tas_Amon_HadGEM2-ES_historical_r1i1p1_185912-188411.nc',
                     'tas_Amon_HadGEM2-ES_historical_r1i1p1_190912-193411.nc',
                     'tas_Amon_HadGEM2-ES_historical_r1i1p1_195912-198411.nc',
                     'tas_Amon_HadGEM2-ES_historical_r1i1p1_193412-195911.nc',
                     'tas_Amon_HadGEM2-ES_historical_r1i1p1_198512-200511.nc']

    ####
    #    NEEDS CALENDAR SUPPORT
    #    360 day
    #    no leap
    #
    ####
    daily_names = [
                   'tas_day_HadGEM2-ES_historical_r1i1p1_18840101-19091212.nc',
                   'tas_day_HadGEM2-ES_historical_r1i1p1_19091214-19341130.nc',
                   'tas_day_HadGEM2-ES_historical_r1i1p1_19341201-19591231.nc',
                   'tas_day_HadGEM2-ES_historical_r1i1p1_19600101-19841130.nc',
                   'tas_day_HadGEM2-ES_historical_r1i1p1_19841201-20051130.nc',
                   ]

    ####
    #    NEEDS DAYS PER MONTH CALENDAR SUPPORT
    #    360 day
    #    no leap
    #
    ####
    three_hourly_names = [
                         'tas_3hr_HadGEM2-ES_historical_r1i1p1_190001010000-190001010300.nc',
                         'tas_3hr_HadGEM2-ES_historical_r1i1p1_190001010700-190001012359.nc',
                         'tas_3hr_HadGEM2-ES_historical_r1i1p1_190001020259-190001022359.nc',
                         ]

    six_hourly_names = [
        'tas_6hr_HadGEM2-ES_historical_r1i1p1_190001010000-190001010600.nc',
        'tas_6hr_HadGEM2-ES_historical_r1i1p1_190001011300-190001012359.nc',
        'tas_6hr_HadGEM2-ES_historical_r1i1p1_190001020559-190001022359.nc',
    ]

    for fnames in [yearly_names, monthly_names, daily_names, three_hourly_names, six_hourly_names]:
        mock_dss = []
        for fname in fnames:
            mock_dss.append(MockNCDataset(fname))

        assert(check_multifile_temporal_continutity(mock_dss, time_index_in_name=-1) == False)

def test_check_multifile_temporal_continutity_fail_2():
    """
    Look for overlaps
    :return:
    """

    yearly_names = ['tas_Oyr_HadGEM2-ES_historical_r1i1p1_1984-2005.nc',
                    'tas_Oyr_HadGEM2-ES_historical_r1i1p1_1859-1884.nc',
                    'tas_Oyr_HadGEM2-ES_historical_r1i1p1_1939-1983.nc',
                    'tas_Oyr_HadGEM2-ES_historical_r1i1p1_1885-1939.nc']

    monthly_names = ['tas_Amon_HadGEM2-ES_historical_r1i1p1_188412-190911.nc',
                     'tas_Amon_HadGEM2-ES_historical_r1i1p1_185912-188411.nc',
                     'tas_Amon_HadGEM2-ES_historical_r1i1p1_190912-193411.nc',
                     'tas_Amon_HadGEM2-ES_historical_r1i1p1_195912-198411.nc',
                     'tas_Amon_HadGEM2-ES_historical_r1i1p1_193412-195911.nc',
                     'tas_Amon_HadGEM2-ES_historical_r1i1p1_198411-200511.nc']

    ####
    #    NEEDS CALENDAR SUPPORT
    #    360 day
    #    no leap
    #
    ####
    daily_names = [
                   'tas_day_HadGEM2-ES_historical_r1i1p1_18840101-19091212.nc',
                   'tas_day_HadGEM2-ES_historical_r1i1p1_19091212-19341130.nc',
                   'tas_day_HadGEM2-ES_historical_r1i1p1_19341201-19591231.nc',
                   'tas_day_HadGEM2-ES_historical_r1i1p1_19600101-19841130.nc',
                   'tas_day_HadGEM2-ES_historical_r1i1p1_19841201-20051130.nc',
                   ]

    ####
    #    NEEDS DAYS PER MONTH CALENDAR SUPPORT
    #    360 day
    #    no leap
    #
    ####
    three_hourly_names = [
                         'tas_3hr_HadGEM2-ES_historical_r1i1p1_190001010000-190001010300.nc',
                         'tas_3hr_HadGEM2-ES_historical_r1i1p1_190001010300-190001012359.nc',
                         'tas_3hr_HadGEM2-ES_historical_r1i1p1_190001020259-190001022359.nc',
                         ]

    six_hourly_names = [
        'tas_6hr_HadGEM2-ES_historical_r1i1p1_190001010000-190001010600.nc',
        'tas_6hr_HadGEM2-ES_historical_r1i1p1_190001010600-190001012359.nc',
        'tas_6hr_HadGEM2-ES_historical_r1i1p1_190001020559-190001022359.nc',
    ]

    for fnames in [yearly_names, monthly_names, daily_names, three_hourly_names, six_hourly_names]:
        mock_dss = []
        for fname in fnames:
            mock_dss.append(MockNCDataset(fname))

        assert(check_multifile_temporal_continutity(mock_dss, time_index_in_name=-1) == False)
