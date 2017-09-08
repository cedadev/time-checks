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
from time_checks import settings

# File name regular expressions for different time component patterns
DT_LENGTHS = ['4', '6', '8', '10', '12', '14']

FILE_NAME_PATTERNS_SINGLE = [r'^\d{{{}}}$'.format(dtl) for dtl in DT_LENGTHS]
FILE_NAME_PATTERNS_DOUBLE = [r'^\d{{{}}}-\d{{{}}}$'.format(dtl, dtl) for dtl in DT_LENGTHS]
FILE_NAME_REGEXES = [re.compile(pattn) for pattn in (FILE_NAME_PATTERNS_SINGLE
                                                     + FILE_NAME_PATTERNS_DOUBLE)]
CMOR_TABLES_FORMAT = {'3hr': 12, '6hrLev': 10, '6hrPLev': 10, 'Amon': 6, 'LImon': 6, 'Lmon': 6, 'OImon': 6,
                      'Omon': 6, 'Oyr': 4, 'aero': 0, 'cf3hr': 12, 'cfDay': 8, 'cfMon': 6, 'cfOff': 0, 'cfSites': 0,
                      'day': 8, 'fx': 0}
IRREGULAR_MONTHLY_CALENDARS = ['gregorian', 'proleptic_gregorian', 'julian', 'noleap', '365_day', 'standard']
VALID_MONTHLY_TIME_DIFFERENCES = [29.5, 30.5, 31.0]


def _resolve_dataset_type(ds):
    """
    _resolve_dataset_type

    This funtion analyses type of dataset (ds)
        - a netCDF4 Dataset
        - a MockNCDataset - used in testing only
        - a compliant dictionary in the form used by this class
          and used to interface with CEDA-CC


    :param ds: a dataset object [type anyalysed in this routine]
    :return: ds [dictonary]
    """

    # First if clause required for testing only - will remove in due course
    if isinstance(ds, MockNCDataset):
        ds = {"time": [],
              "filename": os.path.splitext(os.path.basename(ds.filepath()))[0].split("_")}
    elif isinstance(ds, Dataset):
        ds = _convert_dataset_to_dict(ds)
    elif isinstance(ds, dict):
        # TODO: Check dictionary is of valid form
        pass
    else:
        raise Exception("Unsupported data type. "
                        "Data types supported are netCDF4 objects or CEDA-CC compliant dictionary objects")

    return ds

def _get_nc_attr(var, attr, default=""):
    """
    _get_nc_attr

    This function, looks inside a netCDF 4 Dataset object for the attributes of a variable within the object.
    If the attribute specified for the variable exists then the attribute is returned.

    If the attribute is not associated with the variable then an empty string is returned as default

    :param var: variable name [string]
    :param attr: attribute name [string]
    :param default: Default value to be returned [string]
    :return: variable attribute (default is empty) [string]
    """
    if attr in var.ncattrs():
        return getattr(var, attr)
    else:
        return default


def _convert_dataset_to_dict(ds):
    """
        _convert_dataset_to_dict

    This function converts from a netCDF4 object to a dictionary that is in the same form as CEDA-CC.

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

    :param ds: a netCDF4 Dataset object [netCDF4 Dataset object]
    :return: key file metadata [dictionary]
    """
    """
    The time_var is retrieved using the get_time_variable function from the time_utils code 
    this allows for a temporal axis that does not use the standard name "time". 
    time_var is a netCDF4 variable and therefore has the netCDF4 variable attributes used here:
        dtype, bounds, long_name, standard_name, units, calendar, axis
    """
    time_var = time_utils.get_time_variable(ds)
    time_dict = {
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

    dict = {"time": time_dict, "filename": filename_info}

    # Returns a dictionary of temporal axis information that is in the same form as used by CEDA-CC
    return dict


def _parse_time(tm):
    """
        _parse_time

    Parses time component string to an arrow date time object.

    :param tm: date-time [string]
    :return: datetime [arrow object]
    """
    # If already formatted then just parse and return
    if "-" in tm:
        return arrow.get(tm)

    # Otherwise, reformat then parse 
    padded_time = tm + "00000101000000"[len(tm):]
    splits = [4, 2, 2, 2, 2, 2]
    splits.reverse()  # so we can pop them off the end

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
        _times_match_within_tolerance

    Compares two datetime arrow objects and returns True if they match
    within the time period specified in `tolerance`.
    
    :param t1: datetime [arrow object]
    :param t2: datetime [arrow object]
    :param tolerance: tolerance period [string]  
    :return: boolean [True for success]
    """
    unit = tolerance.split(":")[0]
    n = float(tolerance.split(":")[1])
    delta = timedelta(**{unit: n})

    if t1 == t2:
        return True
    if (t1 - delta) < t2 < (t1 + delta):
        return True

    return False


def _calculate_detla_time_series(times, valid_dt):
    """
       _calculate_detla_time_series

    This function calculates the differences between all the elements of a timeseries and
    compares the differences with a valid time difference.

    True is returned if all the differences are valid; i.e. equal to the valid time difference argument
    False is returned if any of the difference fail to match the valid the time difference argument

    :param times: List of times
    :param valid_dt: Valid time difference, usually scalar, list of valid times supported
    :return: boolean [True for success]
    """

    t = 0
    while t < len(times) - 1:
        t_diff = times[t + 1] - times[t]
        if t_diff not in valid_dt:
            return False
        else:
            return True


def check_file_name_time_format(ds, time_index_in_name=-1):
    """
        check_file_name_time_format

    Checks that the format of the file name follows matches known regular expressions of the form YYYY[mm[DD[HH[MM]]]].
    Where [] indicated the elements are optional and
    YYYY: is a four digit integer year
    mm: is a two digit integer month
    DD: is a two digit integer day
    HH: is a two digit integer hour
    MM: is a two digit integer minute

    :param ds: input dataset [netCDF4 Dataset object (also MockNCDataset) or compliant dictionary]
    :param time_index_in_name: index of time component in the file name [int]
    :return: boolean (True for success).
    """

    ds = _resolve_dataset_type(ds)
    time_comp = ds['filename'][time_index_in_name]

    for regex in FILE_NAME_REGEXES:
        if regex.match(time_comp):
            return True

    return False


def check_file_name_matches_time_var(ds, time_index_in_name=-1, tolerance='days:1'):
    """
        check_file_name_matches_time_var

    Checks that the file name of a dataset (file) `ds` matches the time range
    found in the file. The time component in the file name is extracted at
    index `time_index_in_name` when the name is split by "_" and the extension
    removed. The checks are done within the tolerance level specified.

    :param ds: input dataset [netCDF4 Dataset object (also MockNCDataset) or compliant dictionary]
    :param time_index_in_name: index of time component in the file name [int]
    :param tolerance: tolerance of time difference allowed in match [string]
    :return: boolean [True for success]
    """

    ds = _resolve_dataset_type(ds)
    time_var = ds["time"]["_data"]
    time_comp = ds['filename'][time_index_in_name]
    calendar = ds["time"]["calendar"]

    file_times = [_parse_time(comp) for comp in time_comp.split("-")]
    times = num2date([time_var[0], time_var[-1]], ds["time"]["units"], calendar=calendar)
    t_start, t_end = [arrow.get(tm.strftime()) for tm in times]
 
    if not _times_match_within_tolerance(t_start, file_times[0], tolerance): 
        return False

    if not _times_match_within_tolerance(t_end, file_times[1], tolerance):
        return False

    return True


def check_time_format_matches_frequency(ds, frequency_index=1, time_index_in_name=-1):
    """
        check_time_format_matches_frequency

    Checks for consistenty between the time frequency and the format of the time.

    cmor_table = "yr", "Oyr": yearly data of the form: yyyy, test has length 4
    cmor_table = "Amon", "Lmon", "Omon", "LImon", "OImon", "cfMon": monthly data of the form: yyyyMM, test has length 6
    cmor_table = "monClim": monthly climatology data of the form: yyyyMM, test has length 6
    cmor_table = "day", "cfDay": daily data of the form: yyyyMMdd, test has length 8
    cmor_table = "6hrLev", "6hrPLev": 6 hourly data of the form: yyyyMMddhh, test has length 10
    cmor_table = "3hr", "": 3 hourly data of the form: yyyyMMddhhmm, test has length 12
    cmor_table = "subhr": sub-hourly data of the form: yyyyMMddhhmm, test has length 12


    NOT IMPLEMENTED YET: 'aero': 0,'cfOff': 0, 'cfSites': 0, 'fx': 0

    :param ds: input dataset [netCDF4 Dataset object (also MockNCDataset) or compliant dictionary]
    :return: boolean [True for success]
    """

    ds = _resolve_dataset_type(ds)
    time_comp = ds['filename'][time_index_in_name]
    frequency = ds['filename'][frequency_index]

    if len(time_comp.split('-')[0]) == CMOR_TABLES_FORMAT[frequency]:
        return True
    
    return False


def check_valid_temporal_element(ds, time_index_in_name=-1):
    """
        check_valid_temporal_element
    Checks whether the temporal elements are within the valid ranges:
    years, yyyy: a four digit integer > 0000 (strictly between 1800-2900)
    months, MM: a two digit integer between 01 and 12
    days, dd: a two digit integer between 01-31
    hours, hh: a two digit integer between 00-23
    minutes, mm: a two digit integer between 00-59

    :param ds: input dataset [netCDF4 Dataset object (also MockNCDataset) or compliant dictionary]
    :param time_index_in_name: index of time component in the file name [int]
    :return: boolean [True for success]
    """

    ds = _resolve_dataset_type(ds)
    time_comp = ds['filename'][time_index_in_name]

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
       check_regular_time_axis_increments

    This function checks that the given time axis increments for a given file are regularly spaced throughout.

    Since it is common to have the timestamp of monthly data placed at the middle of month,
    monthly CMIP5 maybe irregularly spaced when using any of the following calendars:
        'gregorian', 'proleptic_gregorian', 'julian', 'noleap', '365_day', 'standard',
    For these calendars valid time axis increments are 29.5, 30.5 and 31 days.

    :param ds: input dataset [netCDF4 Dataset object (also MockNCDataset) or compliant dictionary]
    :param frequency_index: index of the frequency element in the filename
                            (actually the cmor table, frequency must be implied from this) [int]
    :return: boolean [True for success]
    """

    ds = _resolve_dataset_type(ds)
    frequency = ds['filename'][frequency_index]
    calendar = ds["time"]["calendar"]
    times = ds["time"]["_data"]

    delta_t = [times[1] -times[0]]

    if frequency == 'mon' and calendar in IRREGULAR_MONTHLY_CALENDARS:
        res = _calculate_detla_time_series(times, VALID_MONTHLY_TIME_DIFFERENCES)

    else:
        res = _calculate_detla_time_series(times, delta_t)

    return res
