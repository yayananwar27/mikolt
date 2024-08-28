from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort

from accessapp.authapp import auth

from .models import db, OnuTypesModel
from logmikolt.model import MikoltLoggingModel

class CreateOnuTypeSchema(Schema):
    name = fields.String(required=True, metadata={"description":"Name Onu"})
    pon_type = fields.String(required=True, metadata={"description":"Pon Type epon/gpon"})
    description = fields.String(required=False, allow_none=True, metadata={"description":"Description onu"})    
    max_tcont = fields.Integer(required=False, allow_none=True, metadata={"description":"Max Tcont"})
    max_gemport = fields.Integer(required=False, allow_none=True, metadata={"description":"Max Gemport"})
    max_switch = fields.Integer(required=False, allow_none=True, metadata={"description":"Max Switch per slot"})
    max_flow = fields.Integer(required=False, allow_none=True, metadata={"description":"Max flow per switch"})
    max_iphost = fields.Integer(required=False, allow_none=True, metadata={"description":"Max IP host"})
    max_pots = fields.Integer(required=False, allow_none=True, metadata={"description":"Max pots"})
    max_eth = fields.Integer(required=False, allow_none=True, metadata={"description":"Max Ethernet"})
    max_wifi = fields.Integer(required=False, allow_none=True, metadata={"description":"Max Wifi"})
    
class OnuTypeSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"id record"})
    name = fields.String(required=False, allow_none=True, metadata={"description":"Name Onu"})
    pon_type = fields.String(required=False, allow_none=True, metadata={"description":"Pon Type epon/gpon"})
    description = fields.String(required=False, allow_none=True, metadata={"description":"Description onu"})    
    max_tcont = fields.Integer(required=False, allow_none=True, metadata={"description":"Max Tcont"})
    max_gemport = fields.Integer(required=False, allow_none=True, metadata={"description":"Max Gemport"})
    max_switch = fields.Integer(required=False, allow_none=True, metadata={"description":"Max Switch per slot"})
    max_flow = fields.Integer(required=False, allow_none=True, metadata={"description":"Max flow per switch"})
    max_iphost = fields.Integer(required=False, allow_none=True, metadata={"description":"Max IP host"})
    max_pots = fields.Integer(required=False, allow_none=True, metadata={"description":"Max pots"})
    max_eth = fields.Integer(required=False, allow_none=True, metadata={"description":"Max Ethernet"})
    max_wifi = fields.Integer(required=False, allow_none=True, metadata={"description":"Max Wifi"})
    

class ListOnuTypeSchema(Schema):
    data = fields.List(fields.Nested(OnuTypeSchema))

class DeleteOnuTypeSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"id record"})


class OnuTypeApi(MethodResource, Resource):
    @doc(description='Create Onu type', tags=['OLT Onu Type'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(CreateOnuTypeSchema, location=('json'))
    @marshal_with(OnuTypeSchema, code=201)
    @auth.login_required(role=['api', 'noc', 'superadmin'])
    def post(self, **kwargs):
        operator = auth.current_user()
        
        name = kwargs['name']
        pon_type = kwargs['pon_type']
        
        name_exists = OnuTypesModel.query.filter_by(name=name).first()
        if name_exists:
            abort(409, 'name onu type exists')
        if pon_type not in ['epon','gpon']:
            abort(400, 'invalid pon type')

        new_onu_type = OnuTypesModel(
            name, 
            pon_type
        )

        if 'description' in kwargs:
            new_onu_type.description = kwargs['description']
        if 'max_tcont' in kwargs:
            new_onu_type.max_tcont = kwargs['max_tcont']
        if 'max_gemport' in kwargs:
            new_onu_type.max_gemport = kwargs['max_gemport']
        if 'max_switch' in kwargs:
            new_onu_type.max_switch = kwargs['max_switch']
        if 'max_flow' in kwargs:
            new_onu_type.max_flow = kwargs['max_flow']
        if 'max_iphost' in kwargs:
            new_onu_type.max_iphost = kwargs['max_iphost']
        if 'max_pots' in kwargs:
            new_onu_type.max_pots = kwargs['max_pots']
        if 'max_eth' in kwargs:
            new_onu_type.max_eth = kwargs['max_eth']
        if 'max_wifi' in kwargs:
            new_onu_type.max_wifi = kwargs['max_wifi']

        db.session.add(new_onu_type)
        db.session.commit()

        new_logging = MikoltLoggingModel(
            operator.username, 
            'onutypes', 
            new_onu_type.id, 'created', 
            str(new_onu_type.to_dict())
            )
        db.session.add(new_logging)
        db.session.commit()

        msg = {'message':'success',
               'data':new_onu_type.to_dict()
               }
        resp = jsonify(msg)
        resp.status_code = 201
        return resp

    @doc(description='List Onu type', tags=['OLT Onu Type'], security=[{"ApiKeyAuth": []}])
    @marshal_with(ListOnuTypeSchema)
    @auth.login_required(role=['api', 'noc', 'superadmin', 'teknisi'])
    def get(self):
        data = []
        all_record = OnuTypesModel.query.order_by(OnuTypesModel.name.asc()).all()
        if all_record:
            for record in all_record:
                data.append(record.to_dict())

        return jsonify(data)
    

    @doc(description='Update Onu type', tags=['OLT Onu Type'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(OnuTypeSchema, location=('json'))
    @marshal_with(OnuTypeSchema)
    @auth.login_required(role=['api', 'noc', 'superadmin'])
    def put(self, **kwargs):
        operator = auth.current_user()
        id = kwargs['id']

        id_exists = OnuTypesModel.query.filter_by(id=id).first()
        if not id_exists:
            abort(404, 'id not found')
        
        if 'name' in kwargs['name']:
            name_exists = OnuTypesModel.query.filter_by(name=kwargs['name']).first()
            if name_exists:
                abort(409, 'name onu type exists')
            id_exists.name = kwargs['name']

        if 'pon_type' in kwargs:
            if kwargs['pon_type'] not in ['epon','gpon']:
                abort(400, 'invalid pon type')
            id_exists.pon_type = kwargs['pon_type']
        
        if 'description' in kwargs:
            id_exists.description = kwargs['description']
        if 'max_tcont' in kwargs:
            id_exists.max_tcont = kwargs['max_tcont']
        if 'max_gemport' in kwargs:
            id_exists.max_gemport = kwargs['max_gemport']
        if 'max_switch' in kwargs:
            id_exists.max_switch = kwargs['max_switch']
        if 'max_flow' in kwargs:
            id_exists.max_flow = kwargs['max_flow']
        if 'max_iphost' in kwargs:
            id_exists.max_iphost = kwargs['max_iphost']
        if 'max_pots' in kwargs:
            id_exists.max_pots = kwargs['max_pots']
        if 'max_eth' in kwargs:
            id_exists.max_eth = kwargs['max_eth']
        if 'max_wifi' in kwargs:
            id_exists.max_wifi = kwargs['max_wifi']
        db.session.commit()

        new_logging = MikoltLoggingModel(
            operator.username, 
            'onutypes', 
            id_exists.id, 'updated', 
            str(id_exists.to_dict())
            )
        db.session.add(new_logging)
        db.session.commit()

        return jsonify({'message':'success','data':id_exists.to_dict()})
    
    @doc(description='Delete Onu type', tags=['OLT Onu Type'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(DeleteOnuTypeSchema, location=('json'))
    @marshal_with(OnuTypeSchema)
    @auth.login_required(role=['api', 'noc', 'superadmin'])
    def delete(self, **kwargs):
        operator = auth.current_user()
        id = kwargs['id']

        id_exists = OnuTypesModel.query.filter_by(id=id).first()
        if id_exists:
            data = id_exists.to_dict()
            db.session.delete(id_exists)
            db.session.commit()
            new_logging = MikoltLoggingModel(
                operator.username, 
                'onutypes', 
                id, 
                'deleted'
            )
            db.session.add(new_logging)
            db.session.commit()

            return jsonify({'message':'success','data':data})

        abort(404, 'id not found')

        