"""
run_file_timechecks.py
======================

A wrapper to file_time_checks.py which takes 1:n .nc files and then
calls the time checks in given order.

If the output is in False an error message is reported

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

"""
import os
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


def test_filename_extension(file):

    if not file.endswith('.nc'):
        return "T1.000: [file_extension]: File does not end with '.nc'"
    else:
        return "T1.000: [file_extension]: OK"


@resolve_dataset_type
def test_check_file_name_time_format(ds):

    res, msg = check_file_name_time_format(ds)
    if res == False:
        return "T1.001: [check_file_name_time_format]: FAILED:: Format of file name is not recognised. " + msg
    else:
       return "T1.001: [check_file_name_time_format]: OK"


@resolve_dataset_type
def test_check_valid_temporal_element(ds):

    res, msg = check_valid_temporal_element(ds, time_index_in_name=-1)
    if res == False:
        return "T1.002: [check_valid_temporal_element]: FAILED:: Temporal elements are not valid. " + msg
    else:
        return "T1.002: [check_valid_temporal_element]: OK"


@resolve_dataset_type
def test_check_time_format_matches_frequency(ds):

    res, msg = check_time_format_matches_frequency(ds, frequency_index=1, time_index_in_name=-1)
    if res == False:
        return "T1.003: [time_format_matches_frequency]: FAILED:: " \
               "Frequency element of the filename does not match frequency of data in the file. " + msg
    else:
        return "T1.003: [time_format_matches_frequency]: OK"


@resolve_dataset_type
def test_check_file_name_matches_time_var(ds):

    table = ds["filename"][1]
    if table in ['Oyr']:
        frequency = 'days'
        limit = 180
    if table in ['Amon', 'Omon', 'Lmon', 'LImon', 'OImon', 'cfMon', 'aero']:
        frequency = 'days'
        limit = 16
    if table in ['day', 'cfday', 'cfDay']:
        frequency = 'days'
        limit = 1
    if table in ['6hrLev', '6hrPlev', '3hr', 'cf3hr']:
        frequency = 'hours'
        limit = 1

    tolerance = "{}:{}".format(frequency, limit)

    res, msg = check_file_name_matches_time_var(ds, time_index_in_name=-1, tolerance=tolerance)
    if res == False:
        return "T1.004: [file_name_matches_time_var]: FAILED:: " \
               "Frequency element of the filename does not match time format in file. " + msg
    else:
        return "T1.004: [file_name_matches_time_var]: OK"


@resolve_dataset_type
def test_check_regular_time_axis_increments(ds):
    res, msg = check_regular_time_axis_increments(ds, frequency_index=1)
    if res == False:
        return "T1.005: [regular_time_axis_increments]: FAILED:: Time axis increments are not regular. " + msg
    else:
        return "T1.005: [regular_time_axis_increments]: OK"


def main(ifile, odir):
    """
     main() calls all the functions within this script

     Input arguments are
     1 - a NetCDF file with a '.nc' extension
     2 - output directory
     :return: file with name of input file in the specified output directory
     """
    is_file = os.path.isfile(ifile)

    if not os.path.isdir(odir):
        os.makedirs(odir)

    ncfile = os.path.basename(ifile)
    ofile = os.path.join(odir, ncfile.replace('.nc', '__file_timecheck.log'))

    with open(ofile, 'w+') as w:
        w.writelines(["Time checks of: {} \n".format(ifile)])
        if not is_file:
            w.writelines(["FATAL {} does not exist in the CEDA archive \n".format(ifile)])
        else:
            ds = Dataset(ifile)
            tests = [test_filename_extension(ifile),
                     test_check_file_name_time_format(ds),
                     test_check_valid_temporal_element(ds),
                     test_check_time_format_matches_frequency(ds),
                     test_check_file_name_matches_time_var(ds),
                     test_check_regular_time_axis_increments(ds)
                     ]
            for test in tests:
                res = test
                w.writelines([res, '\n'])


if __name__ == '__main__':

    ifile = argv[1]
    # Set default odir to be local dir
    odir = "."

    if len(argv) > 2:
        odir = argv[2]

    main(ifile, odir)
