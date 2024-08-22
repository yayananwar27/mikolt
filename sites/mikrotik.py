from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort

from accessapp.authapp import auth

from .models import db, SitesModel
from mmikrotik.models import MmikrotikModel
from userlogin.models import AllowedSiteUserModel
class IdSiteSchema(Schema):
   id = fields.Integer(required=True, metadata={"description":"Id Site"})

class SiteMikrotikApi(MethodResource, Resource):
    @doc(description='List mikrotik di Site', tags=['Sites'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(IdSiteSchema, location=('json'))
    @auth.login_required(role=['api','noc', 'superadmin', 'teknisi', 'admin'])
    def post(self, **kwargs):
        operator = auth.current_user()
        id_site = kwargs['id']

        if operator.role in ['teknisi', 'admin']:
            allowed_site = AllowedSiteUserModel.query.filter_by(username=operator.username).all()
            list_allowed = []
            for _allowed in allowed_site:
                list_allowed.append(_allowed.site_id)
            if id_site not in list_allowed:
                abort(401, 'Unauthorized')

        
        siteexists = SitesModel.query.filter_by(site_id=id_site).first()
        if not siteexists:
            abort(404, 'ID Site Not Exists')

        mikrotikquery = MmikrotikModel.query.filter_by(site_id=id_site).all()
        list_mikrotik = []
        for mikrotik in mikrotikquery:
            list_mikrotik.append(
                {
                    'mikrotik_id':mikrotik.mikrotik_id,
                    'name':mikrotik.name,
                    'ipaddress':mikrotik.ipaddress,
                    'site_id':mikrotik.site_id,
                }
            )
        
        return jsonify(list_mikrotik)