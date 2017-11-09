"""
run_file_timechecks.py
==================

A wrapper to file_time_checks.py which takes 1:n .nc files and then
calls the time checks in given order.

If the output is in False an error message is reported

1. Check the format of the filename is correct
2. Check that the file name temporal elements are valid
3. Check that the frequency in the name matches the frequency in the file
4. Check that the temporal elements in the filename match the time range found in the file.
5. Check that the time axis increments are regularly spaced

"""
import os
import arrow
from sys import argv
from netCDF4 import Dataset, num2date

from time_checks import utils, constants
from time_checks.utils import resolve_dataset_type
from time_checks import utils, time_utils, settings, constants
from time_checks.file_time_checks import check_file_name_time_format
from time_checks.file_time_checks import check_file_name_matches_time_var
from time_checks.file_time_checks import check_time_format_matches_frequency
from time_checks.file_time_checks import check_valid_temporal_element
from time_checks.file_time_checks import check_regular_time_axis_increments


@resolve_dataset_type
def test_check_file_name_time_format(ds):

    if check_file_name_time_format(ds) == False:
        return "T1.001: [check_file_name_time_format]: FAILED:: Format of file name is not recognised"
    else:
       return "T1.001: [check_file_name_time_format]: OK"


@resolve_dataset_type
def test_check_valid_temporal_element(ds):

    if check_valid_temporal_element(ds, time_index_in_name=-1) == False:
        return "T1.002: [check_valid_temporal_element]: FAILED:: Temporal elements are not valid"
    else:
       return "T1.002: [check_valid_temporal_element]: OK"


@resolve_dataset_type
def test_check_time_format_matches_frequency(ds):

    if check_time_format_matches_frequency(ds, frequency_index=1, time_index_in_name=-1) == False:
        return "T1.003: [time_format_matches_frequency]: FAILED:: Frequency element in filename does not match time format in file"
    else:
        return "T1.003: [time_format_matches_frequency]: OK"


@resolve_dataset_type
def test_check_file_name_matches_time_var(ds):


    table = ds["filename"][1]
    if table in ['Amon', 'Omon', 'Lmon', 'LImon', 'OImon', 'cfMon']:
        frequency = 'days'
        limit = 16
    if table in ['day', 'cfday']:
        frequency = 'days'
        limit = 1
    if table in ['6hrLev', '6hrPlev', '3hr']:
        frequency = 'hours'
        limit = 1

    tolerance = "{}:{}".format(frequency, limit)

    if check_file_name_matches_time_var(ds, time_index_in_name=-1, tolerance=tolerance) == False:
        return "T1.004: [file_name_matches_time_var]: FAILED:: Frequency element in filename does not match time format in file"
    else:
        return "T1.004: [file_name_matches_time_var]: OK"


@resolve_dataset_type
def test_check_regular_time_axis_increments(ds):

    if check_regular_time_axis_increments(ds, frequency_index=1) == False:
        return "T1.005: [regular_time_axis_increments]: FAILED:: Time axis increments are not regular"
    else:
        return "T1.005: [regular_time_axis_increments]: OK"


if __name__ == "__main__":


    #ncfile = "/badc/cmip5/data/cmip5/output1/MOHC/HadGEM2-ES/rcp85/mon/atmos/Amon/r1i1p1/files/tas_20110329/tas_Amon_HadGEM2-ES_rcp85_r1i1p1_200512-203011.nc"

    """
    Input arguments are
    1 - file
    2 - output directory
    :return:
    """

    ifile = argv[1]
    odir = argv[2]

    ncfile = os.path.basename(ifile)
    ofile = os.path.join(odir, ncfile.replace('.nc', '__file_timecheck.log'))

    with open(ofile, 'w+') as w:
        w.writelines(["Time checks of: ", ifile, "\n"] )
        if not ifile.endswith('.nc'):
           w.writelines(["T1.000: [file_extension]: File does not end with '.nc'. \n"])
           raise Exception("File does not end with '.nc'. Exiting time checks")
        else:
            w.writelines(["T1.000: [file_extension]: OK \n"])

        ds = Dataset(ifile)

        tests = [test_check_file_name_time_format(ds),
                 test_check_valid_temporal_element(ds),
                 test_check_time_format_matches_frequency(ds),
                 test_check_file_name_matches_time_var(ds),
                 test_check_regular_time_axis_increments(ds)
                ]

        for test in tests:
            res = test
            w.writelines([res, '\n'])
