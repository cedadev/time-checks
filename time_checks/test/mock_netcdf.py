"""
mock_netcdf.py
==============

Holds a mock version of the netCDF4 Dataset class for use in tests.
"""


class MockNCDataset(object):

    def __init__(self, fpath):
        self.fpath = fpath

    def filepath(self):
        return self.fpath

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.fpath
