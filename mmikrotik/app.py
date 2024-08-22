from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS

mmikrotik_api = Blueprint('mmikrotik_api', __name__)
CORS(mmikrotik_api, supports_credentials=True, resources=r'*', origins='*', methods=['GET','POST','PUT','DELETE'])
api = Api(mmikrotik_api)

from .main import MmikrotikApi, InfoMmikrotikApi
from .pppprofile import PPPProfileApi, NamePPPProfileApi
from .pppsecret import PPPPSecretApi, NamePPPPSecretApi

api.add_resource(MmikrotikApi, '')
api.add_resource(InfoMmikrotikApi, '?mikrotik_id=<int:mikrotik_id>')
api.add_resource(PPPProfileApi, '/<int:mikrotik_id>/pppprofile')
api.add_resource(NamePPPProfileApi, '/<int:mikrotik_id>/pppprofile?name=<name>')

api.add_resource(PPPPSecretApi, '/<int:mikrotik_id>/pppsecrets')
api.add_resource(NamePPPPSecretApi, '/<int:mikrotik_id>/pppsecrets?name=<name>')

def init_docs(docs):
    docs.register(MmikrotikApi, blueprint='mmikrotik_api')
    docs.register(InfoMmikrotikApi, blueprint='mmikrotik_api')
    docs.register(PPPProfileApi, blueprint='mmikrotik_api')
    docs.register(NamePPPProfileApi, blueprint='mmikrotik_api')
    docs.register(PPPPSecretApi, blueprint='mmikrotik_api')
    docs.register(NamePPPPSecretApi, blueprint='mmikrotik_api')
    