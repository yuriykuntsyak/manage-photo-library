#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2022 Yuriy Kuntsyak (https://yuriyk.dev)

This code is licensed under MIT license (see LICENSE for details)
"""

import yaml
import logging
import sys

from multiprocessing import Pool
from subprocess import PIPE, Popen
from pathlib import Path

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader


logging.basicConfig(level=logging.DEBUG)

PROC_POOL_SIZE = 4
PROC_CHUNK_SIZE = 1
MAGICK_EXEC_PATH = "/usr/local/bin/magick"


class ImageMetadata(object):
    def __init__(self, **dict_data):
        self.__dict__.update(dict_data)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__dict__})"

    def __hash__(self) -> int:
        return hash(self.critical_image_properties)

    @property
    def image(self) -> dict:
        return self.__dict__.get("Image", {})

    @property
    def image_statistics(self) -> dict:
        return self.image.get("Image statistics", {})

    @property
    def image_properties(self) -> dict:
        return self.image.get("Properties", {})

    @property
    def image_path(self) -> str:
        return self.image.get("Filename")

    @property
    def filesize(self) -> str:
        return self.image.get("Filesize")

    @property
    def critical_image_properties(self) -> dict:
        # to refine
        return {
            "dng:camera.model.name": self.image_properties.get("dng:camera.model.name"),
            "dng:create.date": self.image_properties.get("dng:create.date"),
            "dng:exposure.time": self.image_properties.get("dng:exposure.time"),
            "dng:f.number": self.image_properties.get("dng:f.number"),
            "dng:focal.length": self.image_properties.get("dng:focal.length"),
            "dng:make": self.image_properties.get("dng:make"),
            "Image statistics": self.image_statistics,
        }

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, ImageMetadata) and (
            self.critical_image_properties == __o.critical_image_properties
        )


def get_metadata(path: str) -> str:
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


if __name__ == "__main__":

    duplicate_images = []
    unique_images = []

    search_path = Path(sys.argv[1])
    logging.debug(f"Will be searching files in {search_path}")

    arw_files_list = search_path.glob("**/*.ARW")

    with Pool(PROC_POOL_SIZE) as pool:
        for output in pool.imap_unordered(get_metadata, arw_files_list, chunksize=PROC_CHUNK_SIZE):
            try:
                metadata_dict = yaml.load(output, SafeLoader)
                img = ImageMetadata(**metadata_dict)

                if img in unique_images:
                    logging.info(f"Found duplicate: {img.image_path}")
                    duplicate_images.append(img)
                else:
                    logging.debug(f"New file: {img.image_path}")
                    unique_images.append(img)

            except Exception as e:
                logging.exception(e)

    logging.info(f"Unique images: {len(unique_images)}")
    logging.info(f"Duplicate images: {len(duplicate_images)}")
