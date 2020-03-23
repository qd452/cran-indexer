import os
from flask import Flask
from flask_pymongo import PyMongo
from flask_redis import FlaskRedis
from celery import Celery
from webapp.config import BaseConfig
from webapp.model import create_mongo_index

mongo = PyMongo()
cache = FlaskRedis(decode_responses=True)

celery = Celery(__name__, broker=BaseConfig.CELERY_BROKER_URL)


def create_app():
    # instantiate the app
    app = Flask(__name__)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    mongo.init_app(app)
    create_mongo_index(mongo)
    cache.init_app(app)
    celery.conf.update(app.config)
    celery.conf.task_routes = ([
                                   ('webapp.task.sync_package', {'queue': 'sync_package'}),
                                   ('webapp.task.process_package', {'queue': 'process_package'})
                               ],)

    tmp_dir = app.config['TMP_DIR']
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    # register blueprints
    from .api import rest_bp
    app.register_blueprint(rest_bp, url_prefix='/api/v0')

    # shell context for flask cli
    app.shell_context_processor({'app': app})

    return app
