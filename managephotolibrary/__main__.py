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

from pathlib import Path, PurePath

try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader

from sqlalchemy.orm import Session

from .constants import PROC_POOL_SIZE, PROC_CHUNK_SIZE
from .utils import get_img_metadata
from . import models, schemas, database

logging.basicConfig(level=logging.WARNING)
logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)


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

def get_images_by_basename(db: Session, image_basename: str):
    return db.query(models.Image).filter(
        models.Image.filename.endswith(image_basename)
    ).all()


def get_images_all(db: Session):
    return db.query(models.Image).all()

def create_image(db: Session, img: schemas.Image):
    logging.debug(f"Going to try inserting image {img.filename!r} into the DB.")

    if get_image_by_filename(db, img.filename):
        logging.error(f"Image {img.filename} is already in the DB. Not adding it again.")
        return None

    # logging.debug(f"{img.dict()!r}")

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

    search_path = Path(sys.argv[1]).resolve()
    logging.debug(f"Will be searching files in {search_path}")

    arw_files_list_all = search_path.glob("**/*.ARW")
    arw_files_list_filtered = []

    with database.SessionLocal() as session:
        for filename in arw_files_list_all:
            if not get_image_by_filename(session, f"{filename}"):
                arw_files_list_filtered.append(f"{filename}")
            else:
                logging.debug(f"{filename} already in DB. Skipping Magick scan.")

    with Pool(PROC_POOL_SIZE) as pool:
        for output in pool.imap_unordered(get_img_metadata, arw_files_list_filtered, chunksize=PROC_CHUNK_SIZE):
            try:
                img_metadata_dict = yaml.load(output, SafeLoader).get("Image")
                img = schemas.Image(**img_metadata_dict)
                create_image(session, img)
                create_image_properties(session, img.properties, img.filename)

                # with database.SessionLocal() as session:
                #     img_basename = PurePath(img.filename).name
                #     same_name_imgs = get_images_by_basename(session, img_basename)

                    # for i in same_name_imgs:
                    #     logging.warning(f"Image {img_basename} already found at path {i.filename}. Going to compare them")
                    #     if (
                    #         img.properties.dng_create_date == i.properties.dng_create_date
                    #         AND img.filesize == i.filesize
                    #         AND
                    #     ):
                    #         logging.debug(f"These files are equal. ")



                        


                    # create_image_channel_depth(session, img.properties, img.filename)
                    # create_image_channel_statistics(session, img.properties, img.filename)
                    # create_image_image_statistics(session, img.properties, img.filename)
                    # create_image_chromaticity(session, img.properties, img.filename)
                    # create_image_profiles(session, img.properties, img.filename)
                    # create_image_artifacts(session, img.properties, img.filename)
                
                logging.info(f"Saved file: {img.filename}")

            except Exception as e:
                logging.exception(e)

    logging.info("Scanning DB for deduplication")
    with database.SessionLocal() as session:
        for img in get_images_all(session):

            img_basename = PurePath(img.filename).name
            for dup_img in get_images_by_basename(session, img_basename):
                logging.info(f"Found a duplicate of {img_basename} at path {dup_img.filename}. Going to compare them.")
                
                if (img.filesize == dup_img.filesize and
                    img.properties.dng_create_date == dup_img.properties.dng_create_date and
                    img.properties.dng_camera_model_name == dup_img.properties.dng_camera_model_name and
                    img.properties.dng_exposure_time == dup_img.properties.dng_exposure_time and
                    img.properties.dng_f_number == dup_img.properties.dng_f_number and
                    img.properties.dng_make == dup_img.properties.dng_make):

                    logging.debug(f"These files are equal. ")


            # "dng:camera.model.name": self.image_properties.get("dng:camera.model.name"),
            # "dng:create.date": self.image_properties.get("dng:create.date"),
            # "dng:exposure.time": self.image_properties.get("dng:exposure.time"),
            # "dng:f.number": self.image_properties.get("dng:f.number"),
            # "dng:focal.length": self.image_properties.get("dng:focal.length"),
            # "dng:make": self.image_properties.get("dng:make"),

                    # for i in same_name_imgs:
                    #     logging.warning(f"Image {img_basename} already found at path {i.filename}. Going to compare them")
                    #     if (
                    #         img.properties.dng_create_date == i.properties.dng_create_date
                    #         AND img.filesize == i.filesize
                    #         AND
                    #     ):
                    #         logging.debug(f"These files are equal. ")


                        #     if (
                    #         img.properties.dng_create_date == i.properties.dng_create_date
                    #         AND img.filesize == i.filesize
                    #         AND
                    #     ):
    # with database.SessionLocal() as session:

    #     img_basename = PurePath("/Users/yuriyk/prj/organize-photolibrary/tests/files/10221007/DSC02029.ARW").name
    #     same_name_imgs = get_images_by_basename(session, img_basename)

    #     for i in same_name_imgs:
    #         logging.warning(f"Image {img_basename} already found at path {i.filename}")


    # with database.SessionLocal() as session:



        # TEST_IMG_PATH = '/Users/yuriyk/prj/organize-photolibrary/tests/files/10221007/DSC02029.ARW'
        # test_img = get_image_by_filename(session, TEST_IMG_PATH)
        # if test_img:
        #     logging.info(f"Confirmed exists: {test_img.filename!r}")

        #     try:
        #         session.delete(test_img)
        #         session.commit()

        #     except Exception as e:
        #         logging.error(f"Failed test delete {e}")
            
        #     check_deleted_img = get_image_by_filename(session, TEST_IMG_PATH)
        #     if check_deleted_img:
        #         logging.error(f"{check_deleted_img.filename} still in DB.")
        #     else:
        #         logging.info(f"Successfully deleted image from DB.")

        # else:
        #     logging.error(f"Test image not found!")

        



        # TO DO: get properties for specific image
        # logging.info(f"{test_img.properties.dng_create_date}")
