#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Copyright (c) 2022 Yuriy Kuntsyak (https://yuriyk.dev)

This code is licensed under MIT license (see LICENSE for details)
"""

import yaml
import logging
import sys
import shutil
import re
from time import sleep
from multiprocessing import Pool
from multiprocessing.pool import ThreadPool
from typing import Optional
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
from datetime import datetime
from dateutil import parser

from pathlib import Path, PurePath

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader

from sqlalchemy.orm import Session

from .constants import PROC_POOL_SIZE, PROC_CHUNK_SIZE
from .utils import get_img_metadata
from . import models, schemas, database


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

# to be fixed
# def get_db():
#     log.debug("Getting a new DB session")

#     db = database.SessionLocal()
#     log.debug(f"{db!r}")
#     try:
#         yield db
#     finally:
#         db.close()

def get_image_by_filename(db: Session, image_filename: str):
    return db.query(models.Image).filter(models.Image.filename == image_filename).first()

def get_images_by_basename(db: Session, image_basename: str):
    return db.query(models.Image).filter(
        models.Image.filename.endswith(image_basename)
    ).all()

def get_images_by_date(db: Session, date_gt: datetime, date_lt: datetime):
    # very ugly workaround to avoid getting models.Properties as well
    return [
        i for i, _ in db.query(
            models.Image, models.Properties
        ).join(
            models.Properties
        ).filter(
            models.Properties.dng_create_date.between(date_gt, date_lt)
        ).all()
    ]

def get_images_by_basename_and_date(db: Session, image_basename: str, date_gt: datetime, date_lt: datetime):
    # very ugly workaround to avoid getting models.Properties as well
    return [
        i for i, _ in db.query(
            models.Image, models.Properties
        ).join(
            models.Properties
        ).filter(
            models.Properties.dng_create_date.between(date_gt, date_lt),
            models.Image.filename.endswith(image_basename)
        ).all()
    ]

def get_images_all(db: Session, limit_results: Optional[int] = None):
    return db.query(models.Image).limit(limit_results).all()

def get_unique_images_all(db: Session, limit_results: Optional[int] = None):
    return db.query(models.UniqueImage).limit(limit_results).all()

def get_unique_image_by_filename(db: Session, image_filename: str):
    return db.query(models.UniqueImage).filter(models.UniqueImage.image_filename == image_filename).first()

def add_unique_image(db: Session, image_filename: str):
    log.debug(f"Going to try inserting image {img.filename!r} as unique image into the DB.")

    u_i_in_db = get_unique_image_by_filename(db, image_filename)
    if not u_i_in_db:
        db_img = models.UniqueImage(
            image_filename=image_filename
        )
        try:
            db.add(db_img)
            db.commit()
            db.refresh(db_img)
        except Exception as e:
            log.error(f"Failed inserting image into the DB. Error: {e!r}")
        return db_img
    else:
        log.debug(f"Image {image_filename} is already in unique_images.")
        return None

def create_image(db: Session, img: schemas.Image):
    log.debug(f"Going to try inserting image {img.filename!r} into the DB.")

    if get_image_by_filename(db, img.filename):
        log.error(f"Image {img.filename} is already in the DB. Not adding it again.")
        return None

    db_img = models.Image(
        filename = img.filename,
        format = img.format,
        class_ = img.class_,
        geometry = img.geometry,
        units = img.units,
        colorspace = img.colorspace,
        type = img.type,
        base_type = img.base_type,
        endianness = img.endianness,
        depth = img.depth,
        rendering_intent = img.rendering_intent,
        gamma = img.gamma,
        matte_color = img.matte_color,
        background_color = img.background_color,
        border_color = img.border_color,
        transparent_color = img.transparent_color,
        interlace = img.interlace,
        intensity = img.intensity,
        compose = img.compose,
        page_geometry = img.page_geometry,
        dispose = img.dispose,
        iterations = img.iterations,
        compression = img.compression,
        orientation = img.orientation,
        tainted = img.tainted,
        filesize = img.filesize,
        number_pixels = img.number_pixels,
        pixel_cache_type = img.pixel_cache_type,
        pixels_per_second = img.pixels_per_second,
        user_time = img.user_time,
        elapsed_time = img.elapsed_time,
        version = img.version,
    )

    try:
        db.add(db_img)
        db.commit()
        db.refresh(db_img)
    except Exception as e:
        log.error(f"Failed inserting image into the DB. Error: {e!r}")
    return db_img

def create_image_properties(db: Session, prop: schemas.Properties, image_filename: str):
    log.debug(f"Going to try inserting properties for {image_filename} into the DB.")

    image_in_db = get_image_by_filename(db, image_filename)
    if not image_in_db:
        log.error(f"Image {image_filename} is not found in DB. MNot going to create properties for it.")
        return None
    elif image_in_db.properties:
        log.error(f"Image {image_filename} seems to already have properties saved: {image_in_db.properties}")
        return None

    db_prop = models.Properties(image_filename=image_filename, **prop.dict())

    try:
        db.add(db_prop)
        db.commit()
        db.refresh(db_prop)
    except Exception as e:
        log.error(f"Failed inserting properties for image {image_filename} into the DB. Error: {e!r}")
    return db_prop



if __name__ == "__main__":
    database.Base.metadata.create_all(bind=database.engine)

    

    duplicate_images = []
    unique_images = []

    search_path = Path(sys.argv[1]).resolve()
    destination_path = Path(sys.argv[2]).resolve()
    filter_dt_gt = parser.parse(sys.argv[3]) # "2022-09-30T00:00:00")
    filter_dt_lt = parser.parse(sys.argv[4]) # "2022-10-17T00:00:00")

    log.debug(f"Will be searching files in {search_path}")
    log.info(f"Going to only work on images between {filter_dt_gt} and {filter_dt_lt}")

    arw_files_list_all = search_path.glob("**/*.ARW")

    # this is a workarount to speed up testing
    # consumes memory because list and not generator anymore
    arw_files_list = [f for f in arw_files_list_all]
    arw_files_list_filtered = []

    log.info(f"{len(arw_files_list)} ARW files in {search_path}.")


    # TODO:
    # add check if file (in search path) still exists on disc


    with database.SessionLocal() as session:
        for filename in tqdm(arw_files_list, desc="Compiling list of new files to scan on disc", unit="files"):

            img_in_db = get_image_by_filename(session, f"{filename}")

            # this one becomes slow because of additional implicit query for properties
            if not img_in_db or not img_in_db.properties:
                arw_files_list_filtered.append(f"{filename}")
            else:
                log.debug(f"{filename!r} already in DB. Skipping metadata scan.")

    with logging_redirect_tqdm():
        with ThreadPool(PROC_POOL_SIZE) as pool:
            # with tqdm(total=len(arw_files_list_filtered), desc="Scanning metadata of new files found disc", unit="files") as pbar:
                # for output in pool.imap_unordered(get_img_metadata, arw_files_list_filtered, chunksize=PROC_CHUNK_SIZE):
            for output in tqdm(pool.imap_unordered(get_img_metadata, arw_files_list_filtered, chunksize=PROC_CHUNK_SIZE), total=len(arw_files_list_filtered), desc="Scanning metadata of new files found disc", unit="files"):
                try:
                    img_metadata_dict = yaml.load(output, SafeLoader).get("Image")
                    img = schemas.Image(**img_metadata_dict)
                    create_image(session, img)
                    create_image_properties(session, img.properties, img.filename)

                        # create_image_channel_depth(session, img.properties, img.filename)
                        # create_image_channel_statistics(session, img.properties, img.filename)
                        # create_image_image_statistics(session, img.properties, img.filename)
                        # create_image_chromaticity(session, img.properties, img.filename)
                        # create_image_profiles(session, img.properties, img.filename)
                        # create_image_artifacts(session, img.properties, img.filename)
                    
                    log.info(f"Saved file metadata to DB: {img.filename!r}")

                except Exception as e:
                    log.exception(e)


    with logging_redirect_tqdm():
        with database.SessionLocal() as session:
            for img in tqdm(get_images_by_date(session, filter_dt_gt, filter_dt_lt), desc="Scanning DB for deduplication", unit="files"):

                img_basename = PurePath(img.filename).name

                if not any(img_basename in sub for sub in unique_images):
                    add_unique_image(session, img.filename)
                    log.debug(f"Added {img.filename!r} to unique_images.")
                    continue               

                # for dup_img in get_images_by_basename_and_date(session, img_basename, filter_dt_gt, filter_dt_lt):
                for dup_img in get_images_by_basename(session, img_basename):

                    # skip any image where date is not as per the filters
                    if not (filter_dt_gt <= dup_img.properties.dng_create_date <= filter_dt_lt):
                        log.debug(f"Image {dup_img.filename!r} has been created outside of date filter, skipping duplicate comparison.")
                        continue

                    if img.filename == dup_img.filename:
                        log.debug(f"Same file as the one we are comparing to. Skipping {dup_img.filename!r}")
                        continue

                    log.debug(f"Found a suspect duplicate of {img_basename} at path {dup_img.filename!r}. Going to compare them.")
                    

                    if (img.filesize == dup_img.filesize and
                        img.properties.dng_create_date == dup_img.properties.dng_create_date): #and
                        # img.properties.dng_camera_model_name == dup_img.properties.dng_camera_model_name and
                        # img.properties.dng_exposure_time == dup_img.properties.dng_exposure_time and
                        # img.properties.dng_f_number == dup_img.properties.dng_f_number and
                        # img.properties.dng_make == dup_img.properties.dng_make):


                        # Image signature is generated from the pixel components, not the image metadata.
                        if(img.properties.signature != dup_img.properties.signature):
                            log.debug(f"Images have a different signature, ignoring this fact for now.")

                        log.debug(f"Found duplicate of {img.filename!r} at path {dup_img.filename!r}")

                        # ImageMagick has a flag known as 'taint' which becomes true is some pixels or meta-data was modified.
                        # If it is not modified IM will simple copy the file. That is part of its 'delegate' handling for external filter programs.
                        # TO DO: check for img.tainted as well

                        continue

                    else:
                        log.debug(f"Images (with same basename) are different: {img.filename!r} and {dup_img.filename!r}.")

                        if not get_unique_image_by_filename(session, dup_img.filename):
                            add_unique_image(dup_img.filename)
                            log.debug(f"Added {dup_img.filename!r} to unique_images.")
                        else:
                            log.debug(f"Image {dup_img.filename!r} is already in unique_images.")


    with logging_redirect_tqdm():
        with database.SessionLocal() as session:
            unique_images = get_unique_images_all(session)
            log.info(f"Found {len(unique_images)} total unique images.")

            for u_img in tqdm(unique_images, desc="Making path structure", unit="path"):
                i = u_img.image
                img_basename = PurePath(i.filename).name
                i_yyyy = i.properties.dng_create_date.year
                i_mm = i.properties.dng_create_date.month
                i_dd = i.properties.dng_create_date.day
                
                p = PurePath(destination_path, f"{i_yyyy}/{i_mm}/{i_dd}")

                if not Path(p).is_dir():
                    Path(p).mkdir(parents=True, exist_ok=True)
                    log.info(f"Created path {i_yyyy}/{i_mm}/{i_dd}")
                else:
                    log.debug(f"Skipped existing path {i_yyyy}/{i_mm}/{i_dd}")
                
                if Path(f"{p}/{img_basename}").is_file():
                    log.debug(f"Image {img_basename} already present at {p!r}")
                else:
                    log.info(f"Copying image {img_basename} into {p!r}")

                    # TODO: evaluate if parallel copy would speed up (on ssd as well as hdd)
                    # threading.Thread(target=shutil.copy2, args=[src,dst]).run()
                    try:
                        cp_result = shutil.copy2(i.filename, p)
                        log.info(f"Copied {i.filename} into {cp_result}")
                    except shutil.SameFileError:
                        log.info(f"Image {img_basename} already found in {p}. Skipping copy.")
                    except Exception as e:
                        log.error(e)

