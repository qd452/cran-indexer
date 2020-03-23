# app/server/image/tasks.py
import os
import math
from flask import current_app
from webapp.utils.parser import PackageParser
from webapp.utils.packge_handler import PackageHandler
from webapp import cache, celery, mongo


# celery = create_celery_app(app)


@celery.task
def sync_package():
    for pkg in PackageParser().parse_from_url():
        pkg, ver = pkg['Package'], pkg['Version']
        pkg_ver = 'processed:' + pkg + '_' + ver
        cache.set(pkg_ver, 'false', nx=True)
        if cache.get(pkg_ver) == 'false':
            cache.set(pkg_ver, 'pending')
            process_package.apply_async(args=[pkg, ver])


@celery.task
def process_package(pkg_name, pkg_version):
    try:
        pkg_handler = PackageHandler(pkg_name, pkg_version)
        app = current_app._get_current_object()
        desc = pkg_handler.get_description(app.config['TMP_DIR'])
        pkg_id = mongo.db.package.insert_one(desc).inserted_id
        print(pkg_id)
        pkg_ver = 'processed:' + pkg_name + '_' + pkg_version
        cache.set(pkg_ver, 'true')
    except Exception as e:
        print(f'{pkg_name}-')
