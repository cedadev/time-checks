
import os
import re
from datetime import timedelta

import arrow
import cf_units
from netCDF4 import Dataset, num2date

from time_checks import time_utils, constants


def get_start_end_freq(finfo, time_index_in_name=-1, frequency_index=1):
    """
    Returns a tuple of ((start, end), frequency) parsed from file name
    or file name component list.

    :param finfo: File name/path or file name component list
    :param time_index_in_name: index of time component in file name
    :param frequency_index: index of frequency component in file name
    :return: Tuple of: ((start, end), frequency)
    """
    if type(finfo) is str:
        fname = os.path.splitext(os.path.basename(finfo))[0]
        finfo = fname.split("_")

    start, end = finfo[time_index_in_name].split("-")
    frequency = finfo[frequency_index]

    return (start, end), frequency


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

    @property
    def _components(self):
        return self.year, self.month, self.day, self.hour, self.minute, self.second, self.microsecond

    def __str__(self):
        return "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{}".format(*self._components)

    def __repr__(self):
        return str(self)

    def __gt__(self, other):
        this, other = self._components, other._components
        return this > other

    def __lt__(self, other):
        this, other = self._components, other._components
        return this < other

    def __ge__(self, other):
        this, other = self._components, other._components
        return this >= other

    def __le__(self, other):
        this, other = self._components, other._components
        return this <= other


def str_to_anytime(dt):
    """
    Takes a string representing date/time and returns a DateTimeAnyTime object.
    String formats should start with Year and go through to Microsecond, but you
    can miss out anything from month onwards.

    :param dt: string representing a date/time [string]
    :return: DateTimeAnyTime object
    """
    if len(dt) < 1:
        raise Exception("Must provide at least the year as argument to create date time.")

    # Start with most common pattern
    regex = re.compile("^(\d+)-(\d+)-(\d+)[T ](\d+):(\d+):(\d+).(\d+)$")
    match = regex.match(dt)
    if match:
        return DateTimeAnyTime(*[int(i) for i in match.groups()])

    defaults = [-1, 1, 1, 0, 0, 0, 0]
    lens = [4, 2, 2, 2, 2, 2, None]
    cleaned_dt = re.sub("[- T:.]", "", dt)
    components = []

    for length in lens:
        if len(cleaned_dt) == 0:
            break

        value = int(cleaned_dt[:length])

        components.append(value)
        cleaned_dt = cleaned_dt[length:]

    components += defaults[len(components):]
    return DateTimeAnyTime(*components)


class TimeSeries(object):
    """
    TimeSeries class - able to generate a time series from a start, end, interval
    and calendar.
    """
    # Define constants for calculating intervals
    _microsecond = (0, 0, 1)
    _second = (0, 1)
    _minute = (0, 60)
    _hour = (0, 3600)
    _day = (1, 0)

    # Conversion factors
    CONVERSION_FACTORS = {('microsecond', 'second'): 1000.,
                          ('second', 'day'): 60 * 60 * 24.,
                          ('minute', 'day'): 60 * 24.,
                          ('hour', 'day'): 24.}

    SUPPORTED_FREQUENCIES = ['hour', 'day', 'month', 'year']
    FREQUENCY_MAPPINGS = {'mon': 'month', 'Amon': 'month', 'Omon': 'month',
                          'yr': 'year', 'Ayr': 'year', 'Oyr': 'year',
                          'hr': 'hour'
                          }


    def __init__(self, start, end, delta, calendar="standard"):
        """

        :param start: an instance of
        :param end:
        :param delta:
        :param calendar:
        """
        self._check_date_times(*[start, end])

        self._clean_delta(delta)
        self.calendar = calendar
        self.base_time_unit = 'days since {}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}.{}'.format(*start._components)
        self.series = []

        # In the case of year and monthly deltas we need to convert the `_components` of DateTimeAnyTime objects
        if self.delta.unit == "year":
            self._generate_time_series_year_delta(start, end)
        elif self.delta.unit == "month":
            self._generate_time_series_month_delta(start, end)
        # In all other cases we use NetCDF datetime objects and their operations
        else:
            self._generate_time_series(start, end)


    def _check_date_times(self, *times):
        """
        Asserts that each time is an instance of DateTimeAnyTime
        :param times:
        :return:
        """
        for tm in times:
            if not isinstance(tm, DateTimeAnyTime):
                raise TypeError("Datetimes must be of type: DateTimeAnyTime, not: {}".format(type(tm)))


    def _clean_delta(self, delta):
        """

        :param delta:
        :return:
        """
        if type(delta) not in (tuple, list) or len(delta) != 2:
            raise Exception('Delta must be tuple of (<number>, <time_unit>) such as: (3, "hour")')

        if delta[1] in self.FREQUENCY_MAPPINGS:
            delta = (delta[0], self.FREQUENCY_MAPPINGS[delta[1]])

        if not delta[1] in self.SUPPORTED_FREQUENCIES:
            raise Exception("Delta uses time frequency '{}' that is not yet supported.".format(delta[1]))

        # Define simple class for holding the delta
        class Delta(object):
            def __init__(self, n, unit):
                self.n = n
                self.unit = unit

        self.delta = Delta(*delta)


    def _resolve_delta(self):
        """
        Reads `self.delta` set as (<n>, <time_interval>) and returns as tuple of:
            (<n_days>, <n_seconds>, <n_microseconds>)

        :return: Tuple of (<n_days>, <n_seconds>, <n_microseconds>)
        """
        if self.delta.unit == 'day':
            return (self.delta.n, 0, 0)
        elif self.delta.unit == 'hour':
            return (self.delta.n / self.CONVERSION_FACTORS[('hour', 'day')], 0, 0)


    def _get_as_netcdf_time(self, anytime):
        """
        Converts the incoming DateTime/DateTimeAnyTime into a netCDF time object.
        The base time unit and calendar set on the object are used.

        :param anytime: an instance of DateTimeAnyTime or DateTime
        :return: netCDF Time object (aware of calendars)
        """
        value = cf_units.date2num(anytime, self.base_time_unit, self.calendar)
        return get_nc_datetime(value, self.base_time_unit, self.calendar)


    def _generate_time_series(self, start, end):
        """
        Generates time series and stores in `self.series`

        :return: None
        """
        start = self._get_as_netcdf_time(start)
        end = self._get_as_netcdf_time(end)

        delta = self._resolve_delta()
        current_time = start

        while current_time <= end:
            self.series.append(current_time)

            # Now increment
            current_time += timedelta(*delta)


    def _generate_time_series_month_delta(self, start, end):
        """

        :param start:
        :param end:
        :return:
        """
        current_time = start

        while current_time <= end:
            self.series.append(self._get_as_netcdf_time(current_time))

            # Now increment
            current_time.month += self.delta.n

            # Cater for 12 months per year
            if current_time.month > 12:
                current_time.year += 1
                current_time.month -= 12


    def _generate_time_series_year_delta(self, start, end):
        """

        :param start:
        :param end:
        :return:
        """
        current_time = start

        while current_time <= end:
            self.series.append(self._get_as_netcdf_time(current_time))

            # Now increment
            current_time.year += self.delta.n


def map_frequency(frequency):
    """

    :param frequency:
    :return:
    """
    mapped_frequency = constants.FREQUENCY_MAPPINGS.get(frequency, None)

    if not mapped_frequency:
        raise Exception("Cannot find a valid frequency mapping for: {}".format(frequency))

    return mapped_frequency