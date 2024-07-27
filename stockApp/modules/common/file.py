import os
import shutil
import tempfile
import contextlib
from typing import Optional, Text, IO, Union
from pathlib import Path
from core.log.logger import get_module_logger

log = get_module_logger("modules.common.file")


def get_or_create_path(path: Optional[Text] = None, return_dir: bool = False):
    """Create or get a file or directory given the path and return_dir.

    Parameters
    ----------
    path: a string indicates the path or None indicates creating a temporary path.
    return_dir: if True, create and return a directory; otherwise c&r a file.

    """
    if path:
        if return_dir and not os.path.exists(path):
            os.makedirs(path)
        elif not return_dir:  # return a file, thus we need to create its parent directory
            xpath = os.path.abspath(os.path.join(path, ".."))
            if not os.path.exists(xpath):
                os.makedirs(xpath)
    else:
        temp_dir = os.path.expanduser("~/tmp")
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
        if return_dir:
            _, path = tempfile.mkdtemp(dir=temp_dir)
        else:
            _, path = tempfile.mkstemp(dir=temp_dir)
    return path