from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort

from accessapp.authapp import auth

from .models import db, OltDevicesModels
from userlogin.models import AllowedSiteUserModel

from datetime import datetime
def created_time():
    dt_now = datetime.now()
    date = dt_now.strftime("%Y-%m-%d %H:%M:%S")
    return str(date)

from .device_card import IdOltDeviceShowCardSchema

class OltDeviceListTcontapi(MethodResource, Resource):
    @doc(description='Show Olt Onu Tcont List Name', tags=['OLT Device'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(IdOltDeviceShowCardSchema, location=('json'))
    @auth.login_required(role=['api', 'noc', 'superadmin', 'teknisi'])
    def post(self, **kwargs):
        operator = auth.current_user()
        id = kwargs['id']
        data = {'message':'not found'}

        if operator.role in ['teknisi']:
            allowed_site = AllowedSiteUserModel.query.filter_by(username=operator.username).all()
            list_allowed = []
            for _allowed in allowed_site:
                list_allowed.append(_allowed.site_id)
            found_record = OltDevicesModels.query.filter(
                OltDevicesModels.id_site.in_(list_allowed)
            ).filter_by(
                id=id
            ).order_by(OltDevicesModels.name.asc()).first()

            if found_record:
             data = found_record.oltdevice_showtcont()

        else:
            found_record = OltDevicesModels.query.filter_by(id=id).first()
            if found_record:
                data = found_record.oltdevice_showtcont()

        return data
    
