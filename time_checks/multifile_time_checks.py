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


def OLD_check_multifile_temporal_continuity(dss, time_index_in_name=-1, frequency_index=1):
    """
    Checks for the temporal continuity over a given number of data files.

    The test checks that for each file in a time series the start time of given in the
    filename is one time step ahead of the end time of the previous file in the time series.

    This test checks that from the start for a given time series that:
        (1) there are no jumps in the time series
        (2) there are no missing time steps in the time series
        (3) that the set is complete, i.e. it is continuous from file 0:n by fulfilling (1) and (2)

    This routine only checks the filename as it assumes that each file has passed the check:
        check_file_name_matches_time_var

    :param dss: list of netCDF4 Dataset objects or compliant dictionary objects
    :param time_index_in_name: index of the time index in the filename
    :param frequency_index: index of the frequency element in the filename
                            (actually the cmor table, frequency must be implied from this)

    :return: boolean [True for success]
    """
    # Sort the file list just in case files have been provided in a strange order
    dss.sort()
    file_times = []

    # Get time components from all files and check they are monotonic
    time_comps = [ds['filename'][time_index_in_name] for ds in dss]
    times = chain(*[tc.split("-") for tc in time_comps])


    if frequency not in ("day",): raise Exception("Frequency {} not supported.".format(frequency))
    for ds in dss:
        ds = utils._resolve_dataset_type(ds)
        time_comp = ds['filename'][time_index_in_name]
        frequency = ds['filename'][frequency_index]

        units = ds['time']["units"]
        calendar = ds['time']["calendar"]
        time_var = [5000, 5001]

        file_times.append([parse_time(time_element, units, calendar) for time_element in time_var])
        #file_times.append([utils._parse_time(comp) for comp in time_comp.split("-")])
        sorted_times = sorted(file_times)

   # import pdb; pdb.set_trace()
    #sorted_times = [[arrow.get("1860-02-27"), arrow.get("1860-02-28")],
    #                [arrow.get("1860-02-29"), arrow.get("1860-03-01")],
    #                [arrow.get("1860-03-02"), arrow.get("1860-03-03")],
    #                ]
    srt_i = 0; end_i = 1
    ntimes = 0

    while ntimes < len(sorted_times) - 1:

        # Get end time of one file and start of next
        end = sorted_times[ntimes][end_i]
        start = sorted_times[ntimes+1][srt_i]

        if frequency in ["yr", "Oyr"]:
            if end.shift(years=+1) != start: return False
        elif frequency in ["Amon", "Omon", "OImon", "Lmon", "LImon", "cfMon"]:
            if end.shift(months=+1) != start: return False
        elif frequency in ["day", "cfDay"]:
            if end.shift(days=+1) != start: return False
        elif frequency in ["3hr", "cf3hr"]:
            if end.shift(hours=+3) != start: return False
        elif frequency in ["6hrLev", "6hrPLev"]:
            if end.shift(hours=+6) != start: return False

        else:
            raise Exception("Frequency of unknown format, must be a CMIP5 table format")

        ntimes += 1

    return True



def check_multifile_temporal_continuity(dss, time_index_in_name=-1, frequency_index=1):
    """
    """
    dss = [utils._resolve_dataset_type(ds) for ds in dss]

    # Sort the datasets by file name just in case files have been provided in a strange order
    dss_by_name = [(ds['filename'], ds) for ds in dss]
    dss_by_name.sort()

    # Get first and last dates and time frequency to generate full time series
    # for all files
    (start, _), frequency = utils._get_details_from_file_name(dss_by_name[0])
    (_1, end), _2 = utils._get_details_from_file_name(dss_by_name[-1])

    # Convert start and end to datetimes
    start, end = [utils.str_to_anytime(tm) for tm in (start, end)]
    calendar = dss_by_name[0]['calendar']

    # Full series for all files
    series = utils.TimeSeries(start, end, (1, frequency), calendar).series


    return True

