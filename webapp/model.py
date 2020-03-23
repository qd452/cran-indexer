#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_pymongo import PyMongo
import pymongo


def create_mongo_index(mongo):
    mongo.db.package.create_index([("Package", pymongo.ASCENDING),
                                   ("Version", pymongo.ASCENDING)],
                                  unique=True)
