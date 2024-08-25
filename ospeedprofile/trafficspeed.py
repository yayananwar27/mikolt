from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort

from accessapp.authapp import auth

from .models import db, TrafficSpeedProfileModel
from userlogin.models import AllowedSiteUserModel
from logmikolt.model import MikoltLoggingModel

class CreateTrafficSpeedProfileSchema(Schema):
    name = fields.String(required=True, metadata={"description":"Name Traffic Profile"})
    sir = fields.Integer(required=True, metadata={"description":"SIR Bandwidth Kbps"})
    pir = fields.Integer(required=True, metadata={"description":"PIR Bandwidth Kbps"})
    cbs = fields.Integer(required=True, metadata={"description":"CBS Bandwidth Kbps"})
    pbs = fields.Integer(required=True, metadata={"description":"PBS Bandwidth Kbps"})
    
class TrafficSpeedProfileSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"id record"})
    name = fields.String(required=False, allow_none=True, metadata={"description":"Name Traffic Profile"})
    sir = fields.Integer(required=False, allow_none=True, metadata={"description":"SIR Bandwidth Kbps"})
    pir = fields.Integer(required=False, allow_none=True, metadata={"description":"PIR Bandwidth Kbps"})
    cbs = fields.Integer(required=False, allow_none=True, metadata={"description":"CBS Bandwidth Kbps"})
    pbs = fields.Integer(required=False, allow_none=True, metadata={"description":"PBS Bandwidth Kbps"})
    
class ListTrafficSpeedProfileSchema(Schema):
    data = fields.List(fields.Nested(TrafficSpeedProfileSchema))

class DeleteTrafficSpeedProfileSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"id record"})

class TrafficSpeedprofileApi(MethodResource, Resource):
    @doc(description='Create Traffic Speed Profile', tags=['OLT Speed Profile'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(CreateTrafficSpeedProfileSchema, location=('json'))
    @marshal_with(TrafficSpeedProfileSchema)
    @auth.login_required(role=['api', 'noc', 'superadmin'])
    def post(self, **kwargs):
        operator = auth.current_user()
        name = kwargs['name']        
        sir = 0
        pir = 0
        cbs = 0
        pbs = 0
        
        name_exists = TrafficSpeedProfileModel.query.filter_by(name=name).first()
        if name_exists:
            abort(409, 'Name Already Exists')

        if 'sir' in kwargs:
            sir = kwargs['sir']
        if 'pir' in kwargs:
            pir = kwargs['pir']
        if 'cbs' in kwargs:
            cbs = kwargs['cbs']
        if 'pbs' in kwargs:
            pbs = kwargs['pbs']
        

        new_name = TrafficSpeedProfileModel(
            name, sir, pir, cbs, pbs
        )
        db.session.add(new_name)
        db.session.commit()
        new_logging = MikoltLoggingModel(
            operator.username, 
            'speedprofile-traffic', 
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

    @doc(description='List Traffic Speed Profile', tags=['OLT Speed Profile'], security=[{"ApiKeyAuth": []}])
    @marshal_with(ListTrafficSpeedProfileSchema)
    @auth.login_required(role=['api', 'noc', 'superadmin', 'teknisi'])
    def get(self):
        data = []
        all_record = TrafficSpeedProfileModel.query.order_by(TrafficSpeedProfileModel.name.asc()).all()
        if all_record:
            for record in all_record:
                data.append(record.to_dict())

        return jsonify(data)
    
    @doc(description='Update Traffic Speed Profile', tags=['OLT Speed Profile'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(TrafficSpeedProfileSchema, location=('json'))
    @marshal_with(TrafficSpeedProfileSchema)
    @auth.login_required(role=['api', 'noc', 'superadmin'])
    def put(self, **kwargs):
        operator = auth.current_user()
        id = kwargs['id']

        id_exists = TrafficSpeedProfileModel.query.filter_by(id=id).first()
        if not id_exists:
            abort(404, 'id not found')
        
        if 'name' in kwargs:
            name_exists = TrafficSpeedProfileModel.query.filter_by(name=kwargs['name']).first()
            if name_exists:
                abort(409, 'Name Exists')
            id_exists.name = kwargs['name']
        if 'sir' in kwargs:
            id_exists.sir = kwargs['sir']
        if 'pir' in kwargs:
            id_exists.pir = kwargs['pir']
        if 'cbs' in kwargs:
            id_exists.cbs = kwargs['cbs']
        if 'pbs' in kwargs:
            id_exists.pbs = kwargs['pbs']
        
        db.session.commit()

        new_logging = MikoltLoggingModel(
            operator.username, 
            'speedprofile-traffic', 
            id_exists.id, 'updated', 
            str(id_exists.to_dict())
            )
        db.session.add(new_logging)
        db.session.commit()

        return jsonify({'message':'success','data':id_exists.to_dict()})
    
    @doc(description='Delete Traffic Speed Profile', tags=['OLT Speed Profile'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(DeleteTrafficSpeedProfileSchema, location=('json'))
    @marshal_with(TrafficSpeedProfileSchema)
    @auth.login_required(role=['api', 'noc', 'superadmin'])
    def delete(self, **kwargs):
        operator = auth.current_user()
        id = kwargs['id']

        id_exists = TrafficSpeedProfileModel.query.filter_by(id=id).first()
        if id_exists:
            data = id_exists.to_dict()
            db.session.delete(id_exists)
            db.session.commit()
            new_logging = MikoltLoggingModel(
                operator.username, 
                'speedprofile-traffic', 
                id, 
                'deleted'
            )
            db.session.add(new_logging)
            db.session.commit()

            return jsonify({'message':'success','data':data})

        abort(404, 'id not found')

        