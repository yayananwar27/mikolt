from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort

from accessapp.authapp import auth

from .models import db, OltDevicesModels, OltDevicesCardModels
from logmikolt.model import MikoltLoggingModel
from sites.models import SitesModel
from userlogin.models import AllowedSiteUserModel

from datetime import datetime
def created_time():
    dt_now = datetime.now()
    date = dt_now.strftime("%Y-%m-%d %H:%M:%S")
    return str(date)

class CreateOltDeviceSchema(Schema):
    name = fields.String(required=True, metadata={"description":"Name OLT"})
    host = fields.String(required=True, metadata={"description":"Host/IP OLT"})
    telnet_user = fields.String(required=True, metadata={"description":"Telnet Username OLT"})
    telnet_pass = fields.String(required=True, metadata={"description":"Telnet Password OLT"})
    telnet_port = fields.Integer(required=True, metadata={"description":"Telnet Port OLT"})
    snmp_ro_com = fields.String(required=True, metadata={"description":"SNMP RO Community OLT"})
    snmp_wr_com = fields.String(required=True, metadata={"description":"SNMP RW Community OLT"})
    snmp_port = fields.Integer(required=True, metadata={"description":"SNMP PORT"})
    id_site = fields.Integer(required=True, metadata={"description":"id site"})
    id_merk = fields.Integer(required=True, metadata={"description":"id merk"})
    id_software = fields.Integer(required=True, metadata={"description":"id software"})

class OltDeviceSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"id record"})
    name = fields.String(required=True, metadata={"description":"Name OLT"})
    host = fields.String(required=True, metadata={"description":"Host/IP OLT"})
    telnet_user = fields.String(required=True, metadata={"description":"Telnet Username OLT"})
    telnet_pass = fields.String(required=True, metadata={"description":"Telnet Password OLT"})
    telnet_port = fields.Integer(required=True, metadata={"description":"Telnet Port OLT"})
    snmp_ro_com = fields.String(required=True, metadata={"description":"SNMP RO Community OLT"})
    snmp_wr_com = fields.String(required=True, metadata={"description":"SNMP RW Community OLT"})
    snmp_port = fields.Integer(required=True, metadata={"description":"SNMP PORT"})
    id_site = fields.Integer(required=True, metadata={"description":"id site"})
    id_merk = fields.Integer(required=True, metadata={"description":"id merk"})
    id_software = fields.Integer(required=True, metadata={"description":"id software"})

class ListOltDeviceSchema(Schema):
    data = fields.List(fields.Nested(OltDeviceSchema))

class DeleteOltDeviceSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"id record"})

class OltDeviceapi(MethodResource, Resource):
    @doc(description='Create Olt Device', tags=['OLT Device'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(CreateOltDeviceSchema, location=('json'))
    @marshal_with(OltDeviceSchema, code=201)
    @auth.login_required(role=['api', 'noc', 'superadmin'])
    def post(self, **kwargs):
        operator = auth.current_user()
        name = kwargs['name']
        
        name_exists = OltDevicesModels.query.filter_by(name=name).first()
        if name_exists:
            abort(409, 'Name Already Exists')

        id_site_exists = SitesModel.query.filter_by(site_id=kwargs['id_site']).first()
        if not id_site_exists:
            abort(400, 'id site not found')

        new_name = OltDevicesModels(
            name, 
            kwargs['host'], 
            kwargs['telnet_user'],
            kwargs['telnet_pass'],
            kwargs['telnet_port'],
            kwargs['snmp_ro_com'],
            kwargs['snmp_wr_com'],
            kwargs['snmp_port'],
            kwargs['id_site'],
            kwargs['id_merk'],
            kwargs['id_software']
        )
        db.session.add(new_name)
        db.session.commit()

        new_name.add_list_card()
        new_name.add_vlans()
        #new_name.sync_onu_configured_from_olt()

        new_logging = MikoltLoggingModel(
            operator.username, 
            'oltdevices-device', 
            new_name.id, 'created', 
            str(new_name.to_dict())
            )
        db.session.add(new_logging)
        db.session.commit()
        

        msg = {'message':'success',
               'data':new_name.to_dict()
               }
        resp = jsonify(msg)
        resp.status_code = 201
        return resp

    @doc(description='List Olt Device', tags=['OLT Device'], security=[{"ApiKeyAuth": []}])
    @marshal_with(ListOltDeviceSchema)
    @auth.login_required(role=['api','noc', 'superadmin', 'teknisi'])
    def get(self):
        operator = auth.current_user()
        data = []

        if operator.role in ['teknisi']:
            allowed_site = AllowedSiteUserModel.query.filter_by(username=operator.username).all()
            list_allowed = []
            for _allowed in allowed_site:
                list_allowed.append(_allowed.site_id)
            all_record = OltDevicesModels.query.filter(
                OltDevicesModels.id_site.in_(list_allowed)
            ).order_by(OltDevicesModels.name.asc()).all()
        
        else:
            all_record = OltDevicesModels.query.order_by(OltDevicesModels.name.asc()).all()
        if all_record:
            for record in all_record:
                if operator.role in ['teknisi']:
                    _record = record.to_dict()
                    _record['telnet_user'] = None
                    _record['telnet_pass'] = None
                    _record['telnet_port'] = None
                    _record['snmp_ro_com'] = None
                    _record['snmp_wr_com'] = None
                    _record['snmp_port'] = None
                    data.append(_record)
                else:
                    data.append(record.to_dict())

        return jsonify(data)
    
    @doc(description='Update Olt Device', tags=['OLT Device'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(OltDeviceSchema, location=('json'))
    @marshal_with(OltDeviceSchema)
    @auth.login_required(role=['api', 'noc', 'superadmin'])
    def put(self, **kwargs):
        operator = auth.current_user()
        id = kwargs['id']

        id_exists = OltDevicesModels.query.filter_by(id=id).first()
        if not id_exists:
            abort(404, 'id not found')
        
        id_exists.name = kwargs['name'] 
        id_exists.host = kwargs['host'] 
        id_exists.telnet_user = kwargs['telnet_user']
        id_exists.telnet_pass = kwargs['telnet_pass']
        id_exists.telnet_port = kwargs['telnet_port']
        id_exists.snmp_ro_com = kwargs['snmp_ro_com']
        id_exists.snmp_wr_com = kwargs['snmp_wr_com']
        id_exists.snmp_port = kwargs['snmp_port']
        id_exists.id_site = kwargs['id_site']
        id_exists.id_merk = kwargs['id_merk']
        id_exists.id_software = kwargs['id_software']

        db.session.commit()

        new_logging = MikoltLoggingModel(
            operator.username, 
            'oltdevices-device', 
            id_exists.id, 'updated', 
            str(id_exists.to_dict())
            )
        db.session.add(new_logging)
        db.session.commit()

        return jsonify({'message':'success','data':id_exists.to_dict()})
    
    @doc(description='Delete olt Device', tags=['OLT Device'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(DeleteOltDeviceSchema, location=('json'))
    @marshal_with(OltDeviceSchema)
    @auth.login_required(role=['api', 'noc', 'superadmin'])
    def delete(self, **kwargs):
        operator = auth.current_user()
        id = kwargs['id']

        id_exists = OltDevicesModels.query.filter_by(id=id).first()
        if id_exists:
            #delete card 
            # list_card = OltDevicesCardModels.query.filter_by(id_device=id).all()
            # for card in list_card:
            #     db.session.delete(card)
            #     db.session.commit()
            id_exists.delete_list_card()

            data = id_exists.to_dict()
            db.session.delete(id_exists)
            db.session.commit()
            new_logging = MikoltLoggingModel(
                operator.username, 
                'oltdevices-device', 
                id, 
                'deleted'
            )
            db.session.add(new_logging)
            db.session.commit()

            return jsonify({'message':'success','data':data})

        abort(404, 'id not found')



class InfoOltDeviceapi(MethodResource, Resource):
    @doc(description='Info Olt Device', tags=['OLT Device'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(DeleteOltDeviceSchema, location=('json'))
    #@marshal_with(OltDeviceSchema)
    @auth.login_required(role=['api', 'noc', 'superadmin', 'teknisi'])
    def post(self, **kwargs):
        operator = auth.current_user()
        id = kwargs['id']
        data = None

        if operator.role in ['teknisi']:
            allowed_site = AllowedSiteUserModel.query.filter_by(username=operator.username).all()
            list_allowed = []
            for _allowed in allowed_site:
                list_allowed.append(_allowed.site_id)
            found_record = OltDevicesModels.query.filter(
                OltDevicesModels.id_site.in_(list_allowed)
            ).order_by(OltDevicesModels.name.asc()).first()
        else:
            found_record = OltDevicesModels.query.filter_by(id=id).first()
        if found_record:
            if operator.role in ['teknisi']:
                data = found_record.to_dict_info()
                data['telnet_user'] = None
                data['telnet_pass'] = None
                data['telnet_port'] = None
                data['snmp_ro_com'] = None
                data['snmp_wr_com'] = None
                data['snmp_port'] = None
            else:
                data = found_record.to_dict_info()
        return data