from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS

onutypes_api = Blueprint('onutypes_api', __name__)
CORS(onutypes_api, supports_credentials=True, resources=r'*', origins='*', methods=['GET','POST','PUT','DELETE'])
api = Api(onutypes_api)

from .onutype import OnuTypeApi

api.add_resource(OnuTypeApi, '')

def init_docs(docs):
    docs.register(OnuTypeApi, blueprint='onutypes_api')
    