"""
file_time_tests.py
==================

A set of tests that operate at the file level.

"""

import os
import re

from datetime import datetime, timedelta
from netCDF4 import Dataset, num2date
from time_checks.test.mock_netcdf import MockNCDataset
import arrow

from time_checks import time_utils 


# File name regular expressions for different time component patterns
DT_LENGTHS = ['4', '6', '8', '10', '12', '14']

FILE_NAME_PATTERNS_SINGLE = [r'^\d{{{}}}$'.format(dtl) for dtl in DT_LENGTHS]
FILE_NAME_PATTERNS_DOUBLE = [r'^\d{{{}}}-\d{{{}}}$'.format(dtl, dtl) for dtl in DT_LENGTHS]
FILE_NAME_REGEXES = [re.compile(pattn) for pattn in (FILE_NAME_PATTERNS_SINGLE
                                                     + FILE_NAME_PATTERNS_DOUBLE)]
CMOR_TABLES_FORMAT = {'3hr': 12, '6hrLev': 10, '6hrPLev': 10, 'Amon': 6, 'LImon': 6, 'Lmon': 6, 'OImon': 6,
                      'Omon': 6, 'Oyr': 4, 'aero': 0, 'cf3hr': 12, 'cfDay': 8, 'cfMon': 6, 'cfOff': 0, 'cfSites': 0,
                      'day': 8, 'fx': 0}


def _get_nc_attr(var, attr, default=""):
    if attr in var.ncattrs():
        return getattr(var, attr)
    else:
        return default


def _convert_dataset_to_dict(ds):

    """
    Function that converts from a netCDF4 object to a dictionary in the same form as CEDA-CC.
    
    Dictionary is of the form:
    {"time": {
        "_type": "float64",
        "bounds": "time_bnds",
        "long_name": "time",
        "standard_name": "time",
        "units": "days since 1850-01-01",
        "calendar": "standard",
        "_data": [52975.5, 53005.0, 53034.5, 53065.0, 53095.5, 53126.0, 53156.5, 53187.5, 53218.0, 53248.5, 53279.0],
        "axis": "T"},
        "filename": ["so", "Omon", "MRI-CGCM3", "historical", "r1i1p1", "199501-199912"]
    """

    # time_var = ds.variables["time"]
    time_var = time_utils.get_time_variable(ds)
    d = {
        "_type": time_var.dtype.name,
        "bounds": _get_nc_attr(time_var, "bounds"),
        "long_name": _get_nc_attr(time_var, "long_name"),
        "standard_name": _get_nc_attr(time_var, "standard_name"),
        "units": _get_nc_attr(time_var, "units"),
        "calendar": _get_nc_attr(time_var, "calendar"),
        "axis": _get_nc_attr(time_var, "axis"),
        "_data": list(time_var[:])
    }

    filename_info = os.path.splitext(os.path.basename(ds.filepath()))[0].split("_")
    return {"time": d, "filename": filename_info}, time_var


# THIS FUNCTION IS ONLY REQUIRED IF WORKING DIRECTLY WITH netCDF4 OBJECTS OR MockNCDatasets
def _extract_filename_component(fpath, index=-1, delimiter="_"):
    """
    Extracts the time component from a file name as a string.

    :param fpath: file path [string]
    :param time_index_in_name: index of time component in the file name [int]
    :param delimiter: delimiter in file name [string]
    :return: time component in file [string]
    """
    fname = os.path.basename(fpath)
    fname_comp = os.path.splitext(fname)[0].split(delimiter)[index]
    return fname_comp


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

    if isinstance(ds, MockNCDataset): time_comp = _extract_filename_component(ds.filepath(), index=time_index_in_name)

    if isinstance(ds, Dataset):
        ds, time_var = _convert_dataset_to_dict(ds)
        # GET REQUIRED INFORMATION FROM DICTIONARY
        time_comp = ds['filename'][time_index_in_name]

    # REQUIRED IF WORKING DIRECTLY WITH netCDF4 OBJECTS
    # time_comp = _extract_filename_component(ds.filepath(), index=time_index_in_name)

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

    if isinstance(ds, Dataset): ds, time_var = _convert_dataset_to_dict(ds)

    # REQUIRED IF WORKING DIRECTLY WITH netCDF4 OBJECTS
    # time_comp = _extract_filename_component(ds.filepath(), index=time_index_in_name)
    # time_var = time_utils.get_time_variable(ds)
    # calendar = 'standard'
    # if 'calendar' in time_var.ncattrs():
    #     calendar = time_var.calendar

    # GET REQUIRED INFORMATION FROM DICTIONARY
    time_comp = ds['filename'][time_index_in_name]
    calendar = ds["time"]["calendar"]

    file_times = [_parse_time(comp) for comp in time_comp.split("-")]
    times = num2date([time_var[0], time_var[-1]], time_var.units, calendar=calendar)
    t_start, t_end = [arrow.get(tm.strftime()) for tm in times]
 
    if not _times_match_within_tolerance(t_start, file_times[0], tolerance): 
        return False

    if not _times_match_within_tolerance(t_end, file_times[1], tolerance):
        return False

    return True



def check_time_format_matches_frequency(ds, frequency_index=1, time_index_in_name=-1):
    """
    Checks for consistenty between the time frequency and the format of the time
    variable_table = "fx": time independent data will not have a temporal element NOT IMPLEMENTED YET
    variable_table = "yr": yearly data of the form: yyyy, test has length 4
    variable_table = "mon": monthly data of the form: yyyyMM, test has length 6
    variable_table = "monClim": monthly climatology data of the form: yyyyMM, test has length 6
    variable_table = "day": daily data of the form: yyyyMMdd, test has length 8
    variable_table = "6hr": 6 hourly data of the form: yyyyMMddhh, test has length 10
    variable_table = "3hr": 3 hourly data of the form: yyyyMMddhhmm, test has length 12
    variable_table = "subhr": sub-hourly data of the form: yyyyMMddhhmm, test has length 12

    :param ds:
    :return:
    """
    if isinstance(ds, Dataset):
        ds = _convert_dataset_to_dict(ds)

        # GET REQUIRED INFORMATION FROM DICTIONARY
        time_comp = ds['filename'][time_index_in_name]
        frequency = ds['filename'][frequency_index]
    else:
        # REQUIRED IF WORKING WITH netCDF4 objects or MockNCDatasets
        time_comp = _extract_filename_component(ds.filepath(), index=time_index_in_name)
        frequency = _extract_filename_component(ds.filepath(), index=frequency_index)

    if len(time_comp.split('-')[0]) == CMOR_TABLES_FORMAT[frequency]:
        return True
    
    return False



def check_valid_temporal_element(ds, time_index_in_name=-1):
    """
    Checks whether the temporal elements are within the valid ranges:
        years, yyyy: a four digit integer > 0000 (strictly between 1800-2900)
        months, MM: a two digit integer between 01 and 12
        days, dd: a two digit integer between 01-31
        hours, hh: a two digit integer between 00-23
        minutes, mm: a two digit integer between 00-59
    :param element:
    :return:
    """

    if isinstance(ds, Dataset):
        ds = _convert_dataset_to_dict(ds)

        # GET REQUIRED INFORMATION FROM DICTIONARY
        time_comp = ds['filename'][time_index_in_name]

    else:
        # REQUIRED IF WORKING WITH netCDF4 OBJECTS OR MockNCDatasets
        time_comp = _extract_filename_component(ds.filepath(), index=time_index_in_name)

    for time_element in time_comp.split('-'):
        length_time = len(time_element)
        if length_time >= 4:
            yyyy = int(time_element[:4])
            if length_time >= 6:
                mm = int(time_element[4:6])
                if length_time >= 8:
                    dd = int(time_element[6:8])
                    if length_time >= 10:
                        hh = int(time_element[8:10])
                        if length_time >= 12:
                            mn = int(time_element[10:12])

        if yyyy > 4000 or yyyy < 0000: return False

        if 'mm' in locals():
            if mm > 12 or mm < 01: return False
        if 'dd' in locals():
            if dd > 31 or dd < 01: return False
            # does not account for calendars where 31 may be invalid for a 360 day calendar
        if 'hh' in locals():
            if hh > 23 or hh < 00: return False
        if 'mn' in locals():
            if mn > 59 or mn < 00: return False

    return True

def check_regular_time_axis_increments(ds, frequency_index=1):
    """
    Checks that the time axis increments are at regular intervals
    :param ds:
    :return:
    """

    if isinstance(ds, Dataset):
        ds, time_var = _convert_dataset_to_dict(ds)

        calendar = ds["time"]["calendar"]
        frequency = ds['filename'][frequency_index]
        times = ds["time"]["_data"]

    delta_t = times[1] -times[0]
    if frequency == 'mon':
        # MOnthly frequencies may have irregular intervals test to be implemented
        pass

        t = 1
        while t < len(times):
            t_diff = times[t] - t[t+1]
            if t_diff != delta_t:
                return False

    return True

def check_multifile_temporal_continutity(list_of_time_elements):
    """
    Checks the temporal continutity over a list of files.
    Checks for any gaps or overlaps in the in the timeseries: for each "end" the following "start" is the next
    timestep in the series depending on the temporal resolution

    Check against filename only	Or timestamp?

    :param list_of_time_elements:
    :return:
    """

    pass


def check_multifile_temporal_completeness(list_of_time_elements):
    """
    Checks the temporal completeness over a list of files.
    
    Start to end is continuous
    For a given experiment is the timeseries complete given the CMIP5 requirements

    :param list_of_time_elements:
    :return:
    """

    pass