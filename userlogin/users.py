from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, abort, request
from werkzeug.security import generate_password_hash

from accessapp.authapp import auth

from .models import db, UserLoginModel, AllowedSiteUserModel
from sites.site import SitesModel

class CreateUserLoginSchema(Schema):
    username = fields.String(required=True, metadata={"description":"Username"})
    password = fields.String(required=True, metadata={"description":"Password"})
    role = fields.String(required=False, allow_none=True, metadata={"description":"role user"})
    list_site = fields.List(fields.Integer(required=False, allow_none=True, metadata={"description":"Integer Site"}))


class UserLoginSchema(Schema):
    username = fields.String(metadata={"description":"Username"})
    password = fields.String(metadata={"description":"Password"})
    role = fields.String(metadata={"description":"role user"})
    list_site = fields.List(fields.Integer(required=False, allow_none=True, metadata={"description":"Integer Site"}))

class ListUserLoginSchema(Schema):
    data = fields.List(fields.Nested(UserLoginSchema))

class DeleteUserLoginSchema(Schema):
    username = fields.String(required=True, metadata={"description":"Username"})

class UserLoginApi(MethodResource, Resource):
    @doc(description='Create Users Login', tags=['User Login'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(CreateUserLoginSchema, location=('json'))
    #@marshal_with(UserLoginSchema)
    @auth.login_required(role=['api','noc', 'superadmin'])
    def post(self, **kwargs):
        username = kwargs['username']
        password = kwargs['password']
        role = kwargs['role']

        user_exists = UserLoginModel.query.filter_by(username=username).first()
        if user_exists:
            abort(409, 'username already exists')

        encrypt_pass = generate_password_hash(password)
        new_user = UserLoginModel(username, encrypt_pass, role)
        db.session.add(new_user)
        db.session.commit()

        add_site = []
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

        # list_allowed = AllowedSiteUserModel.query.filter_by(username=username).all()
        # list_site = []
        # list_site_info = []
        # for allowed in list_allowed:
        #     list_site.append(allowed.site_id)
        #     list_site_info.append(allowed.to_dict_info())
        # response = {
        #     'messages':'success',
        #     'username':username,
        #     'list_site':list_site,
        #     'list_site_info':list_site_info
        # }

        
        operator = auth.current_user()
        current_app.logger.info('User Added {} by {}'.format(username, operator.username))
        msg = {'message':'success'}
        response=jsonify(msg)
        response.status_code=201
        return response
    
    @doc(description='Update Users Login', tags=['User Login'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(CreateUserLoginSchema, location=('json'))
    #@marshal_with(UserLoginSchema)
    @auth.login_required(role=['api','noc','superadmin', 'teknisi', 'admin'])
    def put(self, **kwargs):
        operator = auth.current_user()
        if operator.role in ['teknisi', 'admin']:
            username = operator.username
        else:
            username = kwargs['username']
        password = kwargs['password']

        user_exists = UserLoginModel.query.filter_by(username=username).first()
        if not user_exists:
            abort(404, 'username not found')

        encrypt_pass = generate_password_hash(password)
        user_exists.username = username
        user_exists.password = encrypt_pass
        db.session.commit()

        if operator.role in ['api', 'superadmin', 'noc']:
            if 'role' in kwargs:
                if kwargs['role'] in ['api','noc','superadmin', 'teknisi', 'admin']:
                    user_exists.role = kwargs['role']

            if 'list_site' in kwargs:
                list_site = kwargs['list_site']

                site_exists = SitesModel.query.all()
                exists_site = []
                for site in site_exists:
                    exists_site.append(site.site_id)

                if not set(list_site).issubset(set(exists_site)):
                    abort(404, 'some site not exists')

                for site in list_site:
                    allowed_exists = AllowedSiteUserModel.query.filter_by(username=username, site_id=site).first()
                    if allowed_exists:
                        pass
                    else:
                        new_allowed = AllowedSiteUserModel(username, site)
                        db.session.add(new_allowed)
                        db.session.commit()

                dataid_exists = AllowedSiteUserModel.query.filter_by(username=username).all()
                for dataid in dataid_exists:
                    if dataid.site_id not in list_site:
                        db.session.delete(dataid)
                        db.session.commit()

        db.session.commit()

        current_app.logger.info('User Updated {} by {}'.format(username, operator.username))
        msg = {'message':'success'}
        response=jsonify(msg)
        response.status_code=200
        return response

    @doc(description='List Users Login', tags=['User Login'], security=[{"ApiKeyAuth": []}])
    @marshal_with(ListUserLoginSchema)
    @auth.login_required(role=['api','noc','superadmin','teknisi','admin'])
    def get(self):
        operator = auth.current_user()
        if operator.role in ['teknisi','admin']:
            data = []
            user_all = UserLoginModel.query.filter_by(username=operator.username).all()
            for user in user_all:
                list_allowed = AllowedSiteUserModel.query.filter_by(username=user.username).all()
                list_site = []
                list_site_info = []
                for allowed in list_allowed:
                    list_site.append(allowed.site_id)
                    list_site_info.append(allowed.to_dict_info())
                    
                _user = user.to_dict()
                _user.pop('password')
                _user['list_site'] = list_site
                _user['list_site_info'] = list_site_info
                
                data.append(_user)
            
            return jsonify({'data':data})

        else:
            data = []
            if 'username' in request.args:
                user_all = UserLoginModel.query.filter_by(username=request.args.get('username', '', type=str)).all()
            else:  
                user_all = UserLoginModel.query.order_by(UserLoginModel.username.asc()).all()
            for user in user_all:
                list_allowed = AllowedSiteUserModel.query.filter_by(username=user.username).all()
                list_site = []
                list_site_info = []
                for allowed in list_allowed:
                    list_site.append(allowed.site_id)
                    list_site_info.append(allowed.to_dict_info())
                    
                _user = user.to_dict()
                _user.pop('password')
                _user['list_site'] = list_site
                _user['list_site_info'] = list_site_info
                
                data.append(_user)
            
            return jsonify({'data':data})
        
    @doc(description='Delete Users Login', tags=['User Login'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(DeleteUserLoginSchema, location=('json'))
    @auth.login_required(role=['api','noc', 'superadmin'])
    def delete(self, **kwargs):
        username = kwargs['username']

        user_exists = UserLoginModel.query.filter_by(username=username).first()
        if user_exists:
           db.session.delete(user_exists)
           
           dataid_exists = AllowedSiteUserModel.query.filter_by(username=username).all()
           for dataid in dataid_exists:
               db.session.delete(dataid)

           db.session.commit()
           current_app.logger.info('User Deleted {} by {}'.format(username, auth.current_user()))
           return jsonify({"message":"success"})
        else:
            abort(404, 'Not Found')

class InfoUserLoginApi(MethodResource, Resource):
    @doc(description='List Users Login', tags=['User Login'], security=[{"ApiKeyAuth": []}])
    @marshal_with(ListUserLoginSchema)
    @auth.login_required(role=['api','noc','superadmin','teknisi','admin'])
    def get(self):
        pass
