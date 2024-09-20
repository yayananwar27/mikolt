from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort

from accessapp.authapp import auth

from .models import db, OltDevicesCardModels, OltDevicesModels
from userlogin.models import AllowedSiteUserModel

from datetime import datetime
def created_time():
    dt_now = datetime.now()
    date = dt_now.strftime("%Y-%m-%d %H:%M:%S")
    return str(date)

class IdOltDeviceShowCardSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"id record Device"})

class OltDeviceCardapi(MethodResource, Resource):
    @doc(description='Show Olt Device Card', tags=['OLT Device'], security=[{"ApiKeyAuth": []}])
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
                # list_card = OltDevicesCardModels.query.filter_by(id_device=found_record.id).order_by(
                #     OltDevicesCardModels.type_port.asc()
                # ).all()
                data = found_record.show_list_card()

        else:
            found_record = OltDevicesModels.query.filter_by(id=id).first()
            if found_record:
                # list_card = OltDevicesCardModels.query.filter_by(id_device=found_record.id).order_by(
                #     OltDevicesCardModels.type_port.asc()
                # ).all()
                data = found_record.show_list_card()
        
        
        # if len(list_card)>0:
        #     data = []
        #     for card in list_card:
        #         data.append(card.to_dict())

        return data
    
    @doc(description='Update Olt Device Card', tags=['OLT Device'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(IdOltDeviceShowCardSchema, location=('json'))
    @auth.login_required(role=['api', 'noc', 'superadmin', 'teknisi'])
    def put(self, **kwargs):
        id = kwargs['id']
        data = {'message':'Update Failed'}

        device_exists = OltDevicesModels.query.filter_by(id=id).first()
        if device_exists:
            card_list = device_exists.oltdevice_showcard()
            for card in card_list:
                exists_card = OltDevicesCardModels.query.filter_by(
                    id_device=id,
                    frame=card['Frame'],
                    slot=card['Slot']
                ).first()
                if exists_card:
                    exists_card.cfg_type = card['CfgType']
                    exists_card.jml_port = card['Port']
                    exists_card.soft_ver = card['SoftVer']
                    exists_card.status = card['Status']
                    exists_card.type_port = card['type_port']
                    
                    exists_card.last_update = created_time()

                    db.session.commit()
                else:
                    
                    new_card = OltDevicesCardModels(
                        id,
                        card['Frame'],
                        card['Slot'],
                        card['Slot'],
                        card['CfgType'],
                        card['SoftVer'],
                        card['Status'],
                        card['type_port'],
                        created_time()
                    )
                    db.session.add(new_card)
                    db.session.commit()

            data = {'message':'success'}                    
        return data


class OltDeviceCardPonapi(MethodResource, Resource):
    @doc(description='Show Olt Device Card Pon Port', tags=['OLT Device'], security=[{"ApiKeyAuth": []}])
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
               data = found_record.show_list_portpon()
        else:
            found_record = OltDevicesModels.query.filter_by(id=id).first()
            if found_record:
                data = found_record.show_list_portpon()
        
        return data