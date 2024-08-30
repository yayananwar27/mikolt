from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS

oltmaster_api = Blueprint('oltmaster_api', __name__)
CORS(oltmaster_api, supports_credentials=True, resources=r'*', origins='*', methods=['GET','POST','PUT','DELETE'])
api = Api(oltmaster_api)

from .oltmerk import OltMerkApi

api.add_resource(OltMerkApi, '/merk')

def init_docs(docs):
    docs.register(OltMerkApi, blueprint='oltmaster_api')
    