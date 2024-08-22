from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort

from accessapp.authapp import auth

from .models import db, SitesModel
from userlogin.models import AllowedSiteUserModel

class CreateSiteSchema(Schema):
    id = fields.Integer(metadata={"description":"Id Site (Auto jika tidak diisi)"})
    name = fields.String(required=True, metadata={"description":"Nama Site"})
    code = fields.String(metadata={"description":"Nama Site"})

class SiteSchema(Schema):
    id = fields.Integer(metadata={"description":"Id Site"})
    name = fields.String(metadata={"description":"Nama Site"})
    code = fields.String(metadata={"description":"Nama Site"})

class UpdateSiteSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"Id Site"})
    name = fields.String(metadata={"description":"Nama Site"})
    code = fields.String(metadata={"description":"Nama Site"})


class ListSiteSchema(Schema):
    data = fields.List(fields.Nested(SiteSchema))

class DeleteSiteSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"Id Site"})

class SiteApi(MethodResource, Resource):
    @doc(description='Create Site', tags=['Sites'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(CreateSiteSchema, location=('json'))
    @auth.login_required(role=['api'])
    def post(self, **kwargs):
        name = kwargs['name']
        name_exists = SitesModel.query.filter_by(name=name).first()
        if name_exists:
            abort(409, 'Name site exists')
        
        try:
            code = kwargs['code']
        except:
            code=None

        try:
            id = kwargs['id']
            new_sites = SitesModel(name, id, code)
        except:
            new_sites = SitesModel(name, code=code)

        db.session.add(new_sites)
        db.session.commit()

        mesg = {"message":"success"}
        respone = jsonify(mesg)
        respone.status_code = 201
        return respone
    
    @doc(description='List Site', tags=['Sites'], security=[{"ApiKeyAuth": []}])
    @marshal_with(ListSiteSchema)
    @auth.login_required(role=['api','noc','superadmin', 'teknisi', 'admin'])
    def get(self):
        operator = auth.current_user()
        if operator.role in ['api','noc','superadmin']:
            try:
                id = request.args.get('id')
                if id != None:
                    data_sites = SitesModel.query.filter_by(site_id=id).first()
                    if data_sites:
                        return jsonify(data_sites.to_dict())
                    abort(404, 'id not found')
            except:
                pass
            
            try:
                name = request.args.get('name')
                if name != None:
                    data_sites = SitesModel.query.filter_by(name=name).first()
                    if data_sites:
                        return jsonify(data_sites.to_dict())
                    abort(404, 'id not found')
            except:
                pass


        data = []
        if operator.role in ['teknisi', 'admin']:
            allowed_site = AllowedSiteUserModel.query.filter_by(username=operator.username).all()
            list_allowed = []
            for _allowed in allowed_site:
                list_allowed.append(_allowed.site_id)
            
            data_sites = SitesModel.query.filter(SitesModel.site_id.contains(list_allowed)).all()
        else:    
            data_sites = SitesModel.query.order_by(SitesModel.name.asc()).all()

        for site in data_sites:
            data.append(site.to_dict())

        return jsonify(data)
    
    @doc(description='Update Site', tags=['Sites'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(UpdateSiteSchema, location=('json'))
    @auth.login_required(role=['api'])
    def put(self, **kwargs):
        id = kwargs['id']
        id_exists = SitesModel.query.filter_by(id=id).first()
        if id_exists:
            name = kwargs['name']
            name_exists = SitesModel.query.filter_by(name=name).first()
            if name_exists:
                abort(409, 'Name site exists')

            id_exists.name = name
            db.session.commit()

            return jsonify({"message":"success"})
        
        abort(404, 'id not found')

    @doc(description='Delete Site', tags=['Sites'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(DeleteSiteSchema, location=('json','form'))
    @auth.login_required(role=['api'])
    def delete(self, **kwargs):
        id = kwargs['id']
        id_exists = SitesModel.query.filter_by(id=id).first()
        if id_exists:
            db.session.delete(id_exists)
            db.session.commit()
            return jsonify({"message":"success"})
        
        abort(404, 'id not found')



class InfoIdSiteApi(MethodResource, Resource):
    @doc(description='Info Id Site', tags=['Sites'], security=[{"ApiKeyAuth": []}])
    @marshal_with(SiteSchema)
    @auth.login_required(role=['api','noc'])
    def get(self):
        pass

class InfoNameSiteApi(MethodResource, Resource):
    @doc(description='Info name Site', tags=['Sites'], security=[{"ApiKeyAuth": []}])
    @marshal_with(SiteSchema)
    @auth.login_required(role=['api','noc'])
    def get(self):
        pass