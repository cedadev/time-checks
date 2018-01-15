#!/bin/bash

# Define all collections of files to copy to "small" local files

Amon_files=/badc/cmip5/data/cmip5/output1/MOHC/HadGEM2-ES/historical/mon/atmos/Amon/r1i1p1/latest/tas/tas*.nc
day_files=/badc/cmip5/data/cmip5/output1/IPSL/IPSL-CM5A-LR/historical/day/atmos/day/r1i1p1/v20110915/ua/ua*.nc
yr_files=/badc/cmip5/data/cmip5/output1/MOHC/HadGEM2-CC/piControl/yr/ocnBgchem/Oyr/r1i1p1/v20111109/o2/o2*.nc
_6hr_files=/badc/cmip5/data/cmip5/output1/MOHC/HadGEM2-ES/rcp85/6hr/atmos/6hrPlev/r1i1p1/v20111002/psl/psl_6hrPlev_HadGEM2-ES_rcp85_r1i1p1_20????????-??????????.nc
TypeError_files=/badc/cmip5/data/cmip5/output1/CMCC/CMCC-CM/piControl/day/atmos/day/r1i1p1/v20120330/tas/tas_*.nc
ValueError_files=/badc/cmip5/data/cmip5/output1/CSIRO-BOM/ACCESS1-3/piControl/mon/atmos/Amon/r1i1p1/v1/tas/tas_*.nc

output_dir=/home/users/rpetrie/cp4cds/time-checks/test_data/cmip5_ValueError

# Define files variable as the files to convert this time
files=$ValueError_files

for f in $files ; do
    fname=$(basename $f)
    var_id=$(echo $fname | cut -d_ -f1)
    output_file=$output_dir/$fname

    # Add extra args for some cases
    if [[ $fname =~ "piControl" ]]; then
        extra=""
    elif [[ $fname =~ "day" ]]; then
        extra="-d plev,,,8"
    else
        extra=""
    fi

    echo $var_id
    cmd="ncks $extra -d lat,,,100 -d lon,,,100 -v $var_id $f $output_file"
    echo "Running: $cmd"
    $cmd
    echo "Wrote: $output_file"
done

