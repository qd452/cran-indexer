#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_restplus import Api
from webapp.api.package import package_ns

rest_bp = Blueprint('rest_bp', __name__)
api = Api(rest_bp, version='1.0', title='Package API',
          descritpion='Package Indexing and Sync API')

api.add_namespace(package_ns)
