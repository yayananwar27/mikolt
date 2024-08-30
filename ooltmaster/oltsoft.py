from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort

from accessapp.authapp import auth

from .models import db, OltSoftModels
from logmikolt.model import MikoltLoggingModel

class CreateOltSoftSchema(Schema):
    name = fields.String(required=True, metadata={"description":"Name Software"})
    
class OltSoftSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"id record"})
    name = fields.String(required=False, allow_none=True,  metadata={"description":"Name Software"})
    
class ListOltSoftSchema(Schema):
    data = fields.List(fields.Nested(OltSoftSchema))

class DeleteOltSoftSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"id record"})

class OltSoftApi(MethodResource, Resource):
    @doc(description='Create Olt Software', tags=['OLT Master'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(CreateOltSoftSchema, location=('json'))
    @marshal_with(OltSoftSchema, code=201)
    @auth.login_required(role=['api'])
    def post(self, **kwargs):
        operator = auth.current_user()
        name = kwargs['merk']
        
        name_exists = OltSoftModels.query.filter_by(name=name).first()
        if name_exists:
            abort(409, 'Name Already Exists')

        new_name = OltSoftModels(
            name
        )
        db.session.add(new_name)
        db.session.commit()
        new_logging = MikoltLoggingModel(
            operator.username, 
            'oltmaster-soft', 
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

    @doc(description='List Olt Soft', tags=['OLT Master'], security=[{"ApiKeyAuth": []}])
    @marshal_with(ListOltSoftSchema)
    @auth.login_required(role=['api','noc', 'superadmin', 'teknisi'])
    def get(self):
        data = []
        all_record = OltSoftModels.query.order_by(OltSoftModels.name.asc()).all()
        if all_record:
            for record in all_record:
                data.append(record.to_dict())

        return jsonify(data)
    
    @doc(description='Update Olt Software', tags=['OLT Master'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(OltSoftSchema, location=('json'))
    @marshal_with(OltSoftSchema)
    @auth.login_required(role=['api'])
    def put(self, **kwargs):
        operator = auth.current_user()
        id = kwargs['id']

        id_exists = OltSoftModels.query.filter_by(id=id).first()
        if not id_exists:
            abort(404, 'id not found')
        
        if 'name' in kwargs['name']:
            name_exsts = OltSoftModels.query.filter_by(name=kwargs['name']).first()
            if name_exsts:
                abort(409, 'Name Exists')
            id_exists.merk = kwargs['name']
        
        db.session.commit()

        new_logging = MikoltLoggingModel(
            operator.username, 
            'oltmaster-soft', 
            id_exists.id, 'updated', 
            str(id_exists.to_dict())
            )
        db.session.add(new_logging)
        db.session.commit()

        return jsonify({'message':'success','data':id_exists.to_dict()})
    
    @doc(description='Delete olt Software', tags=['OLT Master'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(DeleteOltSoftSchema, location=('json'))
    @marshal_with(OltSoftSchema)
    @auth.login_required(role=['api'])
    def delete(self, **kwargs):
        operator = auth.current_user()
        id = kwargs['id']

        id_exists = OltSoftModels.query.filter_by(id=id).first()
        if id_exists:
            data = id_exists.to_dict()
            db.session.delete(id_exists)
            db.session.commit()
            new_logging = MikoltLoggingModel(
                operator.username, 
                'oltmaster-soft', 
                id, 
                'deleted'
            )
            db.session.add(new_logging)
            db.session.commit()

            return jsonify({'message':'success','data':data})

        abort(404, 'id not found')


class AvaiOltSoftSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"id record software"})

from .oltmerk import ListOltMerkSchema
class OltSoftMerkAvaiApi(MethodResource, Resource):
    @doc(description='List Merk yang dapat menggunakan software ini', tags=['OLT Master'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(AvaiOltSoftSchema, location=('json'))
    @marshal_with(ListOltMerkSchema)
    @auth.login_required(role=['api','noc','superadmin', 'teknisi'])
    def post(self, **kwargs):
        id_exists = OltSoftModels.query.filter_by(id=kwargs['id']).first()
        if not id_exists:
            abort(404, 'id not found')

        data = id_exists.merk_avai()
        return jsonify(data)