# -*- coding: utf-8 -*-

"""
Copyright (c) 2022 Yuriy Kuntsyak (https://yuriyk.dev)

This code is licensed under MIT license (see LICENSE for details)
"""

from __future__ import annotations
from sqlalchemy import Boolean, Column, ForeignKey, Integer, Float, String, DateTime
from sqlalchemy.orm import relationship
from .database import Base
from typing import Optional
from datetime import datetime

import logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
#     is_active = Column(Boolean, default=True)

#     items = relationship("Item", back_populates="owner")


# class Item(Base):
#     __tablename__ = "items"

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, index=True)
#     description = Column(String, index=True)
#     owner_id = Column(Integer, ForeignKey("users.id"))

#     owner = relationship("User", back_populates="items")

#########################



# class ChannelDepth(BaseModel):
#     red = Column(String, index=True)
#     green = Column(String, index=True)
#     blue = Column(String, index=True)


# class Red(BaseModel):
#     min = Column(String)
#     max = Column(String)
#     mean = Column(String)
#     median = Column(String)
#     standard_deviation = Column(String, index=True)
#     kurtosis: float
#     skewness: float
#     entropy: float


# class Green(BaseModel):
#     min = Column(String)
#     max = Column(String)
#     mean = Column(String)
#     median = Column(String)
#     standard_deviation = Column(String, index=True)
#     kurtosis: float
#     skewness: float
#     entropy: float


# class Blue(BaseModel):
#     min = Column(String)
#     max = Column(String)
#     mean = Column(String)
#     median = Column(String)
#     standard_deviation = Column(String, index=True)
#     kurtosis: float
#     skewness: float
#     entropy: float


# class ChannelStatistics(BaseModel):
#     pixels = Column(Integer)
#     red: Red = Field(..., alias='Red')
#     green: Green = Field(..., alias='Green')
#     blue: Blue = Field(..., alias='Blue')


# class Overall(BaseModel):
#     min = Column(String)
#     max = Column(String)
#     mean = Column(String)
#     median = Column(String)
#     standard_deviation = Column(String, index=True)
#     kurtosis: float
#     skewness: float
#     entropy: float


# class ImageStatistics(BaseModel):
#     overall: Overall = Field(..., alias='Overall')


# class Chromaticity(BaseModel):
#     red_primary = Column(String, index=True)
#     green_primary = Column(String, index=True)
#     blue_primary = Column(String, index=True)
#     white_point = Column(String, index=True)


# class Profiles(BaseModel):
#     profile_xmp = Column(String, index=True)


class Properties(Base):
    __tablename__ = "properties"
    id = Column(Integer, primary_key=True)
    image = relationship("Image", back_populates="properties", uselist=False)
    image_filename = Column(String, ForeignKey("images.filename"))

    date_create = Column(DateTime(timezone=True))
    date_modify = Column(DateTime(timezone=True))
    date_timestamp = Column(DateTime(timezone=True))
    dng_camera_model_name = Column(String, index=True)
    dng_create_date = Column(DateTime(timezone=True))
    dng_exposure_time = Column(String, index=True)
    dng_f_number = Column(Float)
    dng_focal_length = Column(String, index=True)
    dng_focal_length_in_35mm_format = Column(String, index=True)
    dng_gps_altitude = Column(String, index=True)
    dng_gps_latitude = Column(String, index=True)
    dng_gps_longitude = Column(String, index=True)
    dng_iso_setting = Column(Integer)
    dng_lens = Column(String, index=True)
    dng_lens_f_stops = Column(Float)
    dng_lens_type = Column(String, nullable=True)
    dng_make = Column(String, index=True)
    dng_max_aperture_at_max_focal = Column(Float)
    dng_max_aperture_at_min_focal = Column(Float)
    dng_max_aperture_value = Column(Float)
    dng_max_focal_length = Column(String, index=True)
    dng_min_focal_length = Column(String, index=True)
    dng_software = Column(String, index=True)
    dng_wb_rb_levels = Column(String, index=True)
    signature = Column(String)
    xmp__rating = Column(Integer)


# class Artifacts(BaseModel):
#     verbose = Column(Boolean)


class Image(Base):
    __tablename__ = "images"
    filename = Column(String, index=True, primary_key=True)
    format = Column(String, index=True)
    class_ = Column(String, index=True)
    geometry = Column(String, index=True)
    units = Column(String, index=True)
    colorspace = Column(String, index=True)
    type = Column(String, index=True)
    base_type = Column(String, index=True)
    endianness = Column(String, index=True)
    depth = Column(String, index=True)

    # channel_depth: ChannelDepth = Field(..., alias='Channel depth') #
    # channel_statistics: ChannelStatistics = Field(..., alias='Channel statistics') #
    # image_statistics: ImageStatistics = Field(..., alias='Image statistics') #

    rendering_intent = Column(String, index=True)
    gamma = Column(Float)

    # chromaticity: Chromaticity = Field(..., alias='Chromaticity') #

    matte_color = Column(String, index=True)
    background_color = Column(String, index=True)
    border_color = Column(String, index=True)
    transparent_color = Column(String, index=True)
    interlace = Column(String, index=True)
    intensity = Column(String, index=True)
    compose = Column(String, index=True)
    page_geometry = Column(String, index=True)
    dispose = Column(String, index=True)
    iterations = Column(Integer)
    compression = Column(String, index=True)
    orientation = Column(String, index=True)

    # profiles: Profiles = Field(..., alias='Profiles') #

    # properties: Properties = Field(..., alias='Properties') #
    properties = relationship("Properties", back_populates="image", cascade="all, delete, delete-orphan", uselist=False)

    # artifacts: Artifacts = Field(..., alias='Artifacts') #

    tainted = Column(Boolean)
    filesize = Column(String, index=True)
    number_pixels = Column(String, index=True)
    pixel_cache_type = Column(String, index=True)
    pixels_per_second = Column(String, index=True)
    user_time = Column(String, index=True)
    elapsed_time = Column(Float)
    version = Column(String, index=True)
