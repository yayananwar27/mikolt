from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort


from accessapp.authapp import auth
from .models import db, MmikrotikModel
from userlogin.models import AllowedSiteUserModel

class CreateMikrotikSchema(Schema):
    name = fields.String(required=True, metadata={"description":"Name Mikrotik"})
    ipaddress = fields.String(required=True, metadata={"description":"IP/Host Mikrotik"})
    username = fields.String(required=True, metadata={"description":"Usename API Mikrotik"})
    password = fields.String(required=True, metadata={"description":"Password API Mikrotik"})
    apiport = fields.Integer(required=True, metadata={"description":"API Port Mikrotik"})
    site_id = fields.Integer(metadata={"description":"Site ID"})

class MikrotikSchema(Schema):
    mikrotik_id = fields.Integer(required=True, metadata={"description":"Mikrotik ID"})
    name = fields.String(required=True, metadata={"description":"Name Mikrotik"})
    ipaddress = fields.String(required=True, metadata={"description":"IP/Host Mikrotik"})
    username = fields.String(required=True, metadata={"description":"Usename API Mikrotik"})
    password = fields.String(required=True, metadata={"description":"Password API Mikrotik"})
    apiport = fields.Integer(required=True, metadata={"description":"API Port Mikrotik"})
    site_id = fields.Integer(metadata={"description":"Site ID"})

class ListMikrotikSchema(Schema):
    data = fields.List(fields.Nested(MikrotikSchema))

class UpdateMikrotikSchema(Schema):
    mikrotik_id = fields.Integer(required=True, metadata={"description":"Site ID"})
    name = fields.String(metadata={"description":"Name Mikrotik"})
    ipaddress = fields.String(metadata={"description":"IP/Host Mikrotik"})
    username = fields.String(metadata={"description":"Usename API Mikrotik"})
    password = fields.String(metadata={"description":"Password API Mikrotik"})
    apiport = fields.Integer(metadata={"description":"API Port Mikrotik"})
    site_id = fields.Integer(metadata={"description":"Site ID"})

class DeleteMikrotikSchema(Schema):
    mikrotik_id = fields.Integer(required=True, metadata={"description":"Site ID"})


class MmikrotikApi(MethodResource, Resource):
    @doc(description='Create Mikrotik', tags=['Mikrotik'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(CreateMikrotikSchema, location=('json'))
    @auth.login_required(role=['api','noc','superadmin'])
    def post(self, **kwargs):
        operator = auth.current_user()
        name = kwargs['name']
        ipaddress = kwargs['ipaddress']
        username = kwargs['username']
        password = kwargs['password']
        apiport = kwargs['apiport']
        try:
            site_id = kwargs['site_id']
        except:
            site_id = None

        name_exist = MmikrotikModel.query.filter_by(name=name).first()
        if name_exist:
            abort(409, 'name conflict')
        ip_exist = MmikrotikModel.query.filter_by(ipaddress=ipaddress, apiport=apiport).first()
        if ip_exist:
            abort(409, 'ip/host conflict')

        new_mikrotik = MmikrotikModel(name, ipaddress, username, password, apiport, site_id)
        db.session.add(new_mikrotik)
        db.session.commit()

        current_app.logger.info('Mikrotik {} added by {}'.format(new_mikrotik.mikrotik_id, operator.username))

        mesg = {"message":"success"}
        respone = jsonify(mesg)
        respone.status_code = 201
        return respone

    @doc(description='List Mikrotik', tags=['Mikrotik'], security=[{"ApiKeyAuth": []}])
    @marshal_with(ListMikrotikSchema)
    @auth.login_required(role=['api','noc','superadmin','teknisi','admin'])
    def get(self, **kwargs):
        operator = auth.current_user()
        if operator.role in ['teknisi','admin']:
            allowed_site = AllowedSiteUserModel.query.filter_by(username=operator.username).all()
            list_allowed = []
            for _allowed in allowed_site:
                list_allowed.append(_allowed.site_id)
            try:
                id = request.args.get('mikrotik_id')
                if id != None:
                    data_sites = MmikrotikModel.query.filter(
                    MmikrotikModel.site_id.in_(list_allowed)
                    ).filter_by(mikrotik_id=id).first()
                    if data_sites:
                        return jsonify(data_sites.to_dict())
                    abort(404, 'id not found')
            except:
                pass
            list_mikrotik = MmikrotikModel.query.filter(
                    MmikrotikModel.site_id.in_(list_allowed)
                    ).order_by(MmikrotikModel.name.asc()).all()
            data = []
            for mikrotik in list_mikrotik:
                data.append(mikrotik.to_dict())

            return jsonify(data)
        
        try:
            id = request.args.get('mikrotik_id')
            if id != None:
                data_sites = MmikrotikModel.query.filter_by(mikrotik_id=id).first()
                if data_sites:
                    return jsonify(data_sites.to_dict())
                abort(404, 'id not found')
        except:
            pass
        list_mikrotik = MmikrotikModel.query.order_by(MmikrotikModel.name.asc()).all()
        data = []
        for mikrotik in list_mikrotik:
            data.append(mikrotik.to_dict())

        return jsonify(data)
    
    @doc(description='Update Mikrotik', tags=['Mikrotik'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(UpdateMikrotikSchema, location=('json'))
    @auth.login_required(role=['api','noc','superadmin'])
    def put(self, **kwargs):
        operator = auth.current_user()
        mikrotik_id = kwargs['mikrotik_id']
        id_exists = MmikrotikModel.query.filter_by(mikrotik_id=mikrotik_id).first()
        if id_exists:
            try:
                name = kwargs['name']
                id_exists.name = name
            except:
                pass

            try:
                ipaddress = kwargs['ipaddress']
                id_exists.ipaddress = ipaddress
            except:
                pass

            try:
                username = kwargs['username']
                id_exists.username = username
            except:
                pass

            try:
                password = kwargs['password']
                id_exists.password = password
            except:
                pass

            try:
                apiport = kwargs['apiport']
                id_exists.apiport = apiport
            except:
                pass

            try:
                site_id = kwargs['site_id']
                id_exists.site_id = site_id
            except:
                pass
            
            db.session.commit()
            current_app.logger.info('Mikrotik {} Updated by {}'.format(id_exists.mikrotik_id, operator.username))
            return jsonify({'message':'success'})

        abort(404, "id Not Found")
    
    @doc(description='Delete Mikrotik', tags=['Mikrotik'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(DeleteMikrotikSchema, location=('json'))
    @auth.login_required(role=['api','noc','superadmin'])
    def delete(self, **kwargs):
        operator = auth.current_user()
        mikrotik_id = kwargs['mikrotik_id']
        id_exists = MmikrotikModel.query.filter_by(mikrotik_id=mikrotik_id).first()
        if id_exists:
            current_app.logger.info('Mikrotik {} deleted by {}'.format(id_exists.mikrotik_id, operator.username))
            db.session.delete(id_exists)
            db.session.commit()
            return jsonify({'message':'success'})
        
        abort(404, "id Not Found")


class InfoMmikrotikApi(MethodResource, Resource):
    @doc(description='Info Mikrotik', tags=['Mikrotik'], security=[{"ApiKeyAuth": []}])
    @marshal_with(MikrotikSchema)
    @auth.login_required(role=['api','noc','superadmin','teknisi','admin'])
    def get(self, **kwargs):
        pass