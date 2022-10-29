# -*- coding: utf-8 -*-

"""
Copyright (c) 2022 Yuriy Kuntsyak (https://yuriyk.dev)

This code is licensed under MIT license (see LICENSE for details)
"""

import logging
from subprocess import PIPE, Popen

logging.basicConfig(level=logging.DEBUG)

from .constants import MAGICK_EXEC_PATH

def get_img_metadata(path: str) -> str:
    logging.debug(f"Starting work on {path}")

    proc = Popen(
        [MAGICK_EXEC_PATH, "identify", "-verbose", f"{path}"],
        stdout=PIPE,
        stderr=PIPE,
        universal_newlines=True,
    )

    stdout, stderr = proc.communicate()

    if proc.returncode != 0 or stderr:
        raise Exception(stderr)

    return stdout
