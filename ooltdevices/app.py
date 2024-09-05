from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS

oltdevices_api = Blueprint('oltdevices_api', __name__)
CORS(oltdevices_api, supports_credentials=True, resources=r'*', origins='*', methods=['GET','POST','PUT','DELETE'])
api = Api(oltdevices_api)

from .device import OltDeviceapi, InfoOltDeviceapi

api.add_resource(OltDeviceapi, '')
api.add_resource(InfoOltDeviceapi, '/info')

def init_docs(docs):
    docs.register(OltDeviceapi, blueprint='oltdevices_api')    
    docs.register(InfoOltDeviceapi, blueprint='oltdevices_api')

   