from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort

from accessapp.authapp import auth
from userlogin.models import AllowedSiteUserModel
from .models import db, OltDevicesModels

class IdOltDeviceShowVlansSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"id record Device"})


class OltDeviceVlansapi(MethodResource, Resource):
    @doc(description='Show Olt Device Vlans', tags=['OLT Device'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(IdOltDeviceShowVlansSchema, location=('json'))
    @auth.login_required(role=['api', 'noc', 'superadmin', 'teknisi'])
    def post(self, **kwargs):
        operator = auth.current_user()
        id = kwargs['id']
        data = {'message':'not found'}

        if operator.role in ['teknisi']:
            allowed_site = AllowedSiteUserModel.query.filter_by(username=operator.username).all()
            list_allowed = []
            for _allowed in allowed_site:
                list_allowed.append(_allowed.site_id)
            found_record = OltDevicesModels.query.filter(
                OltDevicesModels.id_site.in_(list_allowed)
            ).filter_by(
                id=id
            ).order_by(OltDevicesModels.name.asc()).first()

            if found_record:
                data = found_record.show_list_vlans()

        else:
            found_record = OltDevicesModels.query.filter_by(id=id).first()
            if found_record:
                data = found_record.show_list_vlans()
        
        return jsonify(data)
    
class UpdateOltDeviceVlansapi(MethodResource, Resource):
    @doc(description='Update Olt Device Vlans', tags=['OLT Device'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(IdOltDeviceShowVlansSchema, location=('json'))
    @auth.login_required(role=['api', 'noc', 'superadmin', 'teknisi'])
    def post(self, **kwargs):
        operator = auth.current_user()
        id = kwargs['id']
        data = {'message':'not found'}

        if operator.role in ['teknisi']:
            allowed_site = AllowedSiteUserModel.query.filter_by(username=operator.username).all()
            list_allowed = []
            for _allowed in allowed_site:
                list_allowed.append(_allowed.site_id)
            found_record = OltDevicesModels.query.filter(
                OltDevicesModels.id_site.in_(list_allowed)
            ).filter_by(
                id=id
            ).order_by(OltDevicesModels.name.asc()).first()

            if found_record:
                found_record.add_vlans()
            data['message']='success'

        else:
            found_record = OltDevicesModels.query.filter_by(id=id).first()
            if found_record:
                found_record.add_vlans()
                data['message']='success'
        
        return jsonify(data)