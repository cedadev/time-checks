"""
test_file_time_checks.py
========================

Tests for the checks in the `file_time_checks.py` module.
"""

from netCDF4 import Dataset

from time_checks.multifile_time_checks import *
from time_checks.test.mock_netcdf import MockNCDataset
from time_checks import utils, time_utils, settings, constants

# INCLUDE MockNCDataset in supported settings
settings.supported_datasets.append(MockNCDataset)


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

    daily_names_2 = [
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
                        'tas_6hrLev_HadGEM2-ES_historical_r1i1p1_190001010000-190001010600.nc',
                        'tas_6hrLev_HadGEM2-ES_historical_r1i1p1_190001011200-190001012359.nc',
                        'tas_6hrLev_HadGEM2-ES_historical_r1i1p1_190001020559-190001030000.nc',
                        'tas_6hrLev_HadGEM2-ES_historical_r1i1p1_190001030600-190001050000.nc',
                       ]

    #for fnames in [yearly_names, monthly_names, daily_names, three_hourly_names, six_hourly_names]:
    for fnames in [daily_names_2]:
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
        'tas_6hrLev_HadGEM2-ES_historical_r1i1p1_190001010000-190001010600.nc',
        'tas_6hrLev_HadGEM2-ES_historical_r1i1p1_190001011300-190001012359.nc',
        'tas_6hrLev_HadGEM2-ES_historical_r1i1p1_190001020559-190001022359.nc',
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
        'tas_6hrLev_HadGEM2-ES_historical_r1i1p1_190001010000-190001010600.nc',
        'tas_6hrLev_HadGEM2-ES_historical_r1i1p1_190001010600-190001012359.nc',
        'tas_6hrLev_HadGEM2-ES_historical_r1i1p1_190001020559-190001022359.nc',
    ]

    for fnames in [yearly_names, monthly_names, daily_names, three_hourly_names, six_hourly_names]:
        mock_dss = []
        for fname in fnames:
            mock_dss.append(MockNCDataset(fname))

        assert(check_multifile_temporal_continutity(mock_dss, time_index_in_name=-1) == False)
