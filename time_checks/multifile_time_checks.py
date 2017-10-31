"""
multiFile_time_checks.py
========================

A set of tests that operate at the multiple file level.

"""

import re
from datetime import timedelta
from itertools import chain
import arrow
import cf_units

from time_checks import utils


def check_multifile_temporal_continuity(dss, time_index_in_name=-1, frequency_index=1):
    """
    """
    dss = [utils._resolve_dataset_type(ds) for ds in dss]

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

        print len(series), len(f_series)
        if len(f_series) > len(series):
            return False

        # Loop through series: removing from both full series and file series
        #  when both are equal
        while series:
            if not f_series: break

            dt = series[0]

            if f_series[0] == dt:
                f_series.remove(dt)
                series.remove(dt)
            else:
                return False

    # Check if series still contains values: if so return False
    if series: return False

    return True

