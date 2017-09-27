"""
time_series_generator.py
========================

Holds TimeSeriesGenerator class to generate time series values
based on a set of inputs.

"""

from datetime import datetime
from calendar import monthrange


class SimpleDate(object):
    """
    Simple container class for a date.
    """

    def __init__(self, year, month, day):
        """
        Constructor: sets the instance properties and aliases.

        :param self: the instance
        :param year: year [integer]
        :param month: month [integer]
        :param day: day [integer]
        """
        self.year = self.y = year
        self.month = self.m = month
        self.day = self.d = day

    def __repr__(self):
        return "{:4d}-{:02d}-{:02d}".format(self.y, self.m, self.d)

    def as_list(self):
        """
        Return as 3-member list of integers.

        :return: list of integers ([year, month, day]).
        """
        return [self.y, self.m, self.d]

    def as_datetime(self):
        """

        :return:
        """
        return datetime(self.y, self.m, self.d)

    def as_string(self):
        """

        :return:
        """
        return "{:04}-{:02}-{:02}T00:00:00".format(self.y, self.m, self.d)

    def as_format(self, format):
        """

        :param format:
        :return:
        """
        return getattr(self, "as_{}".format(format))()

    def __gt__(self, other):
        this, other = self.as_list(), other.as_list()
        return this > other

    def __lt__(self, other):
        this, other = self.as_list(), other.as_list()
        return this < other

    def __ge__(self, other):
        this, other = self.as_list(), other.as_list()
        return this >= other

    def __le__(self, other):
        this, other = self.as_list(), other.as_list()
        return this <= other



class TimeSeriesGenerator(object):

    SUPPORTED_FREQUENCIES = ['day', 'mon', 'month']
    SUPPORTED_CALENDARS = ['gregorian', 'standard', '360_day']
    SUPPORTED_FORMATS = ['list', 'datetime', 'string']
    FREQUENCY_MAPPINGS = {'mon': 'month'}

    def __init__(self, start, end, delta=(1, 'day'), calendar='360_day', format='list'):
        """

        :param start:
        :param end:
        :param delta:
        :param calendar:
        :param format:
        """
        self.start = self._validate_datetime(start)
        self.end = self._validate_datetime(end)
        self._set_delta(delta)
        self._set_calendar(calendar)
        self.set_format(format)

        # Set up starting points for iterator
        self.current_time = self.start
        self.current_counter = 0

    def __iter__(self):
        return self

    def __next__(self):
        """
        Generator yielding next datetime for 360day calendar.

        :return: tuples of (time value (since reference time), datetime)
        """
        delta_n, unit = self.delta
#
        if self.current_time <= self.end:
            time_value = self.current_time.as_format(self.format)
            value = self.current_counter

            # Now increment before returning
            self.current_counter += delta_n
            for i in range(delta_n):
                getattr(self, "_add_{}".format(unit))(self.current_time)

            return (value, time_value)

        raise StopIteration

    def _validate_datetime(self, dt):
        """

        :param dt:
        :return:
        """
        return SimpleDate(*dt)

    def _set_delta(self, delta):
        """

        :param delta:
        :return:
        """
        if not delta[1] in self.SUPPORTED_FREQUENCIES:
            raise Exception("Delta uses time frequency '{}' that is not yet supported.".format(delta[1]))

        if delta[1] in self.FREQUENCY_MAPPINGS:
            delta = (delta[0], self.FREQUENCY_MAPPINGS[delta[1]])

        self.delta = delta

    def _set_calendar(self, calendar):
        """

        :param calendar:
        :return:
        """
        if not calendar in self.SUPPORTED_CALENDARS:
            raise Exception("Unrecognised calendar: '{}'".format(calendar))

        self.calendar = calendar

    def set_format(self, format):
        """
        Updates the internal `self.format` attribute used to decide which format the
        generator returns its responses as.

        :param format: format to return values [string]
        :return: None
        """
        if format not in self.SUPPORTED_FORMATS:
            raise Exception("Unrecognised format '{}' selected for returning time values.".format(format))

        self.format = format

    def next(self):
        return self.__next__()


    def _add_year(self, dt):
        dt.y += 1

    def _add_month(self, dt):
        if dt.m < 12:
            dt.m += 1
        else:
            dt.m = 1
            self._add_year(dt)

    def _add_day(self, dt):
        if self.calendar == "360_day":
            limit = 30
        elif self.calendar in ("standard", "gregorian"):
            limit = monthrange(dt.y, dt.m)[1]

        if dt.d < limit:
            dt.d += 1
        else:
            dt.d = 1
            self._add_month(dt)

