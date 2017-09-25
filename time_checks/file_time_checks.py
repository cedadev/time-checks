"""
file_time_tests.py
==================

A set of tests that operate at the file level.

"""

import arrow
from netCDF4 import Dataset, num2date

from time_checks import utils, constants


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

    ds = utils._resolve_dataset_type(ds)
    time_comp = ds['filename'][time_index_in_name]

    for regex in constants.FILE_NAME_REGEXES:
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

    ds = utils._resolve_dataset_type(ds)
    time_var = ds["time"]["_data"]
    time_comp = ds['filename'][time_index_in_name]
    calendar = ds["time"]["calendar"]

    file_times = [utils._parse_time(comp) for comp in time_comp.split("-")]
    times = num2date([time_var[0], time_var[-1]], ds["time"]["units"], calendar=calendar)
    t_start, t_end = [arrow.get(tm.strftime()) for tm in times]

    if not utils._times_match_within_tolerance(t_start, file_times[0], tolerance):
        return False

    if not utils._times_match_within_tolerance(t_end, file_times[1], tolerance):
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

    ds = utils._resolve_dataset_type(ds)
    time_comp = ds['filename'][time_index_in_name]
    frequency = ds['filename'][frequency_index]

    if len(time_comp.split('-')[0]) == constants.CMOR_TABLES_FORMAT[frequency]:
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

    ds = utils._resolve_dataset_type(ds)
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

def calculate_detlat_time_series(times, valid_dt):
    """
       calculate_detla_time_series

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

    ds = utils._resolve_dataset_type(ds)
    frequency = ds['filename'][frequency_index]
    calendar = ds["time"]["calendar"]
    times = ds["time"]["_data"]

    delta_t = [times[1] - times[0]]

    if frequency == 'mon' and calendar in constants.IRREGULAR_MONTHLY_CALENDARS:
        true_or_false = calculate_detlat_time_series(times, constants.VALID_MONTHLY_TIME_DIFFERENCES)

    else:
        true_or_false = calculate_detlat_time_series(times, delta_t)

    return true_or_false
