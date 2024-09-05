from dotenv import load_dotenv
import os
load_dotenv()

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
db = SQLAlchemy()

# from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ProcessPoolExecutor, ThreadPoolExecutor

class ApplicationConfig:
    SECRET_KEY = os.environ["SECRET_KEY"]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = "mysql://{0}:{1}@{2}:{3}/{4}".format(os.environ["DATABASE_USER"],os.environ["DATABASE_PASSWORD"],os.environ["DATABASE_HOST"],os.environ["DATABASE_PORT"],os.environ["DATABASE_DB"])
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True, 'pool_recycle':5}
    SQLALCHEMY_POOL_SIZE = 1000
    SQLALCHEMY_MAX_OVERFLOW = -1
    SQLALCHEMY_POOL_TIMEOUT = 300

    APISPEC_SPEC = APISpec(
        title='Mikrotik Management API',
        version='0.0.2',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0.2'
    )
    api_key_scheme = {"type": "apiKey", "in": "header", "name": "Authorization"}
    APISPEC_SPEC.components.security_scheme("ApiKeyAuth", api_key_scheme)
    APISPEC_SWAGGER_URL = '/swagger/'
    APISPEC_SWAGGER_UI_URL = '/swagger-ui/'
    
    SCHEDULER_EXECUTORS = {
        'default': {'type': 'threadpool', 'max_workers': 1},
        'processpool': ProcessPoolExecutor(max_workers=1),
        'threadpool': ThreadPoolExecutor(max_workers=1)
    }
    SCHEDULER_JOB_DEFAULTS = {'coalesce': True, 'max_instances': 1}