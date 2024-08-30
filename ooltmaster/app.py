from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS

oltmaster_api = Blueprint('oltmaster_api', __name__)
CORS(oltmaster_api, supports_credentials=True, resources=r'*', origins='*', methods=['GET','POST','PUT','DELETE'])
api = Api(oltmaster_api)

from .oltmerk import OltMerkApi, OltMerkSoftAvaiApi
from .oltsoft import OltSoftApi, OltSoftMerkAvaiApi

api.add_resource(OltMerkApi, '/merk')
api.add_resource(OltMerkSoftAvaiApi, '/merk/software')
api.add_resource(OltSoftApi, '/software')
api.add_resource(OltSoftMerkAvaiApi, '/software/merk')

def init_docs(docs):
    docs.register(OltMerkApi, blueprint='oltmaster_api')
    docs.register(OltMerkSoftAvaiApi, blueprint='oltmaster_api')
    docs.register(OltSoftApi, blueprint='oltmaster_api')
    docs.register(OltSoftMerkAvaiApi, blueprint='oltmaster_api')
    