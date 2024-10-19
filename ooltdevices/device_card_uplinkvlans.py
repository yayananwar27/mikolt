from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort
import re

from accessapp.authapp import auth

from .models import db, OltDevicesCardModels, OltDevicesCardUplinkModels, OltDevicesModels
from userlogin.models import AllowedSiteUserModel
from logmikolt.model import MikoltLoggingModel

from datetime import datetime
def created_time():
    dt_now = datetime.now()
    date = dt_now.strftime("%Y-%m-%d %H:%M:%S")
    return str(date)

class OltDeviceCardUplinkVlanTagSchema(Schema):
    id_uplink = fields.Integer(required=True, metadata={"description":"id Record Uplink Interface"})
    vlan_tag = fields.String(required=True, metadata={"description":"Vlan tagged ex 1,100-200"})
    

class OltDeviceCardUplinkVlanTagapi(MethodResource, Resource):
    @doc(description='Uplink Add Vlan Tag', tags=['OLT Device'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(OltDeviceCardUplinkVlanTagSchema, location=('json'))
    @auth.login_required(role=['api', 'noc', 'superadmin', 'teknisi'])
    def post(self, **kwargs):
        operator = auth.current_user()
        id_uplink = kwargs['id_uplink']

        uplink_exists = OltDevicesCardUplinkModels.query.filter_by(id=id_uplink).first()
        if uplink_exists:
            card_uplink = OltDevicesCardModels.query.filter_by(id=uplink_exists.id_card).first()
            if card_uplink:
                device_exists = OltDevicesModels.query.filter_by(id=card_uplink.id_device).first()
                if device_exists:
                    pass
                else:
                    abort(404, 'device not found')
            else:
                abort(404, 'card not found')
        else:
            abort(404, 'id uplink not found')

        
        if operator.role in ['teknisi']:
            allowed_site = AllowedSiteUserModel.query.filter_by(username=operator.username).all()
            list_allowed = []
            for _allowed in allowed_site:
                list_allowed.append(_allowed.site_id)
            found_record = OltDevicesModels.query.filter(
                OltDevicesModels.id_site.in_(list_allowed)
            ).filter_by(
                id=device_exists.id
            ).order_by(OltDevicesModels.name.asc()).first()
            if found_record:
                pass
            else:
                abort(401, "Device Not Permited")
        
        vlan_tag = kwargs['vlan_tag']
        if not re.fullmatch(r'[0-9,-]+', vlan_tag):
            abort(400, 'bad vlan tag value')

        new_vlantag = uplink_exists.add_vlan_tag(vlan_tag)

        if new_vlantag == 'success':
            detail = str(uplink_exists.to_dict())+','+vlan_tag
            new_logging = MikoltLoggingModel(
                operator.username, 
                'oltdevices-uplinkvlantag', 
                uplink_exists.id, 'added', 
                detail
                )
            db.session.add(new_logging)
            db.session.commit()

        return jsonify({'message':str(new_vlantag)})
    
    @doc(description='Uplink Delete Vlan Tag', tags=['OLT Device'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(OltDeviceCardUplinkVlanTagSchema, location=('json'))
    @auth.login_required(role=['api', 'noc', 'superadmin', 'teknisi'])
    def delete(self, **kwargs):
        operator = auth.current_user()
        id_uplink = kwargs['id_uplink']

        uplink_exists = OltDevicesCardUplinkModels.query.filter_by(id=id_uplink).first()
        if uplink_exists:
            card_uplink = OltDevicesCardModels.query.filter_by(id=uplink_exists.id_card).first()
            if card_uplink:
                device_exists = OltDevicesModels.query.filter_by(id=card_uplink.id_device).first()
                if device_exists:
                    pass
                else:
                    abort(404, 'device not found')
            else:
                abort(404, 'card not found')
        else:
            abort(404, 'id uplink not found')

        
        if operator.role in ['teknisi']:
            allowed_site = AllowedSiteUserModel.query.filter_by(username=operator.username).all()
            list_allowed = []
            for _allowed in allowed_site:
                list_allowed.append(_allowed.site_id)
            found_record = OltDevicesModels.query.filter(
                OltDevicesModels.id_site.in_(list_allowed)
            ).filter_by(
                id=device_exists.id
            ).order_by(OltDevicesModels.name.asc()).first()
            if found_record:
                pass
            else:
                abort(401, "Device Not Permited")
        
        vlan_tag = kwargs['vlan_tag']
        if not re.fullmatch(r'[0-9,-]+', vlan_tag):
            abort(400, 'bad vlan tag value')

        delete_vlantag = uplink_exists.delete_vlan_tag(vlan_tag)

        if delete_vlantag == 'success':
            detail = str(uplink_exists.to_dict())+','+vlan_tag
            new_logging = MikoltLoggingModel(
                operator.username, 
                'oltdevices-uplinkvlantag', 
                uplink_exists.id, 'deleted', 
                detail
                )
            db.session.add(new_logging)
            db.session.commit()

        return jsonify({'message':str(delete_vlantag)})
    

