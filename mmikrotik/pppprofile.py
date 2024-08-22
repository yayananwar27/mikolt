from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort

from accessapp.authapp import auth

from .models import MmikrotikModel
from userlogin.models import AllowedSiteUserModel

class PPPProfileSchema(Schema):
    id = fields.String(metadata={"description":"Id Profile pada mikrotik"})
    name = fields.String(metadata={"description":"Nama Profile"})
    local_address = fields.String(metadata={"description":"local address"})
    remote_address = fields.String(metadata={"description":"Remote address"})

class ListPPPProfileSchema(Schema):
    data = fields.List(fields.Nested(PPPProfileSchema))
    isolir_ready = fields.Bool(metadata={"description":"Isolir Ready"})

class PPPProfileApi(MethodResource, Resource):
    @doc(description='List PPPOE PRofile', tags=['Mikrotik'], security=[{"ApiKeyAuth": []}])
    @marshal_with(ListPPPProfileSchema)
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
                        profile_pppoe = data_router._get_profile_ppoe(search_name=name)
                        return jsonify(profile_pppoe[0])
            
            data_router = MmikrotikModel.query.filter(
                    MmikrotikModel.site_id.in_(list_allowed)
                    ).filter_by(mikrotik_id=mikrotik_id).first()
            if data_router:
                profile_pppoe = data_router._get_profile_ppoe()
                isolir_ready = data_router._get_profile_ppoe_isolir()
                data = {
                    'data':profile_pppoe,
                    'isolir_ready':isolir_ready['status']
                    }
                return jsonify(data)
            
            abort(404, "id not found")

        if 'name' in request.args:
            name = request.args.get('name')
            if name != None:
                data_router = MmikrotikModel.query.filter_by(mikrotik_id=mikrotik_id).first()
                if data_router:
                    profile_pppoe = data_router._get_profile_ppoe(search_name=name)
                    return jsonify(profile_pppoe[0])
        
        data_router = MmikrotikModel.query.filter_by(mikrotik_id=mikrotik_id).first()
        if data_router:
            profile_pppoe = data_router._get_profile_ppoe()
            isolir_ready = data_router._get_profile_ppoe_isolir()
            data = {
                'data':profile_pppoe,
                'isolir_ready':isolir_ready['status']
                }
            return jsonify(data)
        
        abort(404, "id not found")


class NamePPPProfileApi(MethodResource, Resource):
    @doc(description='Info PPPOE PRofile', tags=['Mikrotik'], security=[{"ApiKeyAuth": []}])
    @marshal_with(PPPProfileSchema)
    @auth.login_required(role=['api', 'noc','superadmin','teknisi','admin'])
    def get(self, mikrotik_id):
        pass