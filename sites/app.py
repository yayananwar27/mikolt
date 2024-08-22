from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS

sites_api = Blueprint('sites_api', __name__)
CORS(sites_api, supports_credentials=True, resources=r'*', origins='*', methods=['GET','POST','PUT','DELETE'])
api = Api(sites_api)

from .site import SiteApi, InfoIdSiteApi, InfoNameSiteApi
from .sync_site import SyncSiteApi
from .mikrotik import SiteMikrotikApi

api.add_resource(SiteApi, '')
api.add_resource(InfoIdSiteApi, '?id=<int:id>')
api.add_resource(InfoNameSiteApi, '?name=<name>')
api.add_resource(SyncSiteApi, '/@sync')
api.add_resource(SiteMikrotikApi, '/mikrotik')

def init_docs(docs):
    docs.register(SiteApi, blueprint='sites_api')
    docs.register(InfoIdSiteApi, blueprint='sites_api')
    docs.register(InfoNameSiteApi, blueprint='sites_api')
    docs.register(SyncSiteApi, blueprint='sites_api')
    docs.register(SiteMikrotikApi, blueprint='sites_api')

from dotenv import load_dotenv
import os
load_dotenv()
from extensions import scheduler
from .sync_site import SyncSiteJob
scheduler.add_job(func=SyncSiteJob,
        trigger="interval",
        seconds=int(os.environ["INTERVAL_SYNC_SITE"]),
        id="SyncSite_job",
        name="SyncSite_job", 
        misfire_grace_time=60,
        replace_existing=False)