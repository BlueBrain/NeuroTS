"""NeuroTS utils used by multiple tools"""


class NeuroTSError(Exception):
    '''Raises NeuroTS error'''


def _check(data):
    """Checks if data in dictionary are empty.
    """
    for key, val in data.items():
        if len(val) == 0:
            raise NeuroTSError('Empty distrib for diameter key: {}'.format(key))
