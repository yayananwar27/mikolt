from flask import Blueprint
from flask_restful import Api
from flask_cors import CORS

oltdevices_api = Blueprint('oltdevices_api', __name__)
CORS(oltdevices_api, supports_credentials=True, resources=r'*', origins='*', methods=['GET','POST','PUT','DELETE'])
api = Api(oltdevices_api)

from .device import OltDeviceapi, InfoOltDeviceapi
from .device_card import OltDeviceCardapi, OltDeviceCardPonapi, OltDeviceCardUplinkapi
from .device_onutype import OltDeviceOnuTypeapi
from .device_vlans import OltDeviceVlansapi, UpdateOltDeviceVlansapi, CudOltDeviceVlansapi
from .device_tcont import OltDeviceListTcontapi
from .device_card_uplinkvlans import OltDeviceCardUplinkVlanTagapi

api.add_resource(OltDeviceapi, '')
api.add_resource(InfoOltDeviceapi, '/info')
api.add_resource(OltDeviceCardapi, '/card')
api.add_resource(OltDeviceCardPonapi, '/card/pon')
api.add_resource(OltDeviceCardUplinkapi, '/card/uplink')
api.add_resource(OltDeviceCardUplinkVlanTagapi, '/card/uplink/vlan_tag')
api.add_resource(OltDeviceOnuTypeapi, '/onutype')
api.add_resource(OltDeviceVlansapi, '/vlan')
api.add_resource(UpdateOltDeviceVlansapi, '/vlan/sync')
api.add_resource(CudOltDeviceVlansapi, '/vlan/action')
api.add_resource(OltDeviceListTcontapi, '/tcont')

def init_docs(docs):
    docs.register(OltDeviceapi, blueprint='oltdevices_api')    
    docs.register(InfoOltDeviceapi, blueprint='oltdevices_api')
    docs.register(OltDeviceCardapi, blueprint='oltdevices_api')
    docs.register(OltDeviceCardPonapi, blueprint='oltdevices_api')
    docs.register(OltDeviceCardUplinkapi, blueprint='oltdevices_api')
    docs.register(OltDeviceCardUplinkVlanTagapi, blueprint='oltdevices_api')
    docs.register(OltDeviceOnuTypeapi, blueprint='oltdevices_api')
    docs.register(OltDeviceVlansapi, blueprint='oltdevices_api')
    docs.register(UpdateOltDeviceVlansapi, blueprint='oltdevices_api')
    docs.register(CudOltDeviceVlansapi, blueprint='oltdevices_api')
    docs.register(OltDeviceListTcontapi, blueprint='oltdevices_api')
    