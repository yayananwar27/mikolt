from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort
from sqlalchemy.orm import aliased

from accessapp.authapp import auth

from mmikrotik.models import MmikrotikModel
from clientppp.models import db, ClientPPPModel, ClientPPPStatsModel
from sites.models import SitesModel
from userlogin.models import UserLoginModel, AllowedSiteUserModel

class MikrotikSummarySchema(Schema):
    total = fields.Integer(metadata={"description":"Total Data"})
    connected = fields.Integer(metadata={"description":"Total Connected"})
    disconnected = fields.Integer(metadata={"description":"Total Disconnect"})

class PPPClientSummarySchema(Schema):
    total = fields.Integer(metadata={"description":"Total Data"})
    configured = fields.Integer(metadata={"description":"Total Configured"})
    unconfigured = fields.Integer(metadata={"description":"Total Unconfigured"})
    enable = fields.Integer(metadata={"description":"Total Enable"})
    disable = fields.Integer(metadata={"description":"Total Disable"})

class PPPClientConnectedSummarySchema(Schema):
    total = fields.Integer(metadata={"description":"Total Data"})
    connected = fields.Integer(metadata={"description":"Total Connected"})
    disconnected = fields.Integer(metadata={"description":"Total Disconnect"})

class RespDashboardSummarySchema(Schema):
    mikrotik = fields.Nested(MikrotikSummarySchema)
    total_site = fields.Integer(metadata={"description":"Total Site"})
    client = fields.Nested(PPPClientSummarySchema)
    total_admin = fields.Integer(metadata={"description":"Total Administrator"})


class DashboardSummaryApi(MethodResource, Resource):
    @doc(description='Dashboard Summary Data', tags=['Dashboard'], security=[{"ApiKeyAuth": []}])
    @marshal_with(RespDashboardSummarySchema)
    @auth.login_required(role=['api','noc','superadmin','teknisi','admin'])
    def get(self):
        operator = auth.current_user()
        if operator.role in ['teknisi','admin']:
            allowed_site = AllowedSiteUserModel.query.filter_by(username=operator.username).all()
            list_allowed = []
            for _allowed in allowed_site:
                list_allowed.append(_allowed.site_id)

            list_mikrotik = MmikrotikModel.query.filter(
                    MmikrotikModel.site_id.in_(list_allowed)
                    ).all()
            mikrotik_connect = 0
            mikrotik_disconnect = 0
            allowed_mikrotik = []

            for _mikrotik in list_mikrotik:
                allowed_mikrotik.append(_mikrotik.mikrotik_id)
                _mik = _mikrotik.to_dict()
                if _mik['connected'] == 1:
                    mikrotik_connect += 1
                else:
                    mikrotik_disconnect += 1
            mikrotik_summary = {
                'total':len(list_mikrotik),
                'connected':mikrotik_connect,
                'disconnected':mikrotik_disconnect
            }

            list_site = SitesModel.query.filter(
                    SitesModel.site_id.in_(list_allowed)
                    ).all()
            #userlogin = UserLoginModel.query.all()

            list_client = ClientPPPModel.query.filter(
                    ClientPPPModel.mikrotik_id.in_(allowed_mikrotik)).all()
            list_configured = ClientPPPModel.query.filter(
                    ClientPPPModel.mikrotik_id.in_(allowed_mikrotik)).filter_by(configuration='configured').all()
            list_disabled = ClientPPPModel.query.filter(
                    ClientPPPModel.mikrotik_id.in_(allowed_mikrotik)).filter_by(status='disable').all()



            client_summary = {
                'total':len(list_client),
                'configured':len(list_configured),
                'unconfigured':len(list_client)-len(list_configured),
                'enable':len(list_client)-len(list_disabled),
                'disable':len(list_disabled)
            }

            data = {
                'mikrotik':mikrotik_summary,
                'total_site':len(list_site),
                'client':client_summary,
                'total_admin':1
            }
            return jsonify(data)


        list_mikrotik = MmikrotikModel.query.all()
        mikrotik_connect = 0
        mikrotik_disconnect = 0

        for _mikrotik in list_mikrotik:
            _mik = _mikrotik.to_dict()
            if _mik['connected'] == 1:
                mikrotik_connect += 1
            else:
                mikrotik_disconnect += 1
        mikrotik_summary = {
            'total':len(list_mikrotik),
            'connected':mikrotik_connect,
            'disconnected':mikrotik_disconnect
        }

        list_site = SitesModel.query.all()
        userlogin = UserLoginModel.query.all()

        list_client = ClientPPPModel.query.all()
        list_configured = ClientPPPModel.query.filter_by(configuration='configured').all()
        list_disabled = ClientPPPModel.query.filter_by(status='disable').all()



        client_summary = {
            'total':len(list_client),
            'configured':len(list_configured),
            'unconfigured':len(list_client)-len(list_configured),
            'enable':len(list_client)-len(list_disabled),
            'disable':len(list_disabled)
        }

        data = {
            'mikrotik':mikrotik_summary,
            'total_site':len(list_site),
            'client':client_summary,
            'total_admin':len(userlogin)
        }
        return jsonify(data)


class DashboardClientConSummaryApi(MethodResource, Resource):
    @doc(description='Dashboard Client Connected', tags=['Dashboard'], security=[{"ApiKeyAuth": []}])
    @marshal_with(PPPClientConnectedSummarySchema)
    @auth.login_required(role=['api','noc','superadmin','teknisi','admin'])
    def get(self):
        list_client = ClientPPPModel.query.all()
        stats_alias = aliased(ClientPPPStatsModel)

        # Query to get the latest stats for each client
        subquery = (
            db.session.query(
                stats_alias.client_id,
                db.func.max(stats_alias.id).label('latest_id')
            )
            .group_by(stats_alias.client_id)
            .subquery()
        )

        # Main query to get clients with zero tx and rx bytes
        list_disconnected = (
            db.session.query(ClientPPPModel)
            .join(subquery, ClientPPPModel.client_id == subquery.c.client_id)
            .join(stats_alias, stats_alias.id == subquery.c.latest_id)
            .filter(stats_alias.total_tx_byte == 0, stats_alias.total_rx_byte == 0)
            .all()
        )
        data = {
            'total':len(list_client),
            'connected':len(list_client)-len(list_disconnected),
            'disconnected': len(list_disconnected)
        }

        return jsonify(data)