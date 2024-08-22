from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort

from accessapp.authapp import auth

from mmikrotik.models import MmikrotikModel

from mmikrotik.pppprofile import PPPProfileSchema, ListPPPProfileSchema
from userlogin.models import AllowedSiteUserModel

class ViewPPPProfileSchema(Schema):
    mikrotik_id = fields.Integer(metadata={"description":"Mikrotik id"})
    mikrotik_id_list = fields.List(fields.Integer(metadata={"description":"Mikrotik id"}))
    site_id = fields.Integer(metadata={"description":"id Site"})
    site_id_list = fields.List(fields.Integer(metadata={"description":"Nama Site"}))

class PPPProfileApi(MethodResource, Resource):
    @doc(description='List PPPOE PRofile gunakan salah satu param jika ingin spesfied', tags=['PPP Profile'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(ViewPPPProfileSchema, location=('json'))
    @marshal_with(ListPPPProfileSchema)
    @auth.login_required(role=['api', 'noc', 'superadmin', 'teknisi', 'admin'])
    def post(self, **kwargs):
        if len(kwargs)>1:
            abort(400, "To much Parameter")

        operator = auth.current_user()
        if operator.role in ['teknisi', 'admin']:
            allowed_site = AllowedSiteUserModel.query.filter_by(username=operator.username).all()
            list_allowed = []
            for _allowed in allowed_site:
                list_allowed.append(_allowed.site_id)
            
            if 'mikrotik_id' in kwargs:
                data_router = MmikrotikModel.query.filter(
                    MmikrotikModel.site_id.in_(list_allowed)
                    ).filter_by(
                        mikrotik_id=kwargs['mikrotik_id']
                        ).all()
            elif 'site_id' in kwargs:
                data_router = MmikrotikModel.query.filter(
                    MmikrotikModel.site_id.in_(list_allowed)
                    ).filter_by(site_id=kwargs['site_id']).all()
            elif 'mikrotik_id_list' in kwargs:
                data_router = MmikrotikModel.query.filter(
                    MmikrotikModel.site_id.in_(list_allowed),
                    MmikrotikModel.mikrotik_id.in_(kwargs['mikrotik_id_list'])
                    ).all()
            elif 'site_id_list' in kwargs:
                data_router = MmikrotikModel.query.filter(
                    MmikrotikModel.site_id.in_(list_allowed),
                    MmikrotikModel.mikrotik_id.in_(kwargs['site_id_list'])).all()
            else:
                data_router = MmikrotikModel.query.filter(
                    MmikrotikModel.site_id.in_(list_allowed)
                    ).order_by(MmikrotikModel.name.asc()).all()
        
        else:
            if 'mikrotik_id' in kwargs:
                data_router = MmikrotikModel.query.filter_by(mikrotik_id=kwargs['mikrotik_id']).all()
            elif 'site_id' in kwargs:
                data_router = MmikrotikModel.query.filter_by(site_id=kwargs['site_id']).all()
            elif 'mikrotik_id_list' in kwargs:
                data_router = MmikrotikModel.query.filter(MmikrotikModel.mikrotik_id.in_(kwargs['mikrotik_id_list'])).all()
            elif 'site_id_list' in kwargs:
                data_router = MmikrotikModel.query.filter(MmikrotikModel.mikrotik_id.in_(kwargs['site_id_list'])).all()
            else:
                data_router = MmikrotikModel.query.order_by(MmikrotikModel.name.asc()).all()
        
        _list_data = []
        for router in data_router:
            profile_pppoe = router._get_profile_ppoe()
            if profile_pppoe != None:
                _list_data = _list_data + profile_pppoe

        unique_names = set()
        list_data = []
        for d in _list_data:
            if d['name'] not in unique_names:
                unique_names.add(d['name'])
                list_data.append(d)

        data = {
            'data':list_data
        }
        return jsonify(data)

        
