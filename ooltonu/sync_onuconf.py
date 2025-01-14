from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort
from marshmallow import Schema, fields
from extensions import scheduler

from accessapp.authapp import auth

from ooltdevices.models import OltDevicesModels

class SyncOnuConfiguredSchema(Schema):
    id_device = fields.Integer(metadata={'description':'id record device'})

class SyncOnuConfiguredFromOltApi(MethodResource, Resource):
    @doc(description='Sync Onu configured From OLT', tags=['OLT Onu'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(SyncOnuConfiguredSchema)
    @auth.login_required(role=['api','noc', 'superadmin'])
    def post(self, **kwargs):
        operator = auth.current_user()
        id_device = kwargs['id_device']
        messages = {'messages':'failed'}

        device_exists = OltDevicesModels.query.filter_by(id=id_device).first()

        def sync_onu_task(id_device, username):
            with scheduler.app.app_context():
                device = OltDevicesModels.query.filter_by(id=id_device).first()
                if device:
                    device.sync_onu_configured_from_olt(username)
        
        if device_exists:
            #device_exists.sync_onu_configured_from_olt(operator.username)
            scheduler.add_job(
                id=f"sync_onu_{id_device}",
                func=sync_onu_task,
                args=[id_device, operator.username],
                replace_existing=True
            )
            messages['messages']='success'

        return jsonify(messages)