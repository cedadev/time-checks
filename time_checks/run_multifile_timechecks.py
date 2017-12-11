"""
run_file_timechecks.py
==================

A wrapper to multifile_time_checks.py which takes 1:n .nc files and then
calls the time checks in given order.

Checks whether the timeseries of datafiles is complete and contiguous.

T1.006: [check_multifile_temporal_continuity]
"""
import os
import arrow
from sys import argv
from netCDF4 import Dataset, num2date

from time_checks import utils, constants
from time_checks.utils import resolve_dataset_type
from time_checks import utils, time_utils, settings, constants
from time_checks.multifile_time_checks import check_multifile_temporal_continuity

@resolve_dataset_type
def test_check_multifile_temporal_continuity(listoffiles):

    res, msg = check_multifile_temporal_continuity(listoffiles)
    if res == False:
        return "T1.006: [check_multifile_temporal_continuity]: FAILED::" + msg
    else:
       return "T1.006: [check_multifile_temporal_continuity]: OK"

