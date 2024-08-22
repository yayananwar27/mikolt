from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS

clientppp_api = Blueprint('clientppp_api', __name__)
CORS(clientppp_api, supports_credentials=True, resources=r'*', origins='*', methods=['GET','POST','PUT','DELETE'])
api = Api(clientppp_api)

from .client import ClientPPPSecretsApi, SearchIDClientPPPSecretsApi, SearchMikrotikClientPPPSecretsApi, SearchProfileClientPPPSecretsApi, SearchSiteClientPPPSecretsApi, SearchIDClientPPPStatsSecretsApi, ServersideMikrotikClientPPPSecretsApi
from .tariksecret import TarikPPPSecretApi
from .stats import ClientPPPStatsSecretsApi, ClientPPPStatsMonthSecretsApi

api.add_resource(ClientPPPSecretsApi, '')
api.add_resource(SearchIDClientPPPSecretsApi, '?client_id=<client_id>')
api.add_resource(SearchSiteClientPPPSecretsApi, '?site_id=<int:site_id>')
api.add_resource(SearchMikrotikClientPPPSecretsApi, '?mikrotik_id=<int:mikrotik_id>')
api.add_resource(SearchProfileClientPPPSecretsApi, '?profile=<profile>')
api.add_resource(TarikPPPSecretApi, '/@tarikdata')
api.add_resource(SearchIDClientPPPStatsSecretsApi, '?client_id=<client_id>&stats=<int:stats>')
api.add_resource(ClientPPPStatsSecretsApi, '/statistic')
api.add_resource(ClientPPPStatsMonthSecretsApi, '/statistic/month')
api.add_resource(ServersideMikrotikClientPPPSecretsApi, '?page=<int:page>&per_page=<int:per_page>&search=<search>')

def init_docs(docs):
    docs.register(ClientPPPSecretsApi, blueprint='clientppp_api')
    docs.register(SearchIDClientPPPSecretsApi, blueprint='clientppp_api')
    docs.register(SearchSiteClientPPPSecretsApi, blueprint='clientppp_api')
    docs.register(SearchMikrotikClientPPPSecretsApi, blueprint='clientppp_api')
    docs.register(SearchProfileClientPPPSecretsApi, blueprint='clientppp_api')
    docs.register(TarikPPPSecretApi, blueprint='clientppp_api')
    docs.register(SearchIDClientPPPStatsSecretsApi, blueprint='clientppp_api')
    docs.register(ClientPPPStatsSecretsApi, blueprint='clientppp_api')
    docs.register(ClientPPPStatsMonthSecretsApi, blueprint='clientppp_api')
    docs.register(ServersideMikrotikClientPPPSecretsApi, blueprint='clientppp_api')
        

from dotenv import load_dotenv
import os
load_dotenv()
from extensions import scheduler
from .tarikstats import TarikStatsJob
scheduler.add_job(func=TarikStatsJob,
        trigger="interval",
        seconds=int(os.environ["INTERVAL_GET_STATS"]),
        id="GetStats_job",
        name="GetStats_job", 
        misfire_grace_time=60,
        replace_existing=False)