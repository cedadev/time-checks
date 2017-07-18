# -*- coding: utf-8 -*-
"""
time_utils.py
=============

Utilities for working with time.
"""

# Some of these are copied directly from:
#  https://github.com/ioos/compliance-checker/blob/master/compliance_checker/cfutil.py


def get_time_variables(ds):
    '''
    Returns a list of variables describing the time coordinate
    :param netCDF4.Dataset ds: An open netCDF4 Dataset
    '''
    time_variables = []
    for variable in ds.get_variables_by_attributes(standard_name='time'):
        time_variables.append(variable.name)

    for variable in ds.get_variables_by_attributes(axis='T'):
        if variable.name not in time_variables:
            time_variables.append(variable.name)

    regx = r'^(?:day|d|hour|hr|h|minute|min|second|s)s? since .*$'
    for variable in ds.get_variables_by_attributes(units=lambda x: isinstance(x, basestring)):
        if re.match(regx, variable.units) and variable.name not in time_variables:
            time_variables.append(variable.name)

    return time_variables


def get_coordinate_variables(ds):
    '''
    Returns a list of variable names that identify as coordinate variables.
    A coordinate variable is a netCDF variable with exactly one dimension. The
    name of this dimension must be equivalent to the variable name.
    From CF §1.2 Terminology
    It is a one-dimensional variable with the same name as its dimension [e.g.,
    time(time) ], and it is defined as a numeric data type with values that are
    ordered monotonically. Missing values are not allowed in coordinate
    variables.
    :param netCDF4.Dataset ds: An open netCDF dataset
    '''
    coord_vars = []
    for dimension in ds.dimensions:
        if dimension in ds.variables:
            if ds.variables[dimension].dimensions == (dimension,):
                coord_vars.append(dimension)
    return coord_vars


def get_auxiliary_coordinate_variables(ds):
    '''
    Returns a list of auxiliary coordinate variables
    An auxiliary coordinate variable is any netCDF variable that contains
    coordinate data, but is not a coordinate variable (in the sense of the term
    defined by CF).
    :param netCDf4.Dataset ds: An open netCDF dataset
    '''
    aux_vars = []
    # get any variables referecned by the coordinates attribute
    for ncvar in ds.get_variables_by_attributes(coordinates=lambda x: isinstance(x, basestring)):
        # split the coordinates into individual variable names
        referenced_variables = ncvar.coordinates.split(' ')
        # if the variable names exist, add them
        for referenced_variable in referenced_variables:
            if referenced_variable in ds.variables and referenced_variable not in aux_vars:
                aux_vars.append(referenced_variable)

    # axis variables are automatically in
    for variable in get_axis_variables(ds):
        if variable not in aux_vars:
            aux_vars.append(variable)

    # Last are any variables that define the common coordinate standard names
    coordinate_standard_names = ['time', 'longitude', 'latitude', 'height', 'depth', 'altitude']
    coordinate_standard_names += DIMENSIONLESS_VERTICAL_COORDINATES

    # Some datasets like ROMS use multiple variables to define coordinates
    for ncvar in ds.get_variables_by_attributes(standard_name=lambda x: x in coordinate_standard_names):
        if ncvar.name not in aux_vars:
            aux_vars.append(ncvar.name)

    # Remove any that are purely coordinate variables
    ret_val = []
    for aux_var in aux_vars:
        if ds.variables[aux_var].dimensions == (aux_var,):
            continue
        ret_val.append(aux_var)

    return ret_val


def get_time_variable(ds):
    '''
    Returns the likeliest variable to be the time coordiante variable
    :param netCDF4.Dataset ds: An open netCDF4 Dataset
    '''
    for var in ds.variables:
        if getattr(ds.variables[var], 'axis', '') == 'T':
            return var
    else:
        candidates = ds.get_variables_by_attributes(standard_name='time')

        if len(candidates) == 1:
            return candidates[0].name
        else:  # Look for a coordinate variable time
            for candidate in candidates:
                if candidate.dimensions == (candidate.name,):
                    return candidate.name

    # If we still haven't found the candidate
    time_variables = set(get_time_variables(ds))
    coordinate_variables = set(get_coordinate_variables(ds))

    if len(time_variables.intersection(coordinate_variables)) == 1:
        return list(time_variables.intersection(coordinate_variables))[0]

    auxiliary_coordinates = set(get_auxiliary_coordinate_variables(ds))
    if len(time_variables.intersection(auxiliary_coordinates)) == 1:
        return list(time_variables.intersection(auxiliary_coordinates))[0]
    return None
