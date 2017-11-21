# time-checks: a set of checks for time consistency in netCDF data sets

## Introduction

This package provides a set of checks that can be run on individual
data files or on groups of data files. Each check relates to an aspect
of the time representation within the data set/file.

For example, there is a check to make sure the representation of time
in the file name matches the `time` variable inside the file. Another
check ensures that the time axis across multiple files is contiguous.

## The checks

The full list of checks managed by this package are provided below:

### Single file tests

The single file tests are:

- check_file_name_time_format
  
  Checks that the format of the file name contains two components in the form "start"-"end", separated by "-"
  Checks that the time components matches known regular expressions of the form YYYY[mm[DD[HH[MM]]]] and the "start" 
  and "end" times must have the same the structure.

  Where [] indicated the elements are optional and
  YYYY: is a four digit integer year
  mm: is a two digit integer month
  DD: is a two digit integer day
  HH: is a two digit integer hour
  MM: is a two digit integer minute


- check_file_name_matches_time_var
  Checks that the file name of a dataset (file) matches the time range
  found in the file. The time component in the file name is extracted at
  index The checks are done within the tolerance level specified.
  
  Are the time axis start and end times as given in the filename the same as those given in the file relevant 
  to a given tolerance. For example *daily* file with a start date given as 18500101 should have a datetime 
  element of `<1850-01-01: 00:00:00>`, however a *monthly* file withe the start time element 18500101 may have 
  a time stamp in the file at the mid month point e.g. `<1850-01-15: 00:00:00>`, therefore a tolerance can be 
  specified for this check.    


- check_time_format_matches_frequency
    Checks for consistenty between the time frequency and the format of the time.
    cmor_table = "yr", "Oyr": yearly data of the form: yyyy, test has length 4
    cmor_table = "Amon", "Lmon", "Omon", "LImon", "OImon", "cfMon": monthly data of the form: yyyyMM, test has length 6
    cmor_table = "monClim": monthly climatology data of the form: yyyyMM, test has length 6
    cmor_table = "day", "cfDay": daily data of the form: yyyyMMdd, test has length 8
    cmor_table = "6hrLev", "6hrPLev": 6 hourly data of the form: yyyyMMddhh, test has length 10
    cmor_table = "3hr", "": 3 hourly data of the form: yyyyMMddhhmm, test has length 12
    cmor_table = "subhr": sub-hourly data of the form: yyyyMMddhhmm, test has length 12
    NOT IMPLEMENTED YET: 'aero': 0,'cfOff': 0, 'cfSites': 0, 'fx': 0
    

- check_valid_temporal_element
    Checks whether the temporal elements are within the valid ranges:
    years, yyyy: a four digit integer > 0000 
    months, MM: a two digit integer between 01 and 12
    days, dd: a two digit integer between 01-31
    hours, hh: a two digit integer between 00-23
    minutes, mm: a two digit integer between 00-59
    
 - check_regular_time_axis_increments
    Checks that the given time axis increments for a given file are regularly spaced throughout the time series.
    Since it is common to have the timestamp of monthly data placed at the middle of month,
    monthly CMIP5 maybe irregularly spaced when using any of the following calendars:
        'gregorian', 'proleptic_gregorian', 'julian', 'noleap', '365_day', 'standard',
    For these calendars valid time axis increments are 29.5, 30.5 and 31 days.
    For most other frequencies in CMIP5 the time increments should be regular.


### Running the time checks on your data using run_file_timechecks.py

`run_file_timechecks.py` is a wrapper to file_time_checks.py which takes 1:n `.nc` files and then
calls the time checks in given order.

1. Check the format of the filename is correct
2. Check that the file name temporal elements are valid
3. Check that the frequency in the name matches the frequency in the file
4. Check that the temporal elements in the filename match the time range found in the file.
5. Check that the time axis increments are regularly spaced

Error codes are as follows:
T1.000: [file_extension]
T1.001: [check_file_name_time_format]
T1.002: [check_valid_temporal_element]
T1.003: [time_format_matches_frequency]
T1.004: [file_name_matches_time_var]
T1.005: [regular_time_axis_increments]

### Aggregation over multi-file timeseries data

Given a variable level dataset (i.e. a directory of a timeseries
Continutity - a: Are there any identified gaps in the timeseries	For each "end" the following "start" is the next timestep in the series depending on the temporal resolution 	Check against filename only	Or timestamp?
Continutity - b: Are there any identified overlaps in the timeseries	For each "end" the following "start" is the next timestep in the series depending on the temporal resolution 	Check against filename only	Or timestamp?
Completeness: start to end is continuous
Completeness: For a given experiment is the timeseries complete, i.e for a list of files there are no gaps or overlaps between files 


## Support for calendars

The library currently supports all the calendars supported by the netcdftime library. 
It therefore supports all the CMIP calendars. 

It will only support AD times and will not support any time dated BC. 


## Installation

The package is managed in a GitHub repository here:

 https://github.com/cedadev/time-checks

To install the package and its dependencies:

```
git clone https://github.com/cedadev/time-checks
cd time-checks
virtualenv venv
echo ". venv/bin/activate" > setup_env.sh
echo "export PYTHONPATH=." >> setup_env.sh

. setup_env.sh
python setup.py install
```

A beta release of this code is also available 

```
wget https://github.com/cedadev/time-checks/archive/time_check_0-6.tar.gz
pip install time_check_0-6.tar.gz
```
Note however that this code is still under active development as of Nov 2017,
new releases in the near future are anticipated.

#### Running the unit tests
To run all tests:

```
py.test [-v] [-k]
```
Use the `-v verbose` option to get full details of all the tests. 
Use the `-k specific test` option to run just one test called by name. 





