
import os
import re
from datetime import datetime, timedelta, date
from functools import wraps

import cf_units
from netCDF4 import Dataset, num2date

from time_checks import time_utils, constants



def resolve_dataset_type(func):
    """
    Decorator to resolve the dataset type to a standard dictionary format.

    The decorator function analyses type of dataset (ds)
        - a netCDF4 Dataset
        - a MockNCDataset - used in testing only
        - a compliant dictionary in the form used by this class
          and used to interface with CEDA-CC

    It converts all to a dictionary in a standard format used by the checks.

    :param ds: a dataset object [type analysed here]
    :return: ds [dictionary]
    """

    @wraps(func)
    def wrapper(datasets, **kwargs):
        # First argument can be a list/tuple of objects of a single one.
        # So convert all to a list
        single_arg = False
        if type(datasets) not in (tuple, list):
            single_arg = True
            datasets = [datasets]

        # Loop through all and convert them
        converted_datasets = []

        for ds in datasets:
            if isinstance(ds, Dataset):
                ds = _convert_dataset_to_dict(ds)
            elif hasattr(ds, 'filepath'):
                # If it is a MockDataset, only set the 'filename'
                ds = {"filename": os.path.splitext(os.path.basename(ds.filepath()))[0].split("_")}
            elif isinstance(ds, dict):
                pass
            else:
                raise Exception("Unsupported data type. "
                                "Data types supported are netCDF4 objects or CEDA-CC compliant dictionary objects")

            converted_datasets.append(ds)

        if single_arg:
            return func(converted_datasets[0], **kwargs)
        else:
            return func(converted_datasets, **kwargs)
    
    return wrapper


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


def _resolve_special_date(time_comp, units, calendar):
    """
    Function to manage a set of "special" date/times that cause
    errors/problems with the NetCDF libraries (sometimes for
    valid reasons). Code to resolve those date/times is also
    included so that we can work with them in this library.

    For example: 1st March 300 is anomalous due to changes in
    calendars used historically (e.g. "proleptic_gregorian",
    "gregorian" etc). As a result the NetCDF libraries fail
    to manage this date properly when we call `get_nc_datetime`
    to generate it. However, we can be clever and generate it
    by creating the `datetime` 1 day before and then subtracting
    the timedelta of 1 day.

    :param time_comp: time value [integer]
    :param units: time units [string]
    :param calendar: calendar [string]
    :return: a netcdftime/datetime object.
    """
    _SPECIAL_DATES = [date(300, 3, 1)]

    # Simple function to match dates by attributes
    def _dates_are_equal(d1, d2):
        for key in ('year', 'month', 'day'):
            if getattr(d1, key) != getattr(d2, key):
                return False

        return True

    # subtract 1 day from time_comp and try to generate datetime
    # then add 1 day on
    time_unit = units.split()[0]
    unit_map = {'days': 1, 'hours': 24, 'minutes': 3600, 'seconds': 86400}

    if time_unit not in unit_map:
        raise Exception("Time unit not recognised: {}".format(time_unit))

    time_comp -= unit_map[time_unit]

    # Now use day before to try to generate valid datetime
    day_before = cf_units.num2date(time_comp, units, calendar)

    # And add a day
    t = day_before + timedelta(1)

    # Now check this is a special date and return if it is
    for _date in _SPECIAL_DATES:
        if _dates_are_equal(_date, t):
            return t

    raise Exception("Cannot resolve date.")


def get_nc_datetime(time_comp, units, calendar):
    """
    Returns a time object from netcdftime library. Type can be a number of date time
    objects reflecting the calendar specified.

    :param time_comp: time value [integer]
    :param units: time units [string]
    :param calendar: calendar [string]
    :return: a netcdftime/datetime object.
    """
    err_msg = "Cannot resolve date/time from: {} {} (calendar: {}).".format(
                time_comp, units, calendar)

    try:
        t = cf_units.num2date(time_comp, units, calendar)
    except ValueError, err:
        if err.message == 'day is out of range for month':
            try:
                t = _resolve_special_date(time_comp, units, calendar)
            except:
                raise Exception(err_msg)
        else:
            raise Exception(err_msg)

    return t


def _times_match_within_tolerance(t1, t2, tolerance="days:1"):
    """
    Compares two datetime datetime/netcdf_time objects and returns True if they match
    within the time period specified in `tolerance`.

    Usually t1 is the start time as taken from the file
    Usually t2 is the start time as given by the filename

    :param t1: datetime/netcdf_time object
    :param t2: datetime/netcdf_time object
    :param tolerance: tolerance period [string]
    :return: boolean [True for success]
    """
    return_msg = ""
    unit = tolerance.split(":")[0]
    n = float(tolerance.split(":")[1])
    delta = timedelta(**{unit: n})

    if t1 == t2:
        return True, return_msg

    # If time series starts on 0001-01-01 then subtracting the timedelta causes error as time goes BC 
    # Arrow only supprts AD times, therefore only check that the time in the filename is less than
    # time in the file with the given tolerance.
    if hasattr(t1, 'calendar'):
        close_to_zero_AD = cf_units.num2date(17, "days since 0000-00-00 00:00:00", t1.calendar)
    else:
        close_to_zero_AD = datetime(1, 1, 17)

    if t2 < close_to_zero_AD:

        if t2 < (t1 + delta):
            return_msg = "Time close to zero"
            return True, return_msg
     
    if (t1 - delta) < t2 < (t1 + delta):
        return True, return_msg

    return False, return_msg


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

    def __eq__(self, other):
        this, other = self._components, other._components
        return this == other

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


def time_object_to_anytime(dt):
    """
    Converts any date/time object that has attributes of 'year', 'month', ...
    ..., 'second' to a DateTimeAnyTime object. Input times might be those from
    the netcdftime library or a simple datetime.

    :param dt: some kind of date/time object
    :return: a DateTimeAnyTime instance
    """
    keys = ('year', 'month', 'day', 'hour', 'minute', 'second')
    return DateTimeAnyTime(*[getattr(dt, key) for key in keys])


def safe_datetime_comparison(dt1, comparison, dt2):
    """
    Casts both date/time objects to DateTimeAnyTime instances so that comparisons
    will work.

    :param dt1: some kind of date/time object
    :param comparison: string for comparison, one of "<", "<=", "==", ">", ">="
    :param dt2: some kind of date/time object
    :return: boolean
    """
    comp_string = "dt1 {} dt2".format(comparison)

    # Try run it normally, but proceed if Exception raised
    try:
        return eval(comp_string)
    except Exception:
        pass

    adt1 = time_object_to_anytime(dt1)
    adt2 = time_object_to_anytime(dt2)

    comp_string = "adt1 {} adt2".format(comparison)
    return eval(comp_string)


def compare(dt1, comparison, dt2):
    """
    Alias to safe_datetime_comparison.

    :param dt1: some kind of date/time object
    :param comparison: string for comparison, one of "<", "<=", "==", ">", ">="
    :param dt2: some kind of date/time object
    :return: boolean
    """
    return safe_datetime_comparison(dt1, comparison, dt2)

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


def anytime_to_netcdf_time(anytime, time_unit, calendar):
    """
    Converts the incoming DateTime/DateTimeAnyTime into a netCDF time object.
    The base time unit and calendar set on the object are used.

    :param anytime: an instance of DateTimeAnyTime or DateTime
    :param time_unit: time units (string)
    :param calendar: calendar (string)
    :return: netCDF Time object (aware of calendars)
    """
    value = cf_units.date2num(anytime, time_unit, calendar)
    return get_nc_datetime(value, time_unit, calendar)


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
    FREQUENCY_MAPPINGS = {'mon': 'month',
                          'yr': 'year'}


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


    def _before_or_equal_to_wrapper(self, t1, t2):
        """
        Wrapper script to catch Exceptions when two datetime objects are compared
        with `t1 <= t2`. Some time series will generate different datetime
        objects which raise an Exception such as:
            "TypeError: cannot compare netcdftime._netcdftime.Datetime ..."

        This code catches the Exception and does a comparison of each component
        rather than the entire object.

        Return True if t1 is before or equal to t2.

        :param t1: a netcdftime or datetime object
        :param t2: a netcdftime or datetime object
        :return: boolean
        """
        return compare(t1, "<=", t2)


    def _generate_time_series(self, start, end):
        """
        Generates time series and stores in `self.series`

        :return: None
        """
        start = anytime_to_netcdf_time(start, self.base_time_unit, self.calendar)
        end = anytime_to_netcdf_time(end, self.base_time_unit, self.calendar)

        delta = self._resolve_delta()
        current_time = start

        while self._before_or_equal_to_wrapper(current_time, end): # current_time <= end:
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
            self.series.append(anytime_to_netcdf_time(current_time, self.base_time_unit, self.calendar))

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
            self.series.append(anytime_to_netcdf_time(current_time, self.base_time_unit, self.calendar))

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


def calculate_delta_time_series(times, valid_dt):
    """
       calculate_delta_time_series

    This function calculates the differences between all the elements of a timeseries and
    compares the differences with a valid time difference.

    True is returned if all the differences are valid; i.e. equal to the valid time difference argument
    False is returned if any of the difference fail to match the valid the time difference argument

    :param times: List of times
    :param valid_dt: Valid time difference, usually scalar, list of valid times supported
    :return: boolean [True for success]
    """
    return_msg = ""
    for t in range(len(times)-1):
        t_diff = times[t+1] - times[t]
        if t_diff not in valid_dt:
            return_msg = "Time difference {} is irregular or not in allowed values {}".format(t_diff, valid_dt)
            return False, return_msg

    return True, return_msg
