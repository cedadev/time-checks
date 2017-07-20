"""
time_utils.py
=============

Utilities for working with time.

"""


def get_main_variable(ds):
    """
    Returns biggest variable in netCDF4 Dataset.

    :param ds: netCDF4 Dataset object
    :return: netCDF4 Variable object
    """
    dsv = ds.variables
    sizes = [(dsv[ncvar].size, dsv[ncvar]) for ncvar in dsv]
    sizes.sort()

    return sizes[-1][1]


def get_time_variable(ds):
    '''
    Returns the likeliest variable to be the time coordiante variable

    :param netCDF4.Dataset ds: An open netCDF4 Dataset
    :return: the time variable 
    '''
    for var in ds.variables:
        if getattr(ds.variables[var], 'axis', '') == 'T':
            return ds.variables[var]
    else:
        candidates = ds.get_variables_by_attributes(standard_name='time')

        if len(candidates) == 1:
            return candidates[0]
        else:  # Look for a coordinate variable time

            for candidate in candidates:
                if candidate.dimensions == (candidate.name,):
                    return candidate

    # Now look at main variable and try that
    main_var = get_main_variable(ds)
    
    for dimension in main_var.dimensions:
        if dimension == 'time':
            return ds.variables['time'] 
 
    # Not found
    return None
