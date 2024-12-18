from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort
from sqlalchemy import or_, and_

from accessapp.authapp import auth

from .models import db, OltOnuConfiguredModels, OltOnuStatusHistoryModels

from logmikolt.model import MikoltLoggingModel
from sites.models import SitesModel
from userlogin.models import AllowedSiteUserModel

from ooltdevices.models import OltDevicesModels

class IdOnuConfiguredSchema(Schema):
    id = fields.Integer(metadata={'description':'id record'})

class OnuConfiguredSchema(Schema):
    id = fields.Integer(metadata={'description':'id record'})
    id_device = fields.Integer(metadata={'description':'id record device'})
    name_device = fields.String(metadata={'description':'name device'})
    id_card = fields.Integer(metadata={'description':'id record card'})
    id_cardpon = fields.Integer(metadata={'description':'id record card pon'})
    id_cardpononu = fields.Integer(metadata={'description':'id record onu'})
    onu = fields.String(metadata={'description':'name gpon onu interface'})
    sn = fields.String(metadata={'description':'Onu SN number'})
    onu_type = fields.String(metadata={'description':'onu type'})
    site_id = fields.Integer(metadata={'description':'id record site'})
    site_name = fields.String(metadata={'description':'name site'})
    name = fields.String(metadata={'description':'onu name'})
    description = fields.String(metadata={'description':'onu description'})

class ListOnuConfiguredSchema(Schema):
    data = fields.List(fields.Nested(OnuConfiguredSchema))
    total = fields.Integer(metadata={'description':'total data'})
    pages = fields.Integer(metadata={'description':'total pages'})
    current_page = fields.Integer(metadata={'description':'curent pages'})
    per_page = fields.Integer(metadata={'description':'data per pages'})

class OnuConfiguredApi(MethodResource, Resource):
    @doc(description='List Onu configured', tags=['OLT Onu'], security=[{"ApiKeyAuth": []}])
    @marshal_with(ListOnuConfiguredSchema)
    @auth.login_required(role=['api','noc', 'superadmin', 'teknisi','admin'])
    def get(self):
        operator = auth.current_user()
        list_device = []
        
        if operator.role in ['teknisi','admin']:
            allowed_site = AllowedSiteUserModel.query.filter_by(username=operator.username).all()
            list_allowed = []
            for _allowed in allowed_site:
                list_allowed.append(_allowed.site_id)
            device_list = OltDevicesModels.query.filter(
                OltDevicesModels.id_site.in_(list_allowed)
            ).all()
            for _allowed in device_list:
                list_device.append(_allowed.id)
        else:
            device_list = OltDevicesModels.query.all()
            for _allowed in device_list:
                list_device.append(_allowed.id)

        #get data server side
        if ('page' in request.args and 'per_page' in request.args) or 'search' in request.args:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            search = request.args.get('search', '', type=str)
            query = OltOnuConfiguredModels.query

            query = query.filter(
                OltOnuConfiguredModels.id_device.in_(list_device)
                )

            search_filter = or_(
                OltOnuConfiguredModels.name.like(f'%{search}%'),
                OltOnuConfiguredModels.description.like(f'%{search}%'),
                OltOnuConfiguredModels.sn.like(f'%{search}%'),
            )
            query = query.filter(search_filter)
            
            pagination = query.paginate(page=page, per_page=per_page,error_out=False)
        else:
            query = OltOnuConfiguredModels.query
            query = query.filter(
                OltOnuConfiguredModels.id_device.in_(list_device)
                )
            query2 = query.all()
            pagination = query.paginate(page=1, per_page=len(query2),error_out=False)

        _data = [onu.to_dict() for onu in pagination.items]

        return jsonify({
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': pagination.page,
            'per_page': pagination.per_page,
            'data': _data
        })
    

class InfoOnuConfiguredApi(MethodResource, Resource):
    @doc(description='Info Onu configured', tags=['OLT Onu'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(IdOnuConfiguredSchema, location=('json'))
    @auth.login_required(role=['api','noc', 'superadmin', 'teknisi','admin'])
    def post(self, **kwargs):
        operator = auth.current_user()
        list_device = []
        
        if operator.role in ['teknisi','admin']:
            allowed_site = AllowedSiteUserModel.query.filter_by(username=operator.username).all()
            list_allowed = []
            for _allowed in allowed_site:
                list_allowed.append(_allowed.site_id)
            device_list = OltDevicesModels.query.filter(
                OltDevicesModels.id_site.in_(list_allowed)
            ).all()
            for _allowed in device_list:
                list_device.append(_allowed.id)
        else:
            device_list = OltDevicesModels.query.all()
            for _allowed in device_list:
                list_device.append(_allowed.id)

        id_onu = kwargs['id']
        data_onu = OltOnuConfiguredModels.query.filter(
                OltOnuConfiguredModels.id_device.in_(list_device)
            ).filter_by(id=id_onu).first()
        
        data = data_onu.info_to_dict()
        return jsonify(data)

class InfoOnuConfiguredStatusRawApi(MethodResource, Resource):
    @doc(description='Info Onu configured Status RAW', tags=['OLT Onu'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(IdOnuConfiguredSchema, location=('json'))
    @auth.login_required(role=['api','noc', 'superadmin', 'teknisi','admin'])
    def post(self, **kwargs):
        operator = auth.current_user()
        list_device = []
        
        if operator.role in ['teknisi','admin']:
            allowed_site = AllowedSiteUserModel.query.filter_by(username=operator.username).all()
            list_allowed = []
            for _allowed in allowed_site:
                list_allowed.append(_allowed.site_id)
            device_list = OltDevicesModels.query.filter(
                OltDevicesModels.id_site.in_(list_allowed)
            ).all()
            for _allowed in device_list:
                list_device.append(_allowed.id)
        else:
            device_list = OltDevicesModels.query.all()
            for _allowed in device_list:
                list_device.append(_allowed.id)

        id_onu = kwargs['id']
        data_onu = OltOnuConfiguredModels.query.filter(
                OltOnuConfiguredModels.id_device.in_(list_device)
            ).filter_by(id=id_onu).first()
        
        raw_status = OltOnuStatusHistoryModels.query.filter_by(
            id_onu=data_onu.id
        ).order_by(OltOnuStatusHistoryModels.timestamp.desc()).first()
        
        data = raw_status.out_raw()
        return jsonify(data)
