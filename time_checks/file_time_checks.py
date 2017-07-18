"""
file_time_tests.py
==================

A set of tests that operate at the file level.

"""

import os
import re

from netCDF4 import Dataset
import arrow

FILE_NAME_REGEXES = [
    r'\d{4,8,10,12,14}',
    r'\d{4}-\d{4}',
    r'\d{6}-\d{6}',
    r'\d{8}-\d{8}',
    r'\d{10}-\d{10}',
    r'\d{12}-\d{12}',
    r'\d{14}-\d{14}'
]


def _extract_time_comp(fpath, time_index_in_name=-1, delimiter="_"):
    """
    Extracts the time component from a file name as a string.

    :param fpath: file path [string]
    :param time_index_in_name: index of time component in the file name [int]
    :param delimiter: delimiter in file name [string]
    :return: time component in file [string]
    """
    fname = os.path.basename(ds.filepath())
    time_comp = os.path.splitext(fname)[0].split("_")[time_index_in_name]
    return time_comp


def check_file_name_time_format(ds, time_index_in_name=-1):
    """
    Checks that the format of the file name follows matches known
    regular expressions.

    :param ds: netCDF4 Dataset object.
    :return: boolean (True for success).
    """
    time_comp = _extract_time_comp(ds, time_index_in_name=time_index_in_name)
    for regex in FILE_NAME_REGEXES:
        if regex.match(time_comp):
            return True

    return False


def check_file_name_matches_time_var(ds, time_index_in_name=-1):
    """
    Checks that the file name of netCDF4 Dataset `ds` matches the time range
    found in the file. The time component in the file name is extracted at
    index `time_index_in_name` when the name is split by "_" and the extension
    removed.

    :param ds: netCDF4 Dataset object.
    :param time_index_in_name:
    :return: boolean (True for success).
    """
    fname = os.path.basename(ds.filepath())
    time_comp = os.path.splitext(fname)[0].split("_")[time_index_in_name]

    file_times = [arrow.parse(comp) for comp in time_comp.split("-")]
