from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort

from accessapp.authapp import auth

from .models import MmikrotikModel
from userlogin.models import AllowedSiteUserModel

class PPPSecretSchema(Schema):
    secret_uuid = fields.String(metadata={"description":"UUID record secret pada sistem manajemen mikrotik"})
    name = fields.String(metadata={"description":"Nama Secret"})
    password = fields.String(metadata={"description":"Password"})
    profile = fields.String(metadata={"description":"Profile"})
    service = fields.String(metadata={"description":"Service Used"})
    ref_id = fields.String(metadata={"description":"ID Record secret pada mikrotik device"})

class ListPPPSecretSchema(Schema):
    data = fields.List(fields.Nested(PPPSecretSchema))
    count = fields.Integer(metadata={"description":"Jumlah PPP Secret"}) 
    mikrotik_id = fields.Integer(metadata={"description":"Mikrotik id"})

class PPPPSecretApi(MethodResource, Resource):
    @doc(description='List PPPOE Secret', tags=['Mikrotik'], security=[{"ApiKeyAuth": []}])
    @marshal_with(ListPPPSecretSchema)
    @auth.login_required(role=['api', 'noc','superadmin','teknisi','admin'])
    def get(self, mikrotik_id):
        operator = auth.current_user()
        if operator.role in ['teknisi','admin']:
            allowed_site = AllowedSiteUserModel.query.filter_by(username=operator.username).all()
            list_allowed = []
            for _allowed in allowed_site:
                list_allowed.append(_allowed.site_id)

            if 'name' in request.args:
                name = request.args.get('name')
                if name != None:
                    data_router = MmikrotikModel.query.filter(
                    MmikrotikModel.site_id.in_(list_allowed)
                    ).filter_by(mikrotik_id=mikrotik_id).first()
                    if data_router:
                        secret_pppoe = data_router._get_ppp_secret(search_name=name)
                        return jsonify(secret_pppoe[0])
            
            data_router = MmikrotikModel.query.filter(
                    MmikrotikModel.site_id.in_(list_allowed)
                    ).filter_by(mikrotik_id=mikrotik_id).first()
            if data_router:
                secret_pppoe = data_router._get_ppp_secret()
                data = {
                    'data':secret_pppoe,
                    'count':len(secret_pppoe),
                    'mikrotik_id':mikrotik_id
                    }
                return jsonify(data)
            
            abort(404, "id not found")

        if 'name' in request.args:
            name = request.args.get('name')
            if name != None:
                data_router = MmikrotikModel.query.filter_by(mikrotik_id=mikrotik_id).first()
                if data_router:
                    secret_pppoe = data_router._get_ppp_secret(search_name=name)
                    return jsonify(secret_pppoe[0])
        
        data_router = MmikrotikModel.query.filter_by(mikrotik_id=mikrotik_id).first()
        if data_router:
            secret_pppoe = data_router._get_ppp_secret()
            data = {
                'data':secret_pppoe,
                'count':len(secret_pppoe),
                'mikrotik_id':mikrotik_id
                }
            return jsonify(data)
        
        abort(404, "id not found")


class NamePPPPSecretApi(MethodResource, Resource):
    @doc(description='Name PPPOE Secret', tags=['Mikrotik'], security=[{"ApiKeyAuth": []}])
    #@marshal_with(PPPSecretSchema)
    @auth.login_required(role=['api', 'noc','superadmin','teknisi','admin'])
    def get(self, mikrotik_id):
        pass

