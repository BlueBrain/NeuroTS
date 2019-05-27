import shutil
import tempfile
from contextlib import contextmanager

@contextmanager
def setup_tempdir(prefix, cleanup=True):
    temp_dir = tempfile.mkdtemp(prefix=prefix)
    try:
        yield temp_dir
    finally:
        if cleanup:
            shutil.rmtree(temp_dir)
