# -*- coding: utf-8 -*-

"""
Copyright (c) 2022 Yuriy Kuntsyak (https://yuriyk.dev)

This code is licensed under MIT license (see LICENSE for details)
"""

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime

import logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)

class ChannelDepth(BaseModel):
    red: str = Field(..., alias='Red')
    green: str = Field(..., alias='Green')
    blue: str = Field(..., alias='Blue')


class Red(BaseModel):
    min: str
    max: str
    mean: str
    median: str
    standard_deviation: str = Field(..., alias='standard deviation')
    kurtosis: float
    skewness: float
    entropy: float


class Green(BaseModel):
    min: str
    max: str
    mean: str
    median: str
    standard_deviation: str = Field(..., alias='standard deviation')
    kurtosis: float
    skewness: float
    entropy: float


class Blue(BaseModel):
    min: str
    max: str
    mean: str
    median: str
    standard_deviation: str = Field(..., alias='standard deviation')
    kurtosis: float
    skewness: float
    entropy: float


class ChannelStatistics(BaseModel):
    pixels: int = Field(..., alias='Pixels')
    red: Red = Field(..., alias='Red')
    green: Green = Field(..., alias='Green')
    blue: Blue = Field(..., alias='Blue')


class Overall(BaseModel):
    min: str
    max: str
    mean: str
    median: str
    standard_deviation: str = Field(..., alias='standard deviation')
    kurtosis: float
    skewness: float
    entropy: float


class ImageStatistics(BaseModel):
    overall: Overall = Field(..., alias='Overall')


class Chromaticity(BaseModel):
    red_primary: str = Field(..., alias='red primary')
    green_primary: str = Field(..., alias='green primary')
    blue_primary: str = Field(..., alias='blue primary')
    white_point: str = Field(..., alias='white point')


class Profiles(BaseModel):
    profile_xmp: str = Field(..., alias='Profile-xmp')


class Properties(BaseModel):
    date_create: datetime = Field(..., alias='date:create')
    date_modify: datetime = Field(..., alias='date:modify')
    date_timestamp: datetime = Field(..., alias='date:timestamp')
    dng_camera_model_name: str = Field(..., alias='dng:camera.model.name')
    dng_create_date: datetime = Field(..., alias='dng:create.date')
    dng_exposure_time: str = Field(..., alias='dng:exposure.time')
    dng_f_number: float = Field(..., alias='dng:f.number')
    dng_focal_length: str = Field(..., alias='dng:focal.length')
    dng_focal_length_in_35mm_format: str = Field(
        ..., alias='dng:focal.length.in.35mm.format'
    )
    dng_gps_altitude: str = Field(..., alias='dng:gps.altitude')
    dng_gps_latitude: str = Field(..., alias='dng:gps.latitude')
    dng_gps_longitude: str = Field(..., alias='dng:gps.longitude')
    dng_iso_setting: int = Field(..., alias='dng:iso.setting')
    dng_lens: str = Field(..., alias='dng:lens')
    dng_lens_f_stops: float = Field(..., alias='dng:lens.f.stops')
    dng_lens_type: Optional[str] = Field(..., alias='dng:lens.type')
    dng_make: str = Field(..., alias='dng:make')
    dng_max_aperture_at_max_focal: float = Field(
        ..., alias='dng:max.aperture.at.max.focal'
    )
    dng_max_aperture_at_min_focal: float = Field(
        ..., alias='dng:max.aperture.at.min.focal'
    )
    dng_max_aperture_value: float = Field(..., alias='dng:max.aperture.value')
    dng_max_focal_length: str = Field(..., alias='dng:max.focal.length')
    dng_min_focal_length: str = Field(..., alias='dng:min.focal.length')
    dng_software: str = Field(..., alias='dng:software')
    dng_wb_rb_levels: str = Field(..., alias='dng:wb.rb.levels')
    signature: str
    xmp__rating: int = Field(..., alias='xmp:Rating')


class Artifacts(BaseModel):
    verbose: bool


class Image(BaseModel):
    filename: str = Field(..., alias='Filename')
    format: str = Field(..., alias='Format')
    class_: str = Field(..., alias='Class')
    geometry: str = Field(..., alias='Geometry')
    units: str = Field(..., alias='Units')
    colorspace: str = Field(..., alias='Colorspace')
    type: str = Field(..., alias='Type')
    base_type: str = Field(..., alias='Base type')
    endianness: str = Field(..., alias='Endianness')
    depth: str = Field(..., alias='Depth')
    channel_depth: ChannelDepth = Field(..., alias='Channel depth')
    channel_statistics: ChannelStatistics = Field(..., alias='Channel statistics')
    image_statistics: ImageStatistics = Field(..., alias='Image statistics')
    rendering_intent: str = Field(..., alias='Rendering intent')
    gamma: float = Field(..., alias='Gamma')
    chromaticity: Chromaticity = Field(..., alias='Chromaticity')
    matte_color: str = Field(..., alias='Matte color')
    background_color: str = Field(..., alias='Background color')
    border_color: str = Field(..., alias='Border color')
    transparent_color: str = Field(..., alias='Transparent color')
    interlace: str = Field(..., alias='Interlace')
    intensity: str = Field(..., alias='Intensity')
    compose: str = Field(..., alias='Compose')
    page_geometry: str = Field(..., alias='Page geometry')
    dispose: str = Field(..., alias='Dispose')
    iterations: int = Field(..., alias='Iterations')
    compression: str = Field(..., alias='Compression')
    orientation: str = Field(..., alias='Orientation')
    profiles: Profiles = Field(..., alias='Profiles')
    properties: Properties = Field(..., alias='Properties')
    artifacts: Artifacts = Field(..., alias='Artifacts')
    tainted: bool = Field(..., alias='Tainted')
    filesize: str = Field(..., alias='Filesize')
    number_pixels: str = Field(..., alias='Number pixels')
    pixel_cache_type: str = Field(..., alias='Pixel cache type')
    pixels_per_second: str = Field(..., alias='Pixels per second')
    user_time: str = Field(..., alias='User time')
    elapsed_time: float = Field(..., alias='Elapsed time')
    version: str = Field(..., alias='Version')

    class Config:
        orm_mode = True
