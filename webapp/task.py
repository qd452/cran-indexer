# app/server/image/tasks.py
import os
import math
from flask import current_app
from webapp.utils.parser import PackageParser
from webapp.utils.packge_handler import PackageHandler
from webapp import cache, celery, mongo


def is_package_processed_strict(pkg_name, pkg_version):
    pkg_ver = pkg_name + '_' + pkg_version
    if cache.sismember('processed', pkg_ver):
        return True
    if mongo.db.package.find_one(
            {"Package": pkg_name, "Version": pkg_version}):
        # if not in cache but in db, add in cache
        cache.sadd('processed', pkg_ver)
        return True
    return False


@celery.task
def sync_package():
    for pkg in PackageParser().parse_from_url():
        pkg, ver = pkg['Package'], pkg['Version']
        pkg_ver = pkg + '_' + ver
        if not cache.sismember('processed', pkg_ver):
            process_package.apply_async(args=[pkg, ver])


@celery.task(bind=True, retry_kwargs={'max_retries': 2})
def process_package(self, pkg_name, pkg_version):
    try:
        # to make sure the consumer is idempotent
        if is_package_processed_strict(pkg_name, pkg_version):
            return
        pkg_handler = PackageHandler(pkg_name, pkg_version)
        app = current_app._get_current_object()
        desc = pkg_handler.get_description(app.config['TMP_DIR'])
        pkg_id = mongo.db.package.insert_one(desc).inserted_id
        pkg_ver = pkg_name + '_' + pkg_version
        cache.sadd('processed', pkg_ver)
    except Exception as exc:
        # retry after 5 mins
        raise self.retry(exc=exc, countdown=5 * 60)
