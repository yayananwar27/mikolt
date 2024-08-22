from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import abort, jsonify, request

from .tokenapp import verify_token_jwt, get_datetime
from .models import ApiTokenRefreshModel

class VerifyTokenSchema(Schema):
    token = fields.String(metadata={"description":"Token"})

class RespVerifyTokenSchema(Schema):
    status = fields.String(metadata={"description":"Info Token valid/invalid/expired"})

class VerifyTokenApi(MethodResource, Resource):
    @doc(description='Token Verify', tags=['TOKEN VERIFY'])
    @use_kwargs(VerifyTokenSchema, location=('json'))
    @marshal_with(RespVerifyTokenSchema)
    def post(self, **kwargs):
        try:
            token_type = request.args.get('type')
            token = kwargs['token']
            time_now = get_datetime()
            
            if token_type == 'access':
                verify_token = verify_token_jwt(token)
                data_token = verify_token.payload_token()
                if verify_token.verify_token():
                    return jsonify({'status':'valid'})
                elif time_now.unix() > data_token['expired']:
                    return jsonify({'status':'expired'})
                else:
                    return jsonify({'status':'invalid'})
                
            elif token_type == 'refresh':
                token_exists = ApiTokenRefreshModel.query.filter_by(token=token, ipaddress=request.remote_addr, device=request.headers.get('User-Agent')).first()
                if token_exists:
                    verify_token = verify_token_jwt(token)
                    data_token = verify_token.payload_token()
                    if verify_token.verify_token():
                        return jsonify({'status':'valid'})
                    elif time_now.unix() > data_token['expired']:
                        return jsonify({'status':'expired'})
                    
                return jsonify({'status':'invalid'})
            else:
                abort(400, 'Invalid Request')
        except:
            abort(400, 'Invalid Request')
class ParamVerifyTokenApi(MethodResource, Resource):
    @doc(description='Token Verify', tags=['TOKEN VERIFY'])
    @use_kwargs(VerifyTokenSchema, location=('json'))
    @marshal_with(RespVerifyTokenSchema)
    def post(self, **kwargs):
        pass