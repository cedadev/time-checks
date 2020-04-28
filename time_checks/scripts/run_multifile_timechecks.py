"""
run_file_timechecks.py
==================

A wrapper to multifile_time_checks.py which takes 1:n .nc files and then
calls the time checks in given order.

Checks whether the timeseries of datafiles is complete and contiguous.

Returns message of [check_multifile_temporal_continuity]: OK/FAILED
"""

import os
from sys import argv
from netCDF4 import Dataset, num2date

from time_checks import utils, constants
from time_checks.utils import resolve_dataset_type
from time_checks import utils, time_utils, settings, constants
from time_checks.multifile_time_checks import check_multifile_temporal_continuity

 
@resolve_dataset_type
def test_check_multifile_temporal_continuity(files):

    res, msg = check_multifile_temporal_continuity(files)

    if res == False:
        return "T1.006: [check_multifile_temporal_continuity]: FAILED:: " + msg
    else:
        return "T1.006: [check_multifile_temporal_continuity]: OK"


def main(ifiles, odir):

    institute, model, experiment, frequency, realm, table, ensemble, version, variable, ncfile = ifiles[0].split('/')[6:]
    logdir = os.path.join(odir, institute, model, experiment, frequency, realm, version)
    logfile = os.path.join(logdir, ncfile.replace('.nc', '__multifile_timecheck.log'))

    if not os.path.isdir(logdir):
        os.makedirs(logdir)
 
    dataset = []
    for f in ifiles:
        try:
            dataset.append(Dataset(f))
        except IOError as err:
            with open(logfile, 'w+') as w:
                w.writelines(["Error could not perform multifile timechecks", '\n'])
                w.writelines(['File: ', f,  '\n'])
                w.writelines(["Has IOError, ({})".format(str(err)), '\n'])
            return

    res = test_check_multifile_temporal_continuity(dataset)

    with open(logfile, 'w+') as w:
        w.writelines([res, '\n'])
        w.writelines([' ', '\n'])
        w.writelines(["Multifile time check on files:", '\n'])
        for f in ifiles:
            w.writelines([f, '\n'])


if __name__ == '__main__':

    ifiles = argv[1:]
    main(ifiles, odir='./')
