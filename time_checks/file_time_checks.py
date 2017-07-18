"""
file_time_tests.py
==================

A set of tests that operate at the file level.

"""

import os
import re

from datetime import datetime, timedelta
from netCDF4 import Dataset, num2date
import arrow

from time_checks import time_utils 


# File name regular expressions for different time component patterns
DT_LENGTHS = ['4', '6', '8', '10', '12', '14']

FILE_NAME_PATTERNS_SINGLE = [r'^\d{{{}}}$'.format(dtl) for dtl in DT_LENGTHS]
FILE_NAME_PATTERNS_DOUBLE = [r'^\d{{{}}}-\d{{{}}}$'.format(dtl, dtl) for dtl in DT_LENGTHS]

FILE_NAME_REGEXES = [re.compile(pattn) for pattn in (FILE_NAME_PATTERNS_SINGLE
                                                     + FILE_NAME_PATTERNS_DOUBLE)]


def _extract_time_comp(fpath, time_index_in_name=-1, delimiter="_"):
    """
    Extracts the time component from a file name as a string.

    :param fpath: file path [string]
    :param time_index_in_name: index of time component in the file name [int]
    :param delimiter: delimiter in file name [string]
    :return: time component in file [string]
    """
    fname = os.path.basename(fpath)
    time_comp = os.path.splitext(fname)[0].split("_")[time_index_in_name]
    return time_comp


def _parse_time(tm):
    """
    Parses time component string to date time object.

    :param tm: date/time string
    :return: datetime object
    """
    # If already formatted then just parse and return
    if "-" in tm:
        return arrow.get(tm)

    # Otherwise, reformat then parse 
    padded_time = tm + "00000101000000"[len(tm):]
    splits = [4, 2, 2, 2, 2, 2]
    splits.reverse() # so we can pop them off the end

    items = []

    while padded_time:
        i = splits.pop() 
        item = padded_time[:i]
        padded_time = padded_time[i:]
        items.append(item)

    formatted_time = "{}-{}-{}T{}:{}:{}".format(*items)
    return arrow.get(formatted_time)


def _times_match_within_tolerance(t1, t2, tolerance="days:1"):
    """
    Compares two datetime/arrow objects and returns True if they are 
    within the time period specified in `tolerance` of each other.
    
    :param t1: datetime/arrow object
    :param t2: datetime/arrow object
    :param tolerance: tolerance period [string]  
    :return: boolean [True for success].
    """
    unit = tolerance.split(":")[0]
    n = float(tolerance.split(":")[1])
    delta = timedelta(**{unit: n})

    if t1 == t2:
        return True
    if (t1 - delta) < t2 < (t1 + delta):
        return True

    return False 


def check_file_name_time_format(ds, time_index_in_name=-1):
    """
    Checks that the format of the file name follows matches known
    regular expressions.

    :param ds: netCDF4 Dataset object.
    :return: boolean (True for success).
    """
    time_comp = _extract_time_comp(ds.filepath(), time_index_in_name=time_index_in_name)

    for regex in FILE_NAME_REGEXES:
        if regex.match(time_comp):
            return True

    return False


def check_file_name_matches_time_var(ds, time_index_in_name=-1, tolerance='days:1'):
    """
    Checks that the file name of netCDF4 Dataset `ds` matches the time range
    found in the file. The time component in the file name is extracted at
    index `time_index_in_name` when the name is split by "_" and the extension
    removed. The checks are done within the tolerance level specified.

    :param ds: netCDF4 Dataset object.
    :param time_index_in_name: index of time component in the file name [int]
    :param tolerance: tolerance of time difference allowed in match [string]
    :return: boolean (True for success).
    """
    time_comp = _extract_time_comp(ds.filepath(), time_index_in_name=time_index_in_name)
    file_times = [_parse_time(comp) for comp in time_comp.split("-")]

    # Get the time variable from the file
    time_var = ds.variables[time_utils.get_time_variable(ds)] 

    calendar = 'standard'
    if 'calendar' in time_var.ncattrs():
        calendar = time_var.calendar

    times = num2date([time_var[0], time_var[-1]], time_var.units, calendar=calendar)
    t_start, t_end = [arrow.get(tm.strftime()) for tm in times]
 
    if not _times_match_within_tolerance(t_start, file_times[0], tolerance): 
        return False

    if not _times_match_within_tolerance(t_end, file_times[1], tolerance):
        return False

    return True

