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

from pathlib import Path

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader

from sqlalchemy.orm import Session

from .constants import PROC_POOL_SIZE, PROC_CHUNK_SIZE
from .utils import get_img_metadata
from . import models, schemas, database

logging.basicConfig(level=logging.DEBUG)

# to be fixed
# def get_db():
#     logging.debug("Getting a new DB session")

#     db = database.SessionLocal()
#     logging.debug(f"{db!r}")
#     try:
#         yield db
#     finally:
#         db.close()

def get_image_by_filename(db: Session, image_filename: str):
    return db.query(models.Image).filter(models.Image.filename == image_filename).first()

def create_image(db: Session, img: schemas.Image):
    logging.debug(f"Going to try inserting image {img.filename!r} into the DB.")

    if get_image_by_filename(db, img.filename):
        logging.error(f"Image {img.filename} is already in teh DB. Not adding it again.")
        return None

    db_img = models.Image(
        filename = img.filename,
        filesize = img.filesize,
    )

    try:
        db.add(db_img)
        db.commit()
        db.refresh(db_img)
    except Exception as e:
        logging.error(f"Failed inserting image into the DB. Error: {e!r}")
    return db_img

def create_image_properties(db: Session, prop: schemas.Properties, image_filename: str):
    logging.debug(f"Going to try inserting properties for {image_filename} into the DB.")

    image_in_db = get_image_by_filename(db, image_filename)
    if not image_in_db:
        logging.error(f"Image {image_filename} is not found in DB. MNot going to create properties for it.")
        return None
    elif image_in_db.properties:
        logging.error(f"Image {image_filename} seems to already have properties saved: {image_in_db.properties}")
        return None

    db_prop = models.Properties(image_filename=image_filename, **prop.dict())

    try:
        db.add(db_prop)
        db.commit()
        db.refresh(db_prop)
    except Exception as e:
        logging.error(f"Failed inserting properties for image {image_filename} into the DB. Error: {e!r}")
    return db_prop


if __name__ == "__main__":
    database.Base.metadata.create_all(bind=database.engine)

    duplicate_images = []
    unique_images = []

    search_path = Path(sys.argv[1])
    logging.debug(f"Will be searching files in {search_path}")

    arw_files_list_all = search_path.glob("**/*.ARW")
    arw_files_list_filtered = []

    with database.SessionLocal() as session:
        for filename in arw_files_list_all:
            if not get_image_by_filename(session, f"{filename}"):
                arw_files_list_filtered.append(f"{filename}")
            else:
                logging.debug(f"{filename} already in DB. Skipping metadata scan.")

    with Pool(PROC_POOL_SIZE) as pool:
        for output in pool.imap_unordered(get_img_metadata, arw_files_list_filtered, chunksize=PROC_CHUNK_SIZE):
            try:
                img_metadata_dict = yaml.load(output, SafeLoader).get("Image")
                img = schemas.Image(**img_metadata_dict)
                prop = img.properties

                with database.SessionLocal() as session:
                    create_image(session, img)
                    create_image_properties(session, prop, img.filename)
                
                logging.info(f"Saved file: {img.filename}")


            except Exception as e:
                logging.exception(e)


    with database.SessionLocal() as session:
        test_img = get_image_by_filename(session, '../organize-photolibrary/tests/files/10221007/DSC02029.ARW')
        logging.info(f"{test_img.filename!r}")

        # TO DO: get properties for specific image
        # logging.info(f"{test_img.properties.dng_create_date}")
