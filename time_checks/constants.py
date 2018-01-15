
import re

# File name regular expressions for different time component patterns
DT_LENGTHS = ['4', '6', '8', '10', '12', '14']

FILE_NAME_PATTERNS_SINGLE = [r'^\d{{{}}}$'.format(dtl) for dtl in DT_LENGTHS]
FILE_NAME_PATTERNS_DOUBLE = [r'^\d{{{}}}-\d{{{}}}$'.format(dtl, dtl) for dtl in DT_LENGTHS]
FILE_NAME_REGEXES = [re.compile(pattn) for pattn in (FILE_NAME_PATTERNS_SINGLE
                                                     + FILE_NAME_PATTERNS_DOUBLE)]
CMOR_TABLES_FORMAT = {'3hr': 12, '6hrLev': 10, '6hrPLev': 10, 'Amon': 6, 'LImon': 6, 'Lmon': 6, 'OImon': 6,
                      'Omon': 6, 'Oyr': 4, 'aero': 0, 'cf3hr': 12, 'cfDay': 8, 'cfMon': 6, 'cfOff': 0, 'cfSites': 0,
                      'day': 8, 'fx': 0}
IRREGULAR_MONTHLY_CALENDARS = ['gregorian', 'proleptic_gregorian', 'julian', 'noleap', '365_day', 'standard']
VALID_MONTHLY_TIME_DIFFERENCES = [29.5, 30.5, 30.0, 31.0]

FREQUENCY_MAPPINGS = {
    '3hr': (0.125, 'day'),
    '6hrLev': (0.25, 'day'),
    '6hrPlev': (0.25, 'day'),
    'Amon': (1, 'month'),
    'LImon': (1, 'month'),
    'Lmon': (1, 'month'),
    'OImon': (1, 'month'),
    'Omon': (1, 'month'),
    'Oyr': (1, 'year'),
    'aero': (1, 'month'), # aero only has monthly data
    'cf3hr': (3, 'hour'),
    'cfDay': (1, 'day'),
    'cfMon': (1, 'month'),
    'cfOff': None,
    'cfSites': None,
    'day': (1, 'day'),
    'fx': None
}