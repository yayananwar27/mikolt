from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, abort, request
from werkzeug.security import check_password_hash, generate_password_hash

from .models import db, UserLoginModel
from accessapp.models import ApiTokenAccessModel, ApiTokenRefreshModel
from accessapp.tokenapp import create_token_jwt, get_datetime

class TokenUserLoginSchema(Schema):
    username = fields.String(metadata={"description":"Username"})
    access_token = fields.String(metadata={"description":"Access Token"})
    refresh_token = fields.String(metadata={"description":"Refresh Token"})
    access_expired = fields.String(metadata={"description":"Expired Access Token Unix time"})
    access_expired_datetime = fields.DateTime(metadata={"description":"Expired Access Token"})
    refresh_expired = fields.String(metadata={"description":"Expired Refresh Token Unix time"})
    refresh_expired_datetime = fields.DateTime(metadata={"description":"Expired Refresh Token"})

class LoginUserLoginSchema(Schema):
    username = fields.String(required=True, metadata={"description":"Username"})
    password = fields.String(required=True, metadata={"description":"Password"})

class RefreshTokenSchema(Schema):
    refresh_token = fields.String(metadata={"description":"Refresh Token"})
    
class LoginUserLoginApi(MethodResource, Resource):
    @doc(description='Create Users Login', tags=['User Login'])
    @use_kwargs(LoginUserLoginSchema, location=('json'))
    @marshal_with(TokenUserLoginSchema)
    def post(self, **kwargs):
        username = kwargs['username']
        password = kwargs['password']

        user_exists = UserLoginModel.query.filter_by(username=username).first()
        if user_exists:
            if check_password_hash(user_exists.password, password):
                dt_now = get_datetime()
                exp_access = int(dt_now.unix()+(60*60))
                access_payload = {
                    'username':username,
                    'role':user_exists.role,
                    'expired':exp_access
                }
                access_token = create_token_jwt(access_payload)
                
                exp_refresh = int(dt_now.unix()+(24*60*60))
                refresh_payload = {
                    'username':username,
                    'role':user_exists.role,
                    'expired':exp_refresh,
                    'ipaddress':request.remote_addr
                }

                refresh_token = create_token_jwt(refresh_payload)

                access_exists = ApiTokenAccessModel.query.filter_by(username=username).first()
                if access_exists:
                    db.session.delete(access_exists)
                    db.session.commit()
                new_access_token = ApiTokenAccessModel(access_token.get_token(), username, user_exists.role, exp_access)
                new_refresh_token = ApiTokenRefreshModel(refresh_token.get_token(), username, request.headers.get('User-Agent'), request.remote_addr, exp_refresh)
                
                db.session.add(new_access_token)
                db.session.add(new_refresh_token)
                db.session.commit()

                current_app.logger.info(user_exists.username+'logged in')
                data_access = new_access_token.to_dict()
                data_refresh = new_refresh_token.to_dict()

                data = {
                    'username':username,
                    'access_token': data_access['token'],
                    'refresh_token': data_refresh['token'],
                    'access_expired': data_access['expired'],
                    'access_expired_datetime': data_access['expired_date'],
                    'refresh_expired':data_refresh['expired'],
                    'refresh_expired_datetime': data_refresh['expired_date']
                }
                return jsonify(data)
        abort(401,'wrong username or password')


class RefreshUserTokenApi(MethodResource, Resource):
    @doc(description='Renew Access token', tags=['User Login'])
    @use_kwargs(RefreshTokenSchema, location=('json'))
    @marshal_with(TokenUserLoginSchema)
    def post(self, **kwargs):
        from accessapp.tokenapp import verify_token_jwt
        token = kwargs['refresh_token']
        token_exists = ApiTokenRefreshModel.query.filter_by(token=token, ipaddress=request.remote_addr, device=request.headers.get('User-Agent')).first()
        if token_exists:
            token_verify = verify_token_jwt(token)
            if token_verify.verify_token():
                data_token = token_verify.payload_token()
                dt_now = get_datetime()
                exp_access = int(dt_now.unix()+(60*60))
                access_payload = {
                    'username':token_exists.username,
                    'role':data_token['role'],
                    'expired':exp_access
                }
                access_token = create_token_jwt(access_payload)
                access_exists = ApiTokenAccessModel.query.filter_by(username=data_token['username']).first()
                if access_exists:
                    db.session.delete(access_exists)
                    db.session.commit()

                new_access_token = ApiTokenAccessModel(access_token.get_token(), token_exists.username, data_token['role'], exp_access)
                db.session.add(new_access_token)
                db.session.commit()
                data_access = new_access_token.to_dict()
                data = {
                    'access_token':data_access['token'],
                    'access_expired':data_access['expired'],
                    'access_expired_datetime':data_access['expired_date']
                }
                return jsonify(data)

        abort(401,'Invalid Token')