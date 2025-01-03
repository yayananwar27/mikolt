from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS

oltonu_api = Blueprint('oltonu_api', __name__)
CORS(oltonu_api, supports_credentials=True, resources=r'*', origins='*', methods=['GET','POST','PUT','DELETE'])
api = Api(oltonu_api)

from .onu_configured import OnuConfiguredApi, InfoOnuConfiguredApi, InfoOnuConfiguredStatusRawApi
from .sync_onuconf import SyncOnuConfiguredFromOltApi

api.add_resource(OnuConfiguredApi, '/configured')
api.add_resource(InfoOnuConfiguredApi, '/configured/info')
api.add_resource(InfoOnuConfiguredStatusRawApi, '/configured/info/status_raw')
api.add_resource(SyncOnuConfiguredFromOltApi, '/sync/fromolt')

def init_docs(docs):
    docs.register(OnuConfiguredApi, blueprint= 'oltonu_api')
    docs.register(InfoOnuConfiguredApi, blueprint= 'oltonu_api')
    docs.register(SyncOnuConfiguredFromOltApi, blueprint= 'oltonu_api')
    docs.register(InfoOnuConfiguredStatusRawApi, blueprint= 'oltonu_api')


from dotenv import load_dotenv
import os
load_dotenv()
from extensions import scheduler
from .job_onufromolt import SyncOnuFromOlt, GetOnuStatusFromOlt

scheduler.add_job(func=SyncOnuFromOlt,
        trigger="interval",
        seconds=int(os.environ["INTERVAL_GET_ONU_FROM_OLT"]),
        id="SyncOnuFromOlt_job",
        name="SyncOnuFromOlt_job", 
        misfire_grace_time=60,
        replace_existing=False)

scheduler.add_job(func=GetOnuStatusFromOlt,
        trigger="interval",
        seconds=int(os.environ["INTERVAL_GET_ONUSTATUS_FROM_OLT"]),
        id="GetStatsOnuFromOlt_job",
        name="GetStatsOnuFromOlt_job", 
        misfire_grace_time=60,
        replace_existing=False)