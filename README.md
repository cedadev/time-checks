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
 - The temporal subset must contain two components in the form "start"-"end", separated by "-"
 - The structure of "start" and "end" must be of the form yyyy[MM[dd[hh[mm]]]]
 - "start" and "end" must have the same the structure
 - variable_table = "fx": time independent data will not have a temporal element
 - variable_table = "yr": yearly data of the form: yyyy
 - variable_table = "mon": monthly data of the form: yyyyMM
 - variable_table = "monClim": monthly climatology data of the form: yyyyMM
 - variable_table = "day": daily data of the form: yyyyMMdd
 - variable_table = "6hr": 6 hourly data of the form: yyyyMMddhh
 - variable_table = "3hr": 3 hourly data of the form: yyyyMMddhhmm
 - variable_table = "subhr": sub-hourly data of the form: yyyyMMddhhmm

Is the time axis start time consistent with the "start" time as given in the filename (tolerance?)	tolerance 1 timestep	calendar conversion required	Calendars in the CP4CDS CMIP5 data: `julian`, `noleap`, `365_day`, `standard`, `gregorian`, `proleptic_gregorian`, `360_day`.

Is the time axis end time consistent with the "end" as given in the filename (tolerance?)	tolerance 1 timestep	calendar conversion required
Time axis increments are regular	monthly timeseries 28-31 days

```
yyyy is an integer greater than [18-29]00	Could just be >0000
MM is an integer between 01-12
dd is an integer between 01-31
hh is an integer between 00-23
mm is an integer between 00-59
```

### Aggregation over multi-file timeseries data

Given a variable level dataset (i.e. a directory of a timeseries
Continutity - a: Are there any identified gaps in the timeseries	For each "end" the following "start" is the next timestep in the series depending on the temporal resolution 	Check against filename only	Or timestamp?
Continutity - b: Are there any identified overlaps in the timeseries	For each "end" the following "start" is the next timestep in the series depending on the temporal resolution 	Check against filename only	Or timestamp?
Completeness: start to end is continuous
Completeness: For a given experiment is the timeseries complete (given the CMIP5 requirements below)

```
Short Name of Experiment 	 Experiment Name	Temporal constraints	Years requested per run
piControl	pre-industrial control		>= 500
historical	historical 	1850-2005	156
rcp45	RCP4.5	2006-2300	295
rcp85	RCP8.5	2006-2300	295
rcp26	RCP2.6	2006-2300	295
rcp60	RCP6.0	2006-2100	94
```

## Support for calendars

The library currently supports two calendars:
 - standard
 - 360-day

Support can be added for other calendars as required.

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

To run tests:

```
py.test
```





