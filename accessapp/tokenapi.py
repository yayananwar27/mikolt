from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request

from .authapp import auth
from .tokenapp import create_token_jwt
from .models import db, ApiTokenAccessModel

class CreateTokenApiSchema(Schema):
    username = fields.String(required=True, metadata={"description":"Name of API APP"})

class TokenApiSchema(Schema):
    username = fields.String(metadata={"description":"Name of API APP"})
    token = fields.String(metadata={"description":"Token of API APP"})
    expired = fields.String(metadata={"description":"Unix Expired of API APP"})
    expired_date = fields.DateTime(metadata={"description":"Expired datetime of API APP"})    

class ListTokenApiSchema(Schema):
    data = fields.List(fields.Nested(TokenApiSchema))

class DeleteTokenApiSchema(Schema):
    username = fields.String(required=True, metadata={"description":"Name of API APP"})


class TokenApi(MethodResource, Resource):
    @doc(description='Create API Token', tags=['API TOKEN'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(CreateTokenApiSchema, location=('json'))
    @marshal_with(TokenApiSchema)
    #@auth.login_required(role=['api','noc','superadmin'])
    def post(self, **kwargs):
        try:
            
            username = kwargs['username']
            role = 'api'
            payload = {
                'username':username,
                'role':role
            }

            new_token = create_token_jwt(payload)
            new_token = str(new_token.get_token())
            
            new_access_token = ApiTokenAccessModel(new_token, username, role)
            db.session.add(new_access_token)
            db.session.commit()

            current_app.logger.info('{0} - New Api Token Created {1}'.format(request.remote_addr,username))

            return jsonify(new_access_token.to_dict())

        except ValueError as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 400
            return respone
        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
        
    @doc(description='List API Token', tags=['API TOKEN'], security=[{"ApiKeyAuth": []}])
    @marshal_with(ListTokenApiSchema)
    @auth.login_required(role=['api','noc','superadmin'])
    def get(self):
        try:
            list_token_api = ApiTokenAccessModel.query.filter_by(role='api').order_by(ApiTokenAccessModel.username.asc()).all()
            data = []
            for token_api in list_token_api:
                data.append(token_api.to_dict())
            
            return jsonify({'data':data})
        except ValueError as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 400
            return respone
        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
        
    @doc(description='Delete API Token', tags=['API TOKEN'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(DeleteTokenApiSchema, location=('json'))
    @auth.login_required(role=['api','noc','superadmin'])
    def delete(self, **kwargs):
        try:
            username = kwargs['username']

            exists_token = ApiTokenAccessModel.query.filter_by(username=username).first()
            db.session.delete(exists_token)
            db.session.commit()
            current_app.logger.info('{0} - New Api Token Deleted {1}'.format(request.remote_addr,username))
            return jsonify({'message':'success'})
        except ValueError as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 400
            return respone
        except Exception as e:
            print(e)
            error = {"message":e}
            respone = jsonify(error)
            respone.status_code = 500
            return respone
