from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort

from sites.models import SitesModel
from mmikrotik.models import MmikrotikModel
from userlogin.models import AllowedSiteUserModel
from accessapp.authapp import auth

from .models import db, ClientPPPModel, created_time
from dotenv import load_dotenv
import os
load_dotenv()

class ParamTarikSecretSchema(Schema):
    mikrotik_id = fields.Integer(metadata={"description":"Mikrotik ID"})
    site_id = fields.Integer(metadata={"description":"Site ID"})

class RespTarikSecretSchema(Schema):
    jml_data_added = fields.Integer(metadata={"description":"Jumlah data ditambahkan"})
    jml_data_updated = fields.Integer(metadata={"description":"Jumlah data di update"})
    jml_data_skipped = fields.Integer(metadata={"description":"Jumlah data di update"})

class TarikPPPSecretApi(MethodResource, Resource):
    @doc(description='Mikrotik Tarik Secrets', tags=['Client PPP Tools'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(ParamTarikSecretSchema, location=('json'))
    @marshal_with(RespTarikSecretSchema)
    @auth.login_required(role=['api','noc','superadmin','teknisi'])
    def post(self, **kwargs):
        if len(kwargs)>1:
            abort(400, 'To much parameter')

        operator = auth.current_user()
        current_app.logger.info('{} Sync Secret'.format(operator.username))
        if operator.role in ['teknisi']:
            allowed_site = AllowedSiteUserModel.query.filter_by(username=operator.username).all()
            list_allowed = []
            for _allowed in allowed_site:
                list_allowed.append(_allowed.site_id)

            if 'site_id' in kwargs:
                list_router = MmikrotikModel.query.filter(
                    MmikrotikModel.site_id.in_(list_allowed)
                    ).filter_by(site_id=kwargs['site_id']).all()
            elif 'mikrotik_id' in kwargs:
                list_router = MmikrotikModel.query.filter(
                    MmikrotikModel.site_id.in_(list_allowed)
                    ).filter_by(mikrotik_id=kwargs['mikrotik_id']).all()
            else:
                list_router = MmikrotikModel.query.filter(
                    MmikrotikModel.site_id.in_(list_allowed)
                    ).order_by(MmikrotikModel.name.asc()).all()

        else:
            if 'site_id' in kwargs:
                list_router = MmikrotikModel.query.filter_by(site_id=kwargs['site_id']).all()
            elif 'mikrotik_id' in kwargs:
                list_router = MmikrotikModel.query.filter_by(mikrotik_id=kwargs['mikrotik_id']).all()
            else:
                list_router = MmikrotikModel.query.order_by(MmikrotikModel.name.asc()).all()

        data_added = []
        data_updated = []
        data_skiped = []
        for router in list_router:
            list_secret = router._get_ppp_secret()
            for secret in list_secret:
                if secret['profile']==str(os.environ["PROFILE_ISOLIR_NAME"]):
                    data_skiped.append(secret)
                else:
                    name_exists = ClientPPPModel.query.filter_by(name=secret['name']).first()
                    if name_exists:
                        name_exists.configuration = 'configured'
                        name_exists.service_type = secret['service']
                        name_exists.password = secret['password']
                        name_exists.profile = secret['profile']
                        name_exists.mikrotik_id = router.mikrotik_id
                        if secret['disabled']=='true':
                            name_exists.status = 'disable'
                        else:
                            name_exists.status = 'enable'
                        try:
                            name_exists.comment = secret['comment']
                        except:
                            name_exists.comment = None
                        name_exists.ref_id = secret['id']
                        name_exists.last_update_at = created_time()
                        name_exists.last_update_by = auth.current_user()
                        data_updated.append(secret)
                        db.session.commit()
                    else:
                        if secret['disabled']=='true':
                            status = 'disable'
                        else:
                            status = 'enable'

                        comment = None
                        if 'comment' in secret:
                            comment = secret['comment']

                        add_clientppp = ClientPPPModel(
                            secret['name'],
                            status,
                            'configured',
                            secret['password'],
                            secret['profile'],
                            secret['service'],
                            router.mikrotik_id,
                            comment,
                            secret['id'],
                            auth.current_user(),
                            True
                            )
                        db.session.add(add_clientppp)
                        data_added.append(secret)
                        db.session.commit()

        data = {
            'jml_data_added':len(data_added),
            'jml_data_updated':len(data_updated),
            'jml_data_skipped':len(data_skiped),
            'data_added':data_added,
            'data_updated':data_updated,
            'data_skipped':data_skiped
        }
        
        return jsonify(data)
