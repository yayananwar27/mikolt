from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS

userlogin_api = Blueprint('userlogin_api', __name__)
CORS(userlogin_api, supports_credentials=True, resources=r'*', origins='*', methods=['GET','POST','PUT','DELETE'])
api = Api(userlogin_api)

from .users import UserLoginApi, InfoUserLoginApi
from .login import LoginUserLoginApi, RefreshUserTokenApi
from .usersite import UserAllowedSiteApi

api.add_resource(UserLoginApi, '')
api.add_resource(InfoUserLoginApi, '?username=<username>')
api.add_resource(LoginUserLoginApi, '/login')
api.add_resource(RefreshUserTokenApi, '/@refresh_token')
api.add_resource(UserAllowedSiteApi, '/siteallowed')

def init_docs(docs):
    docs.register (UserLoginApi, blueprint='userlogin_api')
    docs.register (InfoUserLoginApi, blueprint='userlogin_api')
    docs.register (LoginUserLoginApi, blueprint='userlogin_api')
    docs.register (RefreshUserTokenApi, blueprint='userlogin_api')
    docs.register (UserAllowedSiteApi, blueprint='userlogin_api')
