
import os
import re
from datetime import timedelta

import arrow
from netCDF4 import Dataset, num2date

from time_checks import time_utils


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
    if isinstance(ds, Dataset):
        ds = _convert_dataset_to_dict(ds)
    elif hasattr(ds, 'filepath'):
        ds = {"time": {
                    "_type": "float64",
                    "bounds": "time_bnds",
                    "long_name": "time",
                    "standard_name": "time",
                    "units": "days since 1850-01-01",
                    "calendar": "360_day",
                    "_data": [],
                    "axis": "T"},
              "filename": os.path.splitext(os.path.basename(ds.filepath()))[0].split("_")}
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


def OLD_parse_time_new(time_element, units="day since 1850-01-01", calendar="standard"):
    """
        _parse_time

    Parses time component string to an arrow date time object.

    :param tm: date-time [string]
    :return: datetime [arrow object]
    """
    # If already formatted then just parse and return since "-" is a component in arrow times.
    if "-" in tm:
        return arrow.get(tm)

    # try doing something with just strings

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

    # Else do it with the actual time and units and calendar
    t = cf_units.num2date(time_comp, units, calendar)

    return arrow.get(t.year, t.month, t.day, t.hour, t.minute, t.second)


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


def get_nc_datetime(time_comp, units, calendar):
    """
    Returns a time object from netcdftime library. Type can be a number of date time
    objects reflecting the calendar specified.

    :param time_comp: time value [integer]
    :param units: time units [string]
    :param calendar: calendar [string]
    :return: a netcdftime object.
    """
    t = cf_units.num2date(time_comp, units, calendar)
    return t


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



class DateTimeAnyTime(object):
    """
    Class to mimmick the interface of a ``datetime.datetime`` object. It has the
    same time component attributes so can be treated like a datetime object by
    other code.

    This allows _illegal_ time values to be set such as the 30th February - as used
    by the 360_day calendar. The requirement to use dates that are out of range means
    we cannot use ``datetime`` or ``arrow`` objects.
    """

    def __init__(self, year, month=1, day=1, hour=0, minute=0, second=0, microsecond=0):
        """

        :param year: year [integer]
        :param month: month [integer], default: 1
        :param day: day [integer], default: 1
        :param hour: hour [integer], default: 0
        :param minute: minute [integer], default: 0
        :param second: second [integer], default: 0
        :param microsecond: microsecond [integer], default: 0
        """
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.microsecond = microsecond

        self._components = (self.year, self.month, self.day, self.hour,
                           self.minute, self.second, self.microsecond)

    def __str__(self):
        return "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{}".format(*self._components)

    def __repr__(self):
        return str(self)


def str_to_anytime(dt):
    """
    Takes a string representing date/time and returns a DateTimeAnyTime object.
    String formats should start with Year and go through to Microsecond, but you
    can miss out anything from month onwards.

    :param dt: string representing a date/time [string]
    :return: DateTimeAnyTime object
    """
    defaults = [-1, 1, 1, 0, 0, 0, 0]
    lens = [4, 2, 2, 2, 2, 2, -1]
    cleaned_dt = re.sub("[- T:.]", "", dt)
    components = []

    for length in lens:
        if len(cleaned_dt) == 0:
            break
        components.append(int(cleaned_dt[:length]))
        cleaned_dt = cleaned_dt[length:]

    return DateTimeAnyTime(*components)



class TimeSeries(object):
    """
    TimeSeries class - able to generate a time series from a start, end, interval
    and calendar.
    """
    # Define constants for calculating intervals
    _second = (0, 1)
    _minute = (0, 60)
    _hour = (0, 3600)
    _day = (1, 0)

    SUPPORTED_FREQUENCIES = ['day', 'month']

    def __init__(self, start, end, delta, calendar="standard"):
        self._set_delta(delta)
        self.base_time_unit = 'days since {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{}'.format()
        self.start = get_nc_datetime(start, "")

    def _set_delta(self, delta):
        """

        :param delta:
        :return:
        """
        if type(delta) not in (tuple, list) or len(delta) != 2:
            raise Exception('Delta must be tuple of (<number>, <time_unit>) such as: (3, "hour")')

        if not delta[1] in self.SUPPORTED_FREQUENCIES:
            raise Exception("Delta uses time frequency '{}' that is not yet supported.".format(delta[1]))

        if delta[1] in self.FREQUENCY_MAPPINGS:
            delta = (delta[0], self.FREQUENCY_MAPPINGS[delta[1]])

        self.delta = delta

