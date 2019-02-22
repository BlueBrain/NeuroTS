"""TNS utils used by multiple tools"""


class TNSError(Exception):
    '''Raises TNS error'''


def _check(data):
    """Checks if data in dictionary are empty.
    """
    for key, val in data.items():
        if len(val) == 0:
            raise TNSError('Empty distrib for diameter key: {}'.format(key))
