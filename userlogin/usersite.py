from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, abort
from werkzeug.security import generate_password_hash

from accessapp.authapp import auth

from .models import db, UserLoginModel, AllowedSiteUserModel
from sites.models import SitesModel
from userlogin.models import UserLoginModel

class UserAllowedSiteSchema(Schema):
    username = fields.String(required=True, metadata={"description":"Username"})
    id_site = fields.Integer(required=False, allow_none=True, metadata={"description":"Integer Site"})
    list_site = fields.List(fields.Integer(required=False, allow_none=True, metadata={"description":"Integer Site"}))

class ListUserAllowedSiteSchema(Schema):
    username = fields.String(required=True, metadata={"description":"Username"})
    list_site = fields.List(fields.Integer(required=False, allow_none=True, metadata={"description":"Integer Site"}))

class UserAllowedSiteApi(MethodResource, Resource):
    @doc(description='Create Users Allow Site', tags=['User Login'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(UserAllowedSiteSchema, location=('json'))
    @marshal_with(ListUserAllowedSiteSchema)
    @auth.login_required(role=['api','noc', 'superadmin'])
    def post(self, **kwargs):
        username = kwargs['username']

        user_exists = UserLoginModel.query.filter_by(username=username).first()
        if not user_exists:
            abort(404, 'username not found')

        add_site = []
        if 'id_site' in kwargs:
            add_site.append(kwargs['id_site'])

        if 'list_site' in kwargs:
            add_site = add_site + kwargs['list_site']

        site_exists = SitesModel.query.all()
        exists_site = []
        for site in site_exists:
            exists_site.append(site.site_id)

        if not set(add_site).issubset(set(exists_site)):
            abort(404, 'some site not exists')

        for site in add_site:
            allowed_exists = AllowedSiteUserModel.query.filter_by(username=username, site_id=site).first()
            if allowed_exists:
                pass
            else:
                new_allowed = AllowedSiteUserModel(username, site)
                db.session.add(new_allowed)
                db.session.commit()

        list_allowed = AllowedSiteUserModel.query.filter_by(username=username).all()
        list_site = []
        list_site_info = []
        for allowed in list_allowed:
            list_site.append(allowed.site_id)
            list_site_info.append(allowed.to_dict_info())
        response = {
            'messages':'success',
            'username':username,
            'list_site':list_site,
            'list_site_info':list_site_info
        }
        return jsonify(response)

    @doc(description='ListUsers Allow Site', tags=['User Login'], security=[{"ApiKeyAuth": []}])
    @marshal_with(ListUserAllowedSiteSchema)
    @auth.login_required(role=['api','noc', 'superadmin','teknisi','admin'])
    def get(self):
        operator = auth.current_user()
        list_allowed = AllowedSiteUserModel.query.filter_by(username=str(auth.current_user())).all()
        list_site = []
        list_site_info = []
        for allowed in list_allowed:
            list_site.append(allowed.site_id)
            list_site_info.append(allowed.to_dict_info())
        response = {
            'username':str(auth.current_user()),
            'list_site':list_site,
            'list_site_info':list_site_info
        }
        if operator.role in ['superadmin','noc','api']:
            list_user = UserLoginModel.query.all()
            response2 = [] 
            for user in list_user:
                list_allowed = AllowedSiteUserModel.query.filter_by(username=user.username).all()
                list_site = []
                list_site_info = []
                for allowed in list_allowed:
                    list_site.append(allowed.site_id)
                    print(user.username)
                    list_site_info.append(allowed.to_dict_info())
                response2.append({
                    'username':user.username,
                    'list_site':list_site,
                    'list_site_info':list_site_info
                })
            print(response2)

            response['other_user'] = response2

        return jsonify(response)
    
    @doc(description='Delete Users Allow Site', tags=['User Login'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(UserAllowedSiteSchema, location=('json'))
    @marshal_with(ListUserAllowedSiteSchema)
    @auth.login_required(role=['api','noc', 'superadmin'])
    def delete(self, **kwargs):
        username = kwargs['username']

        user_exists = UserLoginModel.query.filter_by(username=username).first()
        if not user_exists:
            abort(404, 'username not found')

        delete_site = []
        if 'id_site' in kwargs:
            delete_site.append(kwargs['id_site'])

        if 'list_site' in kwargs:
            delete_site = delete_site + kwargs['list_site']

        site_exists = SitesModel.query.all()
        exists_site = []
        for site in site_exists:
            exists_site.append(site.site_id)

        if not set(delete_site).issubset(set(exists_site)):
            abort(404, 'some site not exists')

        for site in delete_site:
            allowed_exists = AllowedSiteUserModel.query.filter_by(username=username, site_id=site).first()
            if allowed_exists:
                db.session.delete(allowed_exists)
                db.session.commit()
            else:
                pass

        list_allowed = AllowedSiteUserModel.query.filter_by(username=username).all()
        list_site = []
        list_site_info = []
        for allowed in list_allowed:
            list_site.append(allowed.site_id)
            list_site_info.append(allowed.to_dict_info())
        response = {
            'messages':'success',
            'username':username,
            'list_site':list_site,
            'list_site_info':list_site_info
        }
        return jsonify(response)
