from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort
from sqlalchemy import func

from accessapp.authapp import auth

from .models import ClientPPPModel, ClientPPPStatsModel, db, ClientPPPStatMonthsModel
from userlogin.models import AllowedSiteUserModel
from mmikrotik.models import MmikrotikModel
class StatisticClientSchemaRequest(Schema):
    client_name = fields.String(required=True, metadata={"description":"ID client"})
    start_datetime = fields.DateTime(required=True, metadata={"description":"ex 2023-01-01"})
    end_datetime = fields.DateTime(required=True, metadata={"description":"ex 2023-01-02"})

class StatisticClientMonthSchemaRequest(Schema):
    client_name = fields.String(required=True, metadata={"description":"ID client"})
    year_month = fields.String(required=True, metadata={"description":"ex 2024-01"})
    

class ClientPPPStatsSecretsApi(MethodResource, Resource):
    @doc(description='Stats Client PPP', tags=['Client PPP'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(StatisticClientSchemaRequest, location=('json'))
    @auth.login_required(role=['api','noc', 'superadmin', 'teknisi','admin'])
    def post(self, **kwargs):
        operator = auth.current_user()

        client_name = kwargs['client_name']
        start_datetime = str(kwargs['start_datetime'])
        end_datetime = str(kwargs['end_datetime'])

        if operator.role in ['teknisi','admin']:
            allowed_site = AllowedSiteUserModel.query.filter_by(username=operator.username).all()
            list_allowed = []
            for _allowed in allowed_site:
                list_allowed.append(_allowed.site_id)

            list_mikrotik = MmikrotikModel.query.filter(
                    MmikrotikModel.site_id.in_(list_allowed)
                    ).all()
            allowed_mikrotik = []

            for _mikrotik in list_mikrotik:
                allowed_mikrotik.append(_mikrotik.mikrotik_id)

            client_id_exists = ClientPPPModel.query.filter(
                    ClientPPPModel.mikrotik_id.in_(allowed_mikrotik)
                    ).filter_by(name=client_name).first()
            if not client_id_exists:
                abort(404, "client name not found")

        
            datanya = ClientPPPStatsModel.query.filter_by(
                client_id=client_id_exists.client_id
                ).filter(
                    ClientPPPStatsModel.timestamp.between(start_datetime, end_datetime)
                ).order_by(
                    ClientPPPStatsModel.timestamp.asc()
                ).group_by(ClientPPPStatsModel.timestamp).all()
        

        else:
            client_id_exists = ClientPPPModel.query.filter_by(name=client_name).first()
            if not client_id_exists:
                abort(404, "client name not found")

        
            datanya = ClientPPPStatsModel.query.filter_by(
                client_id=client_id_exists.client_id
                ).filter(
                    ClientPPPStatsModel.timestamp.between(start_datetime, end_datetime)
                ).order_by(
                    ClientPPPStatsModel.timestamp.asc()
                ).group_by(ClientPPPStatsModel.timestamp).all()
        
        if datanya:
            total_byte = 0
            total_packet = 0
            _datanya = []
            for _data in datanya:
                _datanya.append(_data.to_dict())
                #total_byte = total_byte + _data.tx_byte + _data.rx_byte
                #total_packet = total_packet + _data.tx_packet + _data.rx_packet
            if len(_datanya)>0:
                total_byte = sum(item['tx_byte'] for item in _datanya)+sum(item['rx_byte'] for item in _datanya)
                total_packet = sum(item['tx_packet'] for item in _datanya)+sum(item['rx_packet'] for item in _datanya)            

            data = {
                'client_id':client_id_exists.client_id,
                'client_name':client_name,
                'start_datetime':start_datetime,
                'end_datetime':end_datetime,
                'data':_datanya,
                'total_byte': total_byte,
                'total_packet': total_packet,
            }
            return jsonify(data)
        else:
            data = {
                    'client_id':client_id_exists.client_id,
                    'client_name':client_name,
                    'start_datetime':start_datetime,
                    'end_datetime':end_datetime,
                    'data':[],
                    'total_byte': 0,
                    'total_packet': 0,
                }
            return jsonify(data)

class ClientPPPStatsMonthSecretsApi(MethodResource, Resource):
    @doc(description='Stats Client PPP month', tags=['Client PPP'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(StatisticClientMonthSchemaRequest, location=('json'))
    @auth.login_required(role=['api','noc', 'superadmin', 'teknisi','admin'])
    def post(self, **kwargs):
        client_name = kwargs['client_name']
        year_month = kwargs['year_month']
        month = '{}-01'.format(year_month)
        operator = auth.current_user()

        if operator.role in ['teknisi','admin']:
            allowed_site = AllowedSiteUserModel.query.filter_by(username=operator.username).all()
            list_allowed = []
            for _allowed in allowed_site:
                list_allowed.append(_allowed.site_id)

            list_mikrotik = MmikrotikModel.query.filter(
                    MmikrotikModel.site_id.in_(list_allowed)
                    ).all()
            
            allowed_mikrotik = []

            for _mikrotik in list_mikrotik:
                allowed_mikrotik.append(_mikrotik.mikrotik_id)


            client_id_exists = ClientPPPModel.query.filter(
                    ClientPPPModel.mikrotik_id.in_(allowed_mikrotik)
                    ).filter_by(name=client_name).first()
            if not client_id_exists:
                abort(404, "client name not found")

            data_exists = ClientPPPStatMonthsModel.query.filter_by(
                client_id = client_id_exists.client_id,
                month = month
            ).first()

        else:
            client_id_exists = ClientPPPModel.query.filter_by(name=client_name).first()
            if not client_id_exists:
                abort(404, "client name not found")

            data_exists = ClientPPPStatMonthsModel.query.filter_by(
                client_id = client_id_exists.client_id,
                month = month
            ).first()


        if data_exists:            
            data = {
                'client_id':client_id_exists.client_id,
                'client_name':client_name,
                'total_upload': data_exists.upload_byte,
                'total_download': data_exists.download_byte,
                'year_month':year_month
            }
            return jsonify(data)
        else:
            data = {
                    'client_id':client_id_exists.client_id,
                    'client_name':client_name,
                    'total_byte': 0,
                    'total_packet': 0,
                    'year_month': year_month
                }
            return jsonify(data)
        
    @doc(description='GET Stats Client PPP month', tags=['Client PPP'], security=[{"ApiKeyAuth": []}])
    @auth.login_required(role=['api','noc', 'superadmin', 'teknisi'])
    def get(self):
        try:
            from datetime import datetime, timedelta
            from concurrent.futures import ThreadPoolExecutor
            current_date = datetime.now()
            start_date = current_date.replace(day=1)
            next_month = start_date + timedelta(days=32)
            end_date = next_month.replace(day=1)

            operator = auth.current_user()
            if operator.role in ['teknisi', 'admin']:
                allowed_site = AllowedSiteUserModel.query.filter_by(username=operator.username).all()
                list_allowed = []
                for _allowed in allowed_site:
                    list_allowed.append(_allowed.site_id)

                list_mikrotik = MmikrotikModel.query.filter(
                        MmikrotikModel.site_id.in_(list_allowed)
                        ).all()
                
                allowed_mikrotik = []

                for _mikrotik in list_mikrotik:
                    allowed_mikrotik.append(_mikrotik.mikrotik_id)

                client_id_exists = ClientPPPModel.query.filter(
                        ClientPPPModel.mikrotik_id.in_(allowed_mikrotik)
                        ).all()
                allowed_client = []
                for client in client_id_exists:
                    allowed_client.append(client.client_id)                
                
                results = db.session.query(
                    ClientPPPStatsModel.client_id,
                    db.func.date_format(ClientPPPStatsModel.timestamp, '%Y-%m-01').label('month'),
                    db.func.sum(ClientPPPStatsModel.tx_byte).label('total_tx_byte'),
                    db.func.sum(ClientPPPStatsModel.rx_byte).label('total_rx_byte')
                ).filter(
                    ClientPPPStatsModel.client_id.in_(allowed_client),
                    ClientPPPStatsModel.timestamp >= start_date,
                    ClientPPPStatsModel.timestamp < end_date
                ).group_by(
                    ClientPPPStatsModel.client_id,
                    db.func.date_format(ClientPPPStatsModel.timestamp, '%Y-%m-01')
                ).all()

            else:
                results = db.session.query(
                    ClientPPPStatsModel.client_id,
                    db.func.date_format(ClientPPPStatsModel.timestamp, '%Y-%m-01').label('month'),
                    db.func.sum(ClientPPPStatsModel.tx_byte).label('total_tx_byte'),
                    db.func.sum(ClientPPPStatsModel.rx_byte).label('total_rx_byte')
                ).filter(
                    ClientPPPStatsModel.timestamp >= start_date,
                    ClientPPPStatsModel.timestamp < end_date
                ).group_by(
                    ClientPPPStatsModel.client_id,
                    db.func.date_format(ClientPPPStatsModel.timestamp, '%Y-%m-01')
                ).all()

            def masukkan_data(app, result):
                with app.app_context():
                    data_exists = ClientPPPStatMonthsModel.query.filter_by(client_id=result.client_id, month=result.month).first()
                    if data_exists:
                        data_exists.download_byte = result.total_tx_byte
                        data_exists.upload_byte = result.total_rx_byte
                    else:
                        new_data = ClientPPPStatMonthsModel(
                            result.client_id,
                            result.month,
                            result.total_tx_byte,
                            result.total_rx_byte
                        )
                        db.session.add(new_data)
                    db.session.commit()

            app = current_app._get_current_object()
            with ThreadPoolExecutor() as executor:
                executor.map(lambda result: masukkan_data(app, result), results)    
                
            return jsonify({
                'messages':'success'
            })
        except Exception as e:
            current_app.logger.error(e)