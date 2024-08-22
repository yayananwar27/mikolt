from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS

mpppprofile_api = Blueprint('mpppprofile_api', __name__)
CORS(mpppprofile_api, supports_credentials=True, resources=r'*', origins='*', methods=['GET','POST','PUT','DELETE'])
api = Api(mpppprofile_api)

from .profile import PPPProfileApi

api.add_resource(PPPProfileApi, '')

def init_docs(docs):
    docs.register(PPPProfileApi, blueprint='mpppprofile_api')