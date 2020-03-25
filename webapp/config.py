import os

basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig(object):
    """Base configuration."""
    WTF_CSRF_ENABLED = True

    # REDIS_URL = 'redis://redis:6379/0'
    REDIS_URL = 'redis://localhost:6379/0'
    MONGO_URI = "mongodb://localhost:27017/cranIndex"
    CELERY_BROKER_URL = 'pyamqp://guest@localhost//'
    # CELERY_BROKER_URL = REDIS_URL

    TMP_DIR = basedir + '/tmp'


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    WTF_CSRF_ENABLED = False


class ProductionConfig(BaseConfig):
    """Development configuration."""
    WTF_CSRF_ENABLED = False
    REDIS_URL = 'redis://redis:6379/0'
    MONGO_URI = "mongodb://mongodb:27017/cranIndex"
    CELERY_BROKER_URL = 'pyamqp://user:bitnami@rabbitmq//'



class TestingConfig(BaseConfig):
    """Testing configuration."""
    TESTING = True
    WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
