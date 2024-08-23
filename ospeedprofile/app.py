from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS

speedprofile_api = Blueprint('speedprofile_api', __name__)
CORS(speedprofile_api, supports_credentials=True, resources=r'*', origins='*', methods=['GET','POST','PUT','DELETE'])
api = Api(speedprofile_api)

from .tcontspeed import TcontSpeedprofileApi
from .trafficspeed import TrafficSpeedprofileApi

api.add_resource(TcontSpeedprofileApi, '/tcont')
api.add_resource(TrafficSpeedprofileApi, '/traffic')

def init_docs(docs):
    docs.register(TcontSpeedprofileApi, blueprint='speedprofile_api')
    docs.register(TrafficSpeedprofileApi, blueprint='speedprofile_api')