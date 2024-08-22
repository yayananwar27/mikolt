from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS

accessapp_api = Blueprint('accessapp_api', __name__)
CORS(accessapp_api, supports_credentials=True, resources=r'*', origins='*', methods=['GET','POST','PUT','DELETE'])
api = Api(accessapp_api)

from .tokenapi import TokenApi
from .tokenstatus import VerifyTokenApi, ParamVerifyTokenApi

api.add_resource(TokenApi, '')
api.add_resource(VerifyTokenApi, '/@verify')
api.add_resource(ParamVerifyTokenApi, '/@verify?type=<type>')

def init_docs(docs):
    docs.register(TokenApi, blueprint='accessapp_api')
    #docs.register(VerifyTokenApi, blueprint='accessapp_api')
    docs.register(ParamVerifyTokenApi, blueprint='accessapp_api')