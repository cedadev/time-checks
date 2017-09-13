"""
multiFile_time_checks.py
==================

A set of tests that operate at the file level.

"""


import os, re, arrow, cf_units
from datetime import datetime, timedelta
from netCDF4 import Dataset, num2date

from time_checks.test.mock_netcdf import MockNCDataset
from time_checks import utils, time_utils, settings, constants

def parse_time(time_comp, units, calendar):

    t = cf_units.num2date(time_comp, units, calendar)
    return arrow.get(t.year, t.month, t.day, t.hour, t.minute, t.second)

def check_multifile_temporal_continutity(dss, time_index_in_name=-1, frequency_index=1):
    """
       check_multifile_temporal_continutity:

    This function checks for the temporal continutiy over a given number of datafiles.

    The test is checks that for each file in a timeseries
    that the start time of given in the filename is one timestep ahead of the end time
    of the previous file in the timeseries.

    This test checks that from the start for a given timeseries that
        (1) there are no jumps in the timeseries
        (2) there are no missing timesteps in the timesesries
        (3) that the set is complete, i.e. it is continuous from file 0:n by fullfilling (1) and (2)

    This routine only checks the filename it assumes that each file has passed the QC test:
        check_file_name_matches_time_var

    :param dss: list of netCDF4 Dataset objects or compliant dictionary objects
    :param time_index_in_name: index of the time index in the filename
    :param frequency_index: index of the frequency element in the filename
                            (actually the cmor table, frequency must be implied from this)

    :return: boolean [True for success]
    """


    file_times = []
    for ds in dss:
        ds = utils._resolve_dataset_type(ds)
        time_comp = ds['filename'][time_index_in_name]
        frequency = ds['filename'][frequency_index]
        units = ds['time']["units"]
        calendar = ds['time']["calendar"]
        time_var = [5000,5001]
        file_times.append([parse_time(time_element, units, calendar) for time_element in time_var])
        #file_times.append([utils._parse_time(comp) for comp in time_comp.split("-")])
        sorted_times = sorted(file_times)

   # import pdb; pdb.set_trace()
    sorted_times = [[arrow.get("1860-02-27"), arrow.get("1860-02-28")],
                    [arrow.get("1860-02-29"), arrow.get("1860-03-01")],
                    [arrow.get("1860-03-02"), arrow.get("1860-03-03")],
                    ]
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
