from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort

from accessapp.authapp import auth

from .models import db, OltMerkModels
from logmikolt.model import MikoltLoggingModel

class CreateOltMerkSchema(Schema):
    merk = fields.String(required=True, metadata={"description":"Merk OLT"})
    model = fields.Integer(required=True, metadata={"description":"Model OLT"})
    
class OltMerkSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"id record"})
    merk = fields.String(required=False, allow_none=True,  metadata={"description":"Merk OLT"})
    model = fields.Integer(required=False, allow_none=True,  metadata={"description":"Model OLT"})
    
class ListOltMerkSchema(Schema):
    data = fields.List(fields.Nested(OltMerkSchema))

class DeleteOltMerkSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"id record"})

class OltMerkApi(MethodResource, Resource):
    @doc(description='Create Olt Merk', tags=['OLT Master'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(CreateOltMerkSchema, location=('json'))
    @marshal_with(OltMerkSchema, code=201)
    @auth.login_required(role=['api', 'noc', 'superadmin'])
    def post(self, **kwargs):
        operator = auth.current_user()
        merk = kwargs['merk']
        model = kwargs['model']
        
        name_exists = OltMerkModels.query.filter_by(merk=merk, model=model).first()
        if name_exists:
            abort(409, 'Name Already Exists')

        new_name = OltMerkModels(
            merk, model
        )
        db.session.add(new_name)
        db.session.commit()
        new_logging = MikoltLoggingModel(
            operator.username, 
            'oltmaster-merk', 
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

    @doc(description='List Olt Merk', tags=['OLT Master'], security=[{"ApiKeyAuth": []}])
    @marshal_with(ListOltMerkSchema)
    @auth.login_required(role=['api', 'noc', 'superadmin', 'teknisi'])
    def get(self):
        data = []
        all_record = OltMerkModels.query.order_by(OltMerkModels.merk.asc()).all()
        if all_record:
            for record in all_record:
                data.append(record.to_dict())

        return jsonify(data)
    
    @doc(description='Update Olt Merk', tags=['OLT Master'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(OltMerkSchema, location=('json'))
    @marshal_with(OltMerkSchema)
    @auth.login_required(role=['api', 'noc', 'superadmin'])
    def put(self, **kwargs):
        operator = auth.current_user()
        id = kwargs['id']

        id_exists = OltMerkModels.query.filter_by(id=id).first()
        if not id_exists:
            abort(404, 'id not found')
        
        if 'merk' in kwargs:
            if 'model' in kwargs:
                name_exists = OltMerkModels.query.filter_by(merk=kwargs['merk'], model=kwargs['model']).first()
            else:
                name_exists = OltMerkModels.query.filter_by(merk=kwargs['merk'], model=id_exists.model).first()
            if name_exists:
                abort(409, 'Name Already Exists')

            id_exists.merk = kwargs['merk']
        
        if 'model' in kwargs:
            if 'merk' in kwargs:
                name_exists = OltMerkModels.query.filter_by(merk=kwargs['merk'], model=kwargs['model']).first()
            else:
                name_exists = OltMerkModels.query.filter_by(merk=id_exists.merk, model=kwargs['model']).first()
            if name_exists:
                abort(409, 'Name Already Exists')
            id_exists.model = kwargs['model']
        
        db.session.commit()

        new_logging = MikoltLoggingModel(
            operator.username, 
            'oltmaster-merk', 
            id_exists.id, 'updated', 
            str(id_exists.to_dict())
            )
        db.session.add(new_logging)
        db.session.commit()

        return jsonify({'message':'success','data':id_exists.to_dict()})
    
    @doc(description='Delete oltmerk', tags=['OLT Master'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(DeleteOltMerkSchema, location=('json'))
    @marshal_with(OltMerkSchema)
    @auth.login_required(role=['api', 'noc', 'superadmin'])
    def delete(self, **kwargs):
        operator = auth.current_user()
        id = kwargs['id']

        id_exists = OltMerkModels.query.filter_by(id=id).first()
        if id_exists:
            data = id_exists.to_dict()
            db.session.delete(id_exists)
            db.session.commit()
            new_logging = MikoltLoggingModel(
                operator.username, 
                'oltmaster-merk', 
                id, 
                'deleted'
            )
            db.session.add(new_logging)
            db.session.commit()

            return jsonify({'message':'success','data':data})

        abort(404, 'id not found')


class AvaiOltMerkSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"id record merk"})

class UpdateOltMerkSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"id record merk"})
    id_soft = fields.Integer(required=True, metadata={"description":"id record software"})

from .oltsoft import ListOltSoftSchema
from .models import OltSoftModels, OltMerkSoftModels
class OltMerkSoftAvaiApi(MethodResource, Resource):
    @doc(description='List software yang dapat menggunakan merk ini', tags=['OLT Master'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(AvaiOltMerkSchema, location=('json'))
    @marshal_with(ListOltSoftSchema)
    @auth.login_required(role=['api','noc','superadmin', 'teknisi'])
    def post(self, **kwargs):
        id_exists = OltMerkModels.query.filter_by(id=kwargs['id']).first()
        if not id_exists:
            abort(404, 'id not found')

        data = id_exists.soft_avai()
        return jsonify(data)
    
    @doc(description='Add software yang dapat menggunakan merk ini', tags=['OLT Master'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(UpdateOltMerkSchema, location=('json'))
    @marshal_with(ListOltSoftSchema)
    @auth.login_required(role=['api','noc','superadmin'])
    def put(self, **kwargs):
        id_exists = OltMerkModels.query.filter_by(id=kwargs['id']).first()
        if not id_exists:
            abort(404, 'id not found')

        id_soft_exists = OltSoftModels.query.filter_by(id=kwargs['id_soft']).first()
        if not id_soft_exists:
            abort(404, 'id not found')

        record_exists = OltMerkSoftModels.query.filter_by(id_merk=kwargs['id'], id_software=kwargs['id_soft']).first()
        if record_exists:
            abort(409, 'already exists')

        new_record = OltMerkSoftModels(kwargs['id'], kwargs['id_soft'])
        db.session.add(new_record)
        db.session.commit()    

        id_exists = OltMerkModels.query.filter_by(id=kwargs['id']).first()
        data = id_exists.soft_avai()

        operator = auth.current_user()
        new_logging = MikoltLoggingModel(
            operator.username, 
            'oltmaster-merksoft', 
            kwargs['id'], 
            'created',
            str(data)
        )
        db.session.add(new_logging)
        db.session.commit()
        return jsonify(data)
    
    @doc(description='Delete software yang dapat menggunakan merk ini', tags=['OLT Master'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(UpdateOltMerkSchema, location=('json'))
    @marshal_with(ListOltSoftSchema)
    @auth.login_required(role=['api','noc','superadmin'])
    def delete(self, **kwargs):
        record_exists = OltMerkSoftModels.query.filter_by(id_merk=kwargs['id'], id_software=kwargs['id_soft']).first()
        if not record_exists:
            abort(404, 'record not found')

        db.session.delete(record_exists)
        db.session.commit()

        id_exists = OltMerkModels.query.filter_by(id=kwargs['id']).first()
        data = id_exists.soft_avai()
        operator = auth.current_user()
        new_logging = MikoltLoggingModel(
            operator.username, 
            'oltmaster-merksoft', 
            kwargs['id'], 
            'deleted',
            str(data)
        )
        db.session.add(new_logging)
        db.session.commit()

        return jsonify({'message':'success'})