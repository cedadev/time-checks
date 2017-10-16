files=/badc/cmip5/data/cmip5/output1/MOHC/HadGEM2-ES/historical/mon/atmos/Amon/r1i1p1/latest/tas/*
output_dir=/group_workspaces/jasmin/cedaproc/astephen/git/time-checks/test_data/cmip5

for f in $files ; do
    fname=$(basename $f)
    var_id=$(echo $fname | cut -d_ -f1)
    output_file=$output_dir/$fname
    cmd="ncks -d lat,,,100 -d lon,,,100 -v $var_id $fname $output_file"
    $cmd
    echo "Wrote: $output_file"
done

