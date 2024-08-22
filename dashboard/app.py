from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS

dashboard_api = Blueprint('dashboard_api', __name__)
CORS(dashboard_api, supports_credentials=True, resources=r'*', origins='*', methods=['GET','POST','PUT','DELETE'])
api = Api(dashboard_api)

from .summary import DashboardSummaryApi, DashboardClientConSummaryApi

api.add_resource(DashboardSummaryApi, '')
api.add_resource(DashboardClientConSummaryApi, '/clientconnected')


def init_docs(docs):
    docs.register(DashboardSummaryApi, blueprint='dashboard_api')
    docs.register(DashboardClientConSummaryApi, blueprint='dashboard_api')