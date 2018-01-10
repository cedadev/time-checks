"""
run_file_timechecks.py
==================

A wrapper to multifile_time_checks.py which takes 1:n .nc files and then
calls the time checks in given order.

Checks whether the timeseries of datafiles is complete and contiguous.

Returns message of [check_multifile_temporal_continuity]: OK/FAILED
"""
import os
import arrow
from sys import argv
from netCDF4 import Dataset, num2date

from time_checks import utils, constants
from time_checks.utils import resolve_dataset_type
from time_checks import utils, time_utils, settings, constants
from time_checks.multifile_time_checks import check_multifile_temporal_continuity


# python run_multifile_timechecks.py ../test_data/cmip5/ua_day_IPSL-CM5A-LR_historical_r1i1p1_19500101-19591231.nc  ../test_data/cmip5/ua_day_IPSL-CM5A-LR_historical_r1i1p1_19800101-19891231.nc ../test_data/cmip5/ua_day_IPSL-CM5A-LR_historical_r1i1p1_19600101-19691231.nc  ../test_data/cmip5/ua_day_IPSL-CM5A-LR_historical_r1i1p1_19900101-19991231.nc ../test_data/cmip5/ua_day_IPSL-CM5A-LR_historical_r1i1p1_19700101-19791231.nc  ../test_data/cmip5/ua_day_IPSL-CM5A-LR_historical_r1i1p1_20000101-20051231.nc


@resolve_dataset_type
def test_check_multifile_temporal_continuity(files):

    res, msg = check_multifile_temporal_continuity(files)

    if res == False:
        return "T1.006: [check_multifile_temporal_continuity]: FAILED:: " + msg
    else:
        return "T1.006: [check_multifile_temporal_continuity]: OK"



def is_part_of_timeseries(ifile):
    
    msg = ""
    if os.path.isdir(os.path.dirname(ifile)):

        if len(os.listdir(os.path.dirname(ifile))) > 1:
            ts = True
        else:
            ts = False
            msg = "Single file in timeseries or fx"
    else:
        ts = False
        msg = "Path error"
        
    return ts, msg

def main(ifiles, odir='.'):

    ifiles = [ifiles]
    import pdb


    if len(ifiles) == 1:
        fname = ifiles[0]
        ts, msg = is_part_of_timeseries(fname)
        if not ts:   
            return "T1.006: [check_multifile_temporal_continuity]: " + msg
        else:
            dirname = os.path.dirname(fname)
            fnames = os.listdir(dirname)
            filenames = []
            for f in fnames:
                filenames.append(os.path.join(dirname, f))

    else :
        filenames = ifiles

    files = []
    for f in filenames:
        files.append(Dataset(f))

    res = test_check_multifile_temporal_continuity(files)
    pdb.set_trace()
    for f in filenames:
        institute, model, experiment, frequency, realm, table, ensemble, version, variable, ncfile = f.split('/')[6:]
        logfile = os.path.join(odir, ncfile.replace('.nc', '__file_timecheck.log'))

        if os.path.isfile(logfile):
            with open(logfile, 'a') as w:
                w.writelines([res, '\n'])

        else:
            if not os.path.isdir(odir):
                os.makedirs(odir)
            with open(logfile, 'w+') as w:
                w.writelines([res, '\n'])


if __name__ == '__main__':

    ifiles = argv[1:]
    main(ifiles, odir)