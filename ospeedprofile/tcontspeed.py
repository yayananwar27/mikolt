from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort

from accessapp.authapp import auth

from .models import db, TcontSpeedProfileModel
from userlogin.models import AllowedSiteUserModel
from logmikolt.model import MikoltLoggingModel

class CreateTcontSpeedProfileSchema(Schema):
    name = fields.String(required=True, metadata={"description":"Name Tcont Profile"})
    type = fields.Integer(required=True, metadata={"description":"Type Tcont 1-5"})
    fixed = fields.Integer(required=True, metadata={"description":"Fixed Bandwidth Kbps"})
    assured = fields.Integer(required=True, metadata={"description":"Assured Bandwidth Kbps"})
    maximum = fields.Integer(required=True, metadata={"description":"Maximum Bandwidth Kbps"})
    
class TcontSpeedProfileSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"id record"})
    name = fields.String(required=False, allow_none=True, metadata={"description":"Name Tcont Profile"})
    type = fields.Integer(required=False, allow_none=True, metadata={"description":"Type Tcont 1-5"})
    fixed = fields.Integer(required=False, allow_none=True, metadata={"description":"Fixed Bandwidth Kbps"})
    assured = fields.Integer(required=False, allow_none=True, metadata={"description":"Assured Bandwidth Kbps"})
    maximum = fields.Integer(required=False, allow_none=True, allow_metadata={"description":"Maximum Bandwidth Kbps"})

class ListTcontSpeedProfileSchema(Schema):
    data = fields.List(fields.Nested(TcontSpeedProfileSchema))

class DeleteTcontSpeedProfileSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"id record"})


class TcontSpeedprofileApi(MethodResource, Resource):
    @doc(description='Create Tcont Speed Profile', tags=['OLT Speed Profile'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(CreateTcontSpeedProfileSchema, location=('json'))
    @marshal_with(TcontSpeedProfileSchema)
    @auth.login_required(role=['api', 'noc', 'superadmin'])
    def post(self, **kwargs):
        operator = auth.current_user()
        name = kwargs['name']
        _type = kwargs['type']
        fixed = 0
        assured = 0
        maximum = 0

        if _type not in range(1,6):
            abort(400, 'Wrong Type Number')

        name_exists = TcontSpeedProfileModel.query.filter_by(name=name).first()
        if name_exists:
            abort(409, 'Name Already Exists')

        if 'fixed' in kwargs:
            fixed = kwargs['fixed']
        if 'assured' in kwargs:
            assured = kwargs['assured']
        if 'maximum' in kwargs:
            maximum = kwargs['maximum']

        new_name = TcontSpeedProfileModel(
            name, _type, fixed, assured, maximum
            )
        db.session.add(new_name)
        
        new_logging = MikoltLoggingModel(
            operator.username, 
            'speedprofile-tcont', 
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

    @doc(description='List Tcont Speed Profile', tags=['OLT Speed Profile'], security=[{"ApiKeyAuth": []}])
    @marshal_with(ListTcontSpeedProfileSchema)
    @auth.login_required(role=['api', 'noc', 'superadmin', 'teknisi'])
    def get(self):
        data = []
        all_record = TcontSpeedProfileModel.query.order_by(TcontSpeedProfileModel.name.asc()).all()
        if all_record:
            for record in all_record:
                data.append(record.to_dict())

        return jsonify(data)
    

    @doc(description='Update Tcont Speed Profile', tags=['OLT Speed Profile'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(TcontSpeedProfileSchema, location=('json'))
    @marshal_with(TcontSpeedProfileSchema)
    @auth.login_required(role=['api', 'noc', 'superadmin'])
    def put(self, **kwargs):
        operator = auth.current_user()
        id = kwargs['id']

        id_exists = TcontSpeedProfileModel.query.filter_by(id=id).first()
        if not id_exists:
            abort(404, 'id not found')
        
        if 'name' in kwargs:
            id_exists.name = kwargs['name']
        if 'type' in kwargs:
            if kwargs['type'] in range(1,6):
                id_exists.type = kwargs['type']
        if 'fixed' in kwargs:
            id_exists.fixed = kwargs['fixed']
        if 'assured' in kwargs:
            id_exists.assured = kwargs['assured']
        if 'maximum' in kwargs:
            id_exists.maximum = kwargs['maximum']

        db.session.commit()

        new_logging = MikoltLoggingModel(
            operator.username, 
            'speedprofile-tcont', 
            id_exists.id, 'updated', 
            str(id_exists.to_dict())
            )
        db.session.add(new_logging)
        db.session.commit()

        return jsonify({'message':'success','data':id_exists.to_dict()})
    
    @doc(description='Delete Tcont Speed Profile', tags=['OLT Speed Profile'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(DeleteTcontSpeedProfileSchema, location=('json'))
    #@marshal_with(TcontSpeedProfileSchema)
    @auth.login_required(role=['api', 'noc', 'superadmin'])
    def delete(self, **kwargs):
        operator = auth.current_user()
        id = kwargs['id']

        id_exists = TcontSpeedProfileModel.query.filter_by(id=id).first()
        if id_exists:
            db.session.delete(id_exists)
            db.session.commit()
            new_logging = MikoltLoggingModel(
                operator.username, 
                'speedprofile-tcont', 
                id, 
                'deleted'
            )
            db.session.add(new_logging)
            db.session.commit()

            return jsonify({'message':'success'})

        abort(404, 'id not found')

        