from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort

from accessapp.authapp import auth
from userlogin.models import AllowedSiteUserModel
from .models import db, OltDevicesModels, OltDevicesVlansModels
from logmikolt.model import MikoltLoggingModel

class IdOltDeviceShowVlansSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"id record Device"})

class CreateDeviceVlanSchema(Schema):
    device_id = fields.Integer(required=True, metadata={"description":"id record Device"})
    vlan_id = fields.Integer(required=True, metadata={"description":"Vlan ID to created"})
    name = fields.String(required=False, allow_none=True, metadata={"description":"Vlan Name"})
    description = fields.String(required=False, allow_none=True, metadata={"description":"Vlan Description"})

class UpdateDeviceVlanSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"id record vlan"})
    name = fields.String(required=False, allow_none=True, metadata={"description":"Vlan Name"})
    description = fields.String(required=False, allow_none=True, metadata={"description":"Vlan Description"})

class IdDeviceVlanSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"id record vlan"})


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
    @doc(description='Sync Olt Device Vlans', tags=['OLT Device'], security=[{"ApiKeyAuth": []}])
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


class CudOltDeviceVlansapi(MethodResource, Resource):
    @doc(description='Create Olt Device Vlans', tags=['OLT Device'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(CreateDeviceVlanSchema, location=('json'))
    @auth.login_required(role=['api', 'noc', 'superadmin'])
    def post(self, **kwargs):
        operator = auth.current_user()
        vlan_id = kwargs['vlan_id']
        device_id = kwargs['device_id']
        name = None
        desc = None
        message = {'message':'failed'}

        vlan_exists = OltDevicesVlansModels.query.filter_by(
            id_device = device_id,
            vlan_id = vlan_id
        ).first()
        if vlan_exists:
            abort(409, 'Vlan Already Exists')

        device_exists = OltDevicesModels.query.filter_by(
            id=device_id
        ).first()
        if not device_exists:
            abort(404, 'Device ID Not Found')

        if 'name' in kwargs:
            name = kwargs['name']
        
        if 'description' in kwargs:
            desc = kwargs['description']

        data = {
            'vlan_id':vlan_id,
            'vlan_name':name,
            'vlan_desc': desc
        }

        add_vlan = device_exists.add_device_vlan(data)
        if add_vlan != 'success':
            message['message'] = add_vlan
            return message

        new_vlan = OltDevicesVlansModels(
            device_id,
            vlan_id,
            name,
            desc
        )
        db.session.add(new_vlan)
        db.session.commit()

        new_logging = MikoltLoggingModel(
            operator.username, 
            'oltdevices-devicevlan', 
            device_id, 'added', 
            str(new_vlan.to_dict())
        )
        db.session.add(new_logging)
        db.session.commit()

        message['message'] = 'success' 
        return message
    
    @doc(description='Update Olt Device Vlans', tags=['OLT Device'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(UpdateDeviceVlanSchema, location=('json'))
    @auth.login_required(role=['api', 'noc', 'superadmin'])
    def put(self, **kwargs):
        operator = auth.current_user()
        id = kwargs['id']
        name = None
        desc = None
        message = {'message':'failed'}

        vlan_exists = OltDevicesVlansModels.query.filter_by(
            id = id
        ).first()
        if not vlan_exists:
            abort(404, 'Vlan Record Not Exists')
        
        device_exists = OltDevicesModels.query.filter_by(
            id=vlan_exists.id_device
        ).first()

        if 'name' in kwargs:
            name = kwargs['name']
        
        if 'description' in kwargs:
            desc = kwargs['description']

        data = {
            'vlan_id':vlan_exists.vlan_id,
            'vlan_name':name,
            'vlan_desc': desc
        }

        update_vlan = device_exists.update_device_vlan(data)
        if update_vlan != 'success':
            message['message'] = update_vlan
            return message

        if 'name' in kwargs:
            vlan_exists.name = kwargs['name']
        
        if 'description' in kwargs:
            vlan_exists.description = kwargs['description']

        db.session.commit()

        new_logging = MikoltLoggingModel(
            operator.username, 
            'oltdevices-devicevlan', 
            vlan_exists.id_device, 'updated', 
            str(vlan_exists.to_dict())
        )
        db.session.add(new_logging)
        db.session.commit()
        message['message'] = 'success'
        return message
    
    @doc(description='Delete Olt Device Vlans', tags=['OLT Device'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(IdDeviceVlanSchema, location=('json'))
    @auth.login_required(role=['api', 'noc', 'superadmin'])
    def delete(self, **kwargs):
        operator = auth.current_user()
        id = kwargs['id']
        message = {'message':'failed'}

        vlan_exists = OltDevicesVlansModels.query.filter_by(
            id = id
        ).first()
        if not vlan_exists:
            abort(404, 'Vlan Record Not Exists')
        
        device_exists = OltDevicesModels.query.filter_by(
            id=vlan_exists.id_device
        ).first()

        delete_vlan = device_exists.delete_device_vlan(vlan_exists.vlan_id)
        if delete_vlan != 'success':
            message['message'] = delete_vlan
            return message
        
        new_logging = MikoltLoggingModel(
            operator.username, 
            'oltdevices-devicevlan', 
            vlan_exists.id_device, 'updated', 
            str(vlan_exists.to_dict())
        )
        db.session.add(new_logging)
        db.session.commit()
        
        db.session.delete(vlan_exists)
        db.session.commit()

        message['message'] = 'success'
        return message