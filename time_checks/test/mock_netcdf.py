"""
mock_netcdf.py
==============

Holds a mock version of the netCDF4 Dataset class for use in tests.
"""


class MockNCDataset(object):

    def __init__(self, fpath):
        self.fpath = fpath
        # self.variables = []
        # self.get_variables_by_attributes = item

    def filepath(self):
        return self.fpath
    #
    # def variables(self):
    #     return self.variables
    #
    # def get_variables_by_attributes(self, item):
    #     return self.item

    # def get_time_variable(self):
    #     return self.var
    #
    # def __getitem__(self, item):
    #     return self.var