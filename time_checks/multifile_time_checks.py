"""
multiFile_time_checks.py
========================

A set of tests that operate at the multiple file level.

"""

import re
from datetime import timedelta
from itertools import chain

from time_checks import utils
from time_checks.utils import resolve_dataset_type


@resolve_dataset_type
def check_multifile_temporal_continuity(dss, time_index_in_name=-1, frequency_index=1):
    """
    Takes a sequence of Datasets and checks that there is temporal continuity
    between the file names and the contents of the files.

    :param dss: sequence of Dataset objects [dictionary or NetCDF4 Dataset]
    :param time_index_in_name: index of the time component in the file names
    :param frequency_index: index of the frequency component in the file names
    :return: Boolean (Success or Failure)
    """
    err_msg = ""

    # Sort the datasets by file name just in case files have been provided in a strange order
    dss_by_name = [(ds['filename'], ds) for ds in dss]
    dss_by_name.sort()

    # Get first and last dates and time frequency to generate full time series
    # for all files
    (start, _), frequency = utils.get_start_end_freq(dss_by_name[0][0])
    (_1, end), _2 = utils.get_start_end_freq(dss_by_name[-1][0])

    # Convert start and end to date-times
    start, end = [utils.str_to_anytime(tm) for tm in (start, end)]
    calendar = dss_by_name[0][1]['time']['calendar']

    # Map the frequency to one that will work with TimeSeries class
    mapped_frequency = utils.map_frequency(frequency)

    # Full series for all files/
    series = utils.TimeSeries(start, end, mapped_frequency, calendar).series

    # Go through each file checking that the combination of all makes up the
    # full expected series
    for fpath, ds in dss_by_name:
        (f_start, f_end), f_frequency = utils.get_start_end_freq(fpath)
        f_start, f_end = [utils.str_to_anytime(tm) for tm in (f_start, f_end)]

        f_mapped_frequency = utils.map_frequency(f_frequency)
        f_series = utils.TimeSeries(f_start, f_end, f_mapped_frequency, calendar).series

        # If file series is longer than remaining full series then fail
        if len(f_series) > len(series):
            err_msg = "File is out of series range"
            return False, err_msg

        # Loop through series: removing from both full series and file series
        #  when both are equal
        while series:
            if not f_series: break

            dt = series[0]

            if utils.compare(f_series[0], "==", dt):
                f_series.remove(dt)
                series.remove(dt)
            else:
                err_msg = "File not in series"
                return False, err_msg

    # Check if series still contains values: if so return False
    if series:
        err_msg = "Temporal consistency error"
        return False, err_msg

    return True, err_msg
