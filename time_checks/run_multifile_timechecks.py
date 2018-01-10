"""
run_file_timechecks.py
==================

A wrapper to multifile_time_checks.py which takes 1:n .nc files and then
calls the time checks in given order.

Checks whether the timeseries of datafiles is complete and contiguous.

Returns message of [check_multifile_temporal_continuity]: OK/FAILED
"""
import os
import arrow
from sys import argv
from netCDF4 import Dataset, num2date

from time_checks import utils, constants
from time_checks.utils import resolve_dataset_type
from time_checks import utils, time_utils, settings, constants
from time_checks.multifile_time_checks import check_multifile_temporal_continuity


# python run_multifile_timechecks.py ../test_data/cmip5/ua_day_IPSL-CM5A-LR_historical_r1i1p1_19500101-19591231.nc  ../test_data/cmip5/ua_day_IPSL-CM5A-LR_historical_r1i1p1_19800101-19891231.nc ../test_data/cmip5/ua_day_IPSL-CM5A-LR_historical_r1i1p1_19600101-19691231.nc  ../test_data/cmip5/ua_day_IPSL-CM5A-LR_historical_r1i1p1_19900101-19991231.nc ../test_data/cmip5/ua_day_IPSL-CM5A-LR_historical_r1i1p1_19700101-19791231.nc  ../test_data/cmip5/ua_day_IPSL-CM5A-LR_historical_r1i1p1_20000101-20051231.nc


@resolve_dataset_type
def test_check_multifile_temporal_continuity(listoffiles):
    res, msg = check_multifile_temporal_continuity(listoffiles)

    if res == False:
        return "[check_multifile_temporal_continuity]: FAILED::" + msg
    else:
        return "[check_multifile_temporal_continuity]: OK"


if __name__ == '__main__':

    args = argv[1:]
    files = []
    for f in args:
        files.append(Dataset(f))
    msg = test_check_multifile_temporal_continuity(files)
    print msg