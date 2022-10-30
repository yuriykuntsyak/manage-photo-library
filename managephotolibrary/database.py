# -*- coding: utf-8 -*-

"""
Copyright (c) 2022 Yuriy Kuntsyak (https://yuriyk.dev)

This code is licensed under MIT license (see LICENSE for details)
"""

import logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.ERROR)

SQLALCHEMY_DATABASE_URL = "sqlite:///./sqlite.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, echo=True, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
