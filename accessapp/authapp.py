from flask import Flask
from flask_httpauth import HTTPTokenAuth

app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')

from .tokenapp import verify_token_jwt
from .models import ApiTokenAccessModel
    

@auth.verify_token
def verify_token(token):
    user = verify_token_jwt(token)
    if user.verify_token():
        data = user.payload_token()
        username_exists = ApiTokenAccessModel.query.filter_by(username=data['username']).first()
        if username_exists:
            #return data['username']
            return username_exists

@auth.get_user_roles
def get_user_roles(user):
    # roles = ApiTokenAccessModel.query.filter_by(username=user).order_by(ApiTokenAccessModel.created_at.desc()).first()
    # return roles.role
    return user.role