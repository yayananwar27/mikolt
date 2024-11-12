from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort
from sqlalchemy import or_, and_

from sites.models import SitesModel
from mmikrotik.models import MmikrotikModel

from accessapp.authapp import auth

from .models import db, ClientPPPModel
from userlogin.models import AllowedSiteUserModel

from dotenv import load_dotenv
import os
load_dotenv()

class CreateClientPPPSchema(Schema):
    name = fields.String(required=True, metadata={"description":"Name/Username client"})
    status = fields.String(required=True, metadata={"description":"status enable/disable"})
    password = fields.String(required=False, metadata={"description":"Password ppp secret"})
    profile = fields.String(required=False, metadata={"description":"name PPP Profile"})
    service_type = fields.String(required=False, metadata={"description":"name service type any/async/l2tp/ovpn/pppoe/pptp/sstp"})
    mikrotik_id = fields.Integer(required=False, metadata={"description":"Mikrotik ID"})
    comment = fields.String(required=False, allow_none=True,  metadata={"description":"comment PPP Profile"})
    configuration = fields.String(required=False, allow_none=True, metadata={"description":"Configuration Status configured/unconfigured"})

class ListClientPPPSchema(Schema):
    data = fields.List(fields.Nested(CreateClientPPPSchema))
    count = fields.Integer(metadata={"description":"Jumlah User"})

class UpdateClientPPPSchema(Schema):
    client_id = fields.Integer(required=False, metadata={"description":"ID client"})
    name = fields.String(required=True, metadata={"description":"Name/Username client"})
    status = fields.String(required=False, metadata={"description":"status enable/disable"})
    password = fields.String(required=False, metadata={"description":"Password ppp secret"})
    profile = fields.String(required=False, metadata={"description":"name PPP Profile"})
    service_type = fields.String(required=False, metadata={"description":"name service type any/async/l2tp/ovpn/pppoe/pptp/sstp"})
    mikrotik_id = fields.Integer(required=False, metadata={"description":"Mikrotik ID"})
    comment = fields.String(required=False, allow_none=True, metadata={"description":"comment PPP Profile"})
    configuration = fields.String(required=False, metadata={"description":"Configuration Status configured/unconfigured"})

class DeleteClientPPPSchema(Schema):
    client_id = fields.Integer(required=True, metadata={"description":"ID client"})

class ClientPPPSecretsApi(MethodResource, Resource):
    @doc(description='Create Client PPP', tags=['Client PPP'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(CreateClientPPPSchema, location=('json'))
    @auth.login_required(role=['api','noc', 'superadmin', 'teknisi'])
    def post(self, **kwargs):
        name = kwargs['name']
        status = kwargs['status']
        
        operator = auth.current_user()
        if operator.role in ['teknisi']:
            allowed_site = AllowedSiteUserModel.query.filter_by(username=operator.username).all()
            list_allowed = []
            for _allowed in allowed_site:
                list_allowed.append(_allowed.site_id)
            code_list = SitesModel.query.filter(
                SitesModel.site_id.in_(list_allowed)
            ).order_by(SitesModel.code.asc()).all()
        
        else:
            code_list = SitesModel.query.order_by(SitesModel.code.asc()).all()
        
        valid = False
        site_id = None
        #code valided
        for code in code_list:
            if code.code in name:
                valid = True
                site_id = code.site_id
                break
        if valid == False:
            abort(400, "invalid name format")

        if status not in ['enable', 'disable']:
            abort(400, "Invalid status")

        password = None
        profile = None
        service_type = None
        mikrotik_id = None
        comment = None

        if 'password' in kwargs:
            password = kwargs['password']

        if 'mikrotik_id' in kwargs:
            mikrotik_id = kwargs['mikrotik_id']
            if operator.role in ['teknisi']:
                mikrotik_exists = MmikrotikModel.query.filter(
                MmikrotikModel.site_id.in_(list_allowed)
                ).filter_by(mikrotik_id=mikrotik_id).first()
            else:
                mikrotik_exists = MmikrotikModel.query.filter_by(mikrotik_id=mikrotik_id).first()
            if not mikrotik_exists:
                abort(400, "invalid mikrotik id")
            if mikrotik_exists.site_id != site_id:
                abort(400, "invalid code and site id")

        if 'profile' in kwargs:
            profile = kwargs['profile']
            try:
                len_profile = mikrotik_exists._get_profile_ppoe(profile)
            except:
                if operator.role in ['teknisi']:
                    data_router = MmikrotikModel.query.filter(
                        MmikrotikModel.site_id.in_(list_allowed)
                    ).order_by(MmikrotikModel.name.asc()).all()
                else:
                    data_router = MmikrotikModel.query.order_by(MmikrotikModel.name.asc()).all()
                for router in data_router:
                    len_profile = router._get_profile_ppoe(profile)
                    if len(len_profile)>0:
                        break
            if len(len_profile) < 1:
                abort(400, "invalid profile")
            
        if 'service_type' in kwargs:
            service_type = kwargs['service_type']
            if service_type not in ['any', 'async', 'l2tp', 'ovpn', 'pppoe', 'pptp', 'sstp']:
                abort(400, "invalid service type")

        if 'comment' in kwargs:
            comment = kwargs['comment']

        if 'configuration' in kwargs:
            configuration = kwargs['configuration']
            if configuration not in ['configured', 'unconfigured']:
                abort(400, "invalid configuration info")
        else:
            configuration = 'unconfigured'

        add_clientppp = ClientPPPModel(name, status, configuration, password, profile, service_type, mikrotik_id, comment)
        db.session.add(add_clientppp)
        db.session.commit()
        current_app.logger.info('PPP addedd {} by {}'.format(add_clientppp.client_id, operator.username))
        mesg = {"message":"success"}
        respone = jsonify(mesg)
        respone.status_code = 201
        return respone
    
    @doc(description='list Client PPP', tags=['Client PPP'], security=[{"ApiKeyAuth": []}])
    @marshal_with(ListClientPPPSchema)
    @auth.login_required(role=['api','noc', 'superadmin', 'teknisi', 'admin'])
    def get(self):
        operator = auth.current_user()
        if operator.role in ['teknisi', 'teknisi', 'admin']:
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
            
        
        if 'client_id' in request.args:
            id = request.args.get('client_id')
            if id != None:
                try:
                    stats = int(request.args.get('stats'))
                except:
                    stats = 0
                if stats == 1:
                    if operator.role in ['teknisi', 'teknisi', 'admin']:
                        data_clientppp = ClientPPPModel.query.filter(
                            ClientPPPModel.mikrotik_id.in_(allowed_mikrotik),
                            ClientPPPModel.client_id == id
                            ).first()
                        if not data_clientppp:
                            data_clientppp = ClientPPPModel.query.filter(
                                ClientPPPModel.mikrotik_id.in_(allowed_mikrotik),
                                ClientPPPModel.name == id
                                ).first()
                    else:
                        data_clientppp = ClientPPPModel.query.filter(ClientPPPModel.client_id == id).first()
                        if not data_clientppp:
                            data_clientppp = ClientPPPModel.query.filter(ClientPPPModel.name == id).first()
                        
                    if data_clientppp:
                        return jsonify(data_clientppp.to_dict_stats())
                else:
                    if operator.role in ['teknisi', 'teknisi', 'admin']:
                        data_clientppp = ClientPPPModel.query.filter(ClientPPPModel.client_id == id).first()
                        if not data_clientppp:
                            data_clientppp = ClientPPPModel.query.filter(ClientPPPModel.name == id).first()

                    else:
                        data_clientppp = ClientPPPModel.query.filter(ClientPPPModel.client_id == id).first()
                        if not data_clientppp:
                            data_clientppp = ClientPPPModel.query.filter(ClientPPPModel.name == id).first()
                    
                    if data_clientppp:
                        return jsonify(data_clientppp.to_dict())
                data = {
                    'data':[],
                    'count':0
                }
                return jsonify(data)

        if 'site_id' in request.args and not ('page' in request.args and 'per_page' in request.args):    
            site_id = request.args.get('site_id')
            if site_id != None:
                if operator.role in ['teknisi', 'teknisi', 'admin']:
                    site_exists = SitesModel.query.filter(
                        SitesModel.site_id.in_(allowed_site)
                    ).filter_by(site_id=site_id).first()
                else:
                    site_exists = SitesModel.query.filter_by(site_id=site_id).first()
                
                if site_exists:
                    data_mikrotik = MmikrotikModel.query.filter_by(site_id=site_id).all()
                    _data = []
                    for mikrotik in data_mikrotik:
                        data_clientppp = ClientPPPModel.query.filter_by(mikrotik_id=mikrotik.mikrotik_id).all()
                        for clientppp in data_clientppp:
                            _data.append(clientppp.to_dict())
                    
                    data = {
                        'data':_data,
                        'count':len(_data)
                    }
                    return jsonify(data)
                data = {
                    'data':[],
                    'count':0
                }
                return jsonify(data)


        if 'profile' in request.args:
            str_profile = request.args.get('profile')
            if str_profile != None:
                if operator.role in ['teknisi', 'teknisi', 'admin']:
                    data_clientppp = ClientPPPModel.query.filter(
                        ClientPPPModel.mikrotik_id.in_(allowed_mikrotik)
                    ).filter_by(profile=str_profile).all()
                else:
                    data_clientppp = ClientPPPModel.query.filter_by(profile=str_profile).all()
                if data_clientppp:
                    _data = []
                    for clientppp in data_clientppp:
                        _data.append(clientppp.to_dict())
                        
                    data = {
                        'data':_data,
                        'count':len(_data)
                    }
                    return jsonify(data)
                else:
                    data = {
                        'data':[],
                        'count':0
                    }
                    return jsonify(data)

        
        if 'mikrotik_id' in request.args:
            mikrotik_id = request.args.get('mikrotik_id')
            if operator.role in ['teknisi', 'teknisi', 'admin']:
                data_mikrotik = MmikrotikModel.query.filter(
                    MmikrotikModel.site_id.in_(allowed_site)
                ).filter_by(mikrotik_id=mikrotik_id).first()
            else:
                data_mikrotik = MmikrotikModel.query.filter_by(mikrotik_id=mikrotik_id).first()
            if data_mikrotik:
                _data = []
                data_clientppp = ClientPPPModel.query.filter_by(mikrotik_id=data_mikrotik.mikrotik_id).all()
                for clientppp in data_clientppp:
                    _data.append(clientppp.to_dict())
                data = {
                    'data':_data,
                    'count':len(_data)
                }
                return jsonify(data)
            data = {
                'data':[],
                'count':0
            }
            return jsonify(data)
        
        #get data server side
        if ('page' in request.args and 'per_page' in request.args) or 'search' in request.args:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            search = request.args.get('search', '', type=str)

            query = ClientPPPModel.query

            if 'configuration' in request.args or 'status' in request.args or 'site_id' in request.args:
                _site_id = request.args.get('site_id', None, type=int)

                if _site_id != None:
                    if operator.role in ['teknisi', 'teknisi', 'admin']:
                        site_exists = SitesModel.query.filter(
                            SitesModel.site_id.in_(allowed_site)
                        ).filter_by(site_id=_site_id).first()
                    else:
                        site_exists = SitesModel.query.filter_by(site_id=_site_id).first()
                    if site_exists:
                        data_mikrotik = MmikrotikModel.query.filter_by(site_id=_site_id).all()
                        _data_mikrotik = []
                        for mikrotik in data_mikrotik:
                            _data_mikrotik.append(mikrotik.mikrotik_id)

                        query = query.filter(
                            ClientPPPModel.mikrotik_id.in_(_data_mikrotik))
                        

                _configuration = request.args.get('configuration', '', type=str)
                _status = request.args.get('status', '', type=str)
                # initial_filter = and_(
                #     ClientPPPModel.status.like(f'{_status}'),
                #     ClientPPPModel.configuration.like(f'{_configuration}')
                # )
                # query = query.filter(initial_filter)
                if operator.role in ['teknisi', 'teknisi', 'admin']:
                    query = query.filter(
                        ClientPPPModel.mikrotik_id.in_(allowed_mikrotik),
                        ClientPPPModel.status.like(f'%{_status}%'))
                    query = query.filter(ClientPPPModel.configuration.like(f'{_configuration}%'))                   
                else:
                    query = query.filter(ClientPPPModel.status.like(f'%{_status}%'))
                    query = query.filter(ClientPPPModel.configuration.like(f'{_configuration}%'))                   
                
                if len(search)>1:
                    search_filter = or_(
                        ClientPPPModel.name.like(f'%{search}%'),
                        ClientPPPModel.profile.like(f'%{search}%'),
                        ClientPPPModel.service_type.like(f'%{search}%'),
                        ClientPPPModel.comment.like(f'%{search}%')
                    )
                    query = query.filter(search_filter)
            else:
                if search:
                    if operator.role in ['teknisi', 'teknisi', 'admin']:
                        search_filter = or_(
                            ClientPPPModel.mikrotik_id.in_(allowed_mikrotik),
                            ClientPPPModel.name.like(f'%{search}%'),
                            ClientPPPModel.profile.like(f'%{search}%'),
                            ClientPPPModel.service_type.like(f'%{search}%'),
                            ClientPPPModel.status.like(f'%{search}%'),
                            ClientPPPModel.configuration.like(f'%{search}%'),
                            ClientPPPModel.comment.like(f'%{search}%')
                        )
                    else:
                        search_filter = or_(
                            ClientPPPModel.name.like(f'%{search}%'),
                            ClientPPPModel.profile.like(f'%{search}%'),
                            ClientPPPModel.service_type.like(f'%{search}%'),
                            ClientPPPModel.status.like(f'%{search}%'),
                            ClientPPPModel.configuration.like(f'%{search}%'),
                            ClientPPPModel.comment.like(f'%{search}%')
                        )
                    query = query.filter(search_filter)

            pagination = query.paginate(page=page, per_page=per_page,error_out=False)

            _data = [client.to_dict() for client in pagination.items]

            return jsonify({
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': pagination.page,
                'per_page': pagination.per_page,
                'data': _data
            })

        if operator.role in ['teknisi', 'teknisi', 'admin']:
            data_clientppp = ClientPPPModel.query.filter(
                ClientPPPModel.mikrotik_id.in_(allowed_mikrotik)
            ).order_by(ClientPPPModel.name.asc()).all()
        else:
            data_clientppp = ClientPPPModel.query.order_by(ClientPPPModel.name.asc()).all()
        _data  = []
        for client in data_clientppp:
            _data.append(client.to_dict())
        
        data = {
            'data':_data,
            'count':len(_data)
            }

        return jsonify(data)

    @doc(description='Update Client PPP', tags=['Client PPP'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(UpdateClientPPPSchema, location=('json'))
    @auth.login_required(role=['api','noc','superadmin','teknisi','admin'])
    def put(self, **kwargs):
        operator = auth.current_user()
        if operator.role in ['teknisi', 'teknisi', 'admin']:
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
            

        if 'client_id' in kwargs:
            client_id = kwargs['client_id']
            if operator.role in ['teknisi', 'teknisi', 'admin']:
                client_id_exists = ClientPPPModel.query.filter(
                ClientPPPModel.mikrotik_id.in_(allowed_mikrotik)
            ).filter_by(client_id=client_id).first()
            else:
                client_id_exists = ClientPPPModel.query.filter_by(client_id=client_id).first()
        else:
            name_cliet = kwargs['name']
            if operator.role in ['teknisi', 'teknisi', 'admin']:
                client_id_exists = ClientPPPModel.query.filter(
                ClientPPPModel.mikrotik_id.in_(allowed_mikrotik)
            ).filter_by(name=name_cliet).first()
            else:
                client_id_exists = ClientPPPModel.query.filter_by(name=name_cliet).first()

        if client_id_exists:
            if 'name' in kwargs:
                name = kwargs['name']
                code_list = SitesModel.query.order_by(SitesModel.code.asc()).all()
                valid = False
                site_id = []
                for code in code_list:
                    if code.code in name:
                        valid = True
                        site_id.append(code.site_id)
                        
                if valid == False:
                    abort(400, "invalid name format")
                client_id_exists.name = name

            if 'status' in kwargs:
                status = kwargs['status']
                if status not in ['enable', 'disable']:
                    abort(400, "Invalid status")
                client_id_exists.status = status
            
            if 'password' in kwargs:
                client_id_exists.password = kwargs['password']

            if 'service_type' in kwargs:
                service_type = kwargs['service_type']
                if service_type not in ['any', 'async', 'l2tp', 'ovpn', 'pppoe', 'pptp', 'sstp']:
                    abort(400, "invalid service type")
                client_id_exists.service_type = service_type
            
            if 'comment' in kwargs:
                client_id_exists.comment = kwargs['comment']

            mikrotik_exists = MmikrotikModel.query.filter_by(mikrotik_id=client_id_exists.mikrotik_id).first()
            if 'mikrotik_id' in kwargs:
                mikrotik_id = kwargs['mikrotik_id']
                mikrotik_exists = MmikrotikModel.query.filter_by(mikrotik_id=mikrotik_id).first()
                if not mikrotik_exists:
                    abort(400, "invalid mikrotik id")
                if mikrotik_exists.site_id not in site_id:
                    abort(400, "invalid code and site id")

                client_id_exists.mikrotik_id = mikrotik_id
            
            if 'profile' in kwargs:
                profile = kwargs['profile']
                len_profile = mikrotik_exists._get_profile_ppoe(profile)
                if len(len_profile) < 1:
                    abort(400, "invalid profile")
                client_id_exists.profile = profile
            
            if 'configuration' in kwargs:
                configuration = kwargs['configuration']
                if configuration not in ['configured', 'unconfigured']:
                    abort(400, 'invalid configuration info')
                client_id_exists.configuration = configuration
            
            from .models import created_time
            client_id_exists.last_update_at = created_time()
            client_id_exists.last_update_by = auth.current_user()
            db.session.commit()

            client_id_exists = ClientPPPModel.query.filter_by(client_id=client_id_exists.client_id).first()
            data = {'message':'success', 'mikrotik':None}
            if client_id_exists.ref_id != None:
                if client_id_exists.status == 'enable':
                    update_data = mikrotik_exists.update_user(client_id_exists.ref_id, client_id_exists.name, client_id_exists.service_type, client_id_exists.password, client_id_exists.profile, client_id_exists.comment)
                else:
                    update_data = mikrotik_exists.update_user(client_id_exists.ref_id, client_id_exists.name, client_id_exists.service_type, client_id_exists.password, str(os.environ["PROFILE_ISOLIR_NAME"]), client_id_exists.comment)
                try:
                    if update_data['messages'] == 'success':
                        data['mikrotik'] = 'mikrotik updated'
                    else:
                        data['mikrotik'] = 'mikrotik not updated'
                except Exception as e:
                    current_app.logger.error(e)
                    data['mikrotik'] = 'mikrotik not updated'
            elif client_id_exists.password != None and client_id_exists.profile != None and client_id_exists.mikrotik_id != None:
                if client_id_exists.status == 'enable':
                    add_data = mikrotik_exists._add_ppp_secret(client_id_exists.name, client_id_exists.service_type, client_id_exists.password, client_id_exists.profile, client_id_exists.comment)
                else:
                    add_data = mikrotik_exists._add_ppp_secret(client_id_exists.name, client_id_exists.service_type, client_id_exists.password, str(os.environ["PROFILE_ISOLIR_NAME"]), client_id_exists.comment)
                if add_data == True:
                    id_secret = mikrotik_exists._get_ppp_secret(client_id_exists.name)
                    client_id_exists.ref_id = id_secret[0]['id']
                    db.session.commit()
                    data['mikrotik'] = 'mikrotik added'
            else:
                data['mikrotik'] = 'mikrotik no action'

            current_app.logger.info('PPP Secret Updated {} by {}'.format(client_id_exists.name, operator.username))
            return jsonify(data)

        abort(404, 'id not found')

    @doc(description='Delete Client PPP', tags=['Client PPP'], security=[{"ApiKeyAuth": []}])
    @use_kwargs(DeleteClientPPPSchema, location=('json'))
    @auth.login_required(role=['api','noc','superadmin','teknisi'])
    def delete(self, **kwargs):
        operator = auth.current_user()
        if operator.role in ['teknisi', 'teknisi', 'admin']:
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
            
        client_id = kwargs['client_id']
        if operator.role in ['teknisi', 'teknisi', 'admin']:
            client_id_exists = ClientPPPModel.query.filter(
                ClientPPPModel.mikrotik_id.in_(allowed_mikrotik)
            ).filter_by(client_id=client_id).first()
        else:
            client_id_exists = ClientPPPModel.query.filter_by(client_id=client_id).first()
        if client_id_exists:
            data = {'message':'success', 'mikrotik':'no action'}
            if client_id_exists.ref_id != None:
                mikrotik_exists = MmikrotikModel.query.filter_by(mikrotik_id=client_id_exists.mikrotik_id).first()
                removed = mikrotik_exists.delete_user(client_id_exists.ref_id, client_id_exists.name)
                data['mikrotik'] = removed
                
            db.session.delete(client_id_exists)
            db.session.commit()
            current_app.logger.info('PPP Secret Deleted {} by {}'.format(client_id_exists.name, operator.username))
            return jsonify(data)

        abort(404, 'id not found')

class SearchIDClientPPPSecretsApi(MethodResource, Resource):
    @doc(description='Info Client PPP by ID', tags=['Client PPP'], security=[{"ApiKeyAuth": []}])
    @auth.login_required(role=['api','noc', 'superadmin', 'teknisi', 'admin'])
    def get(self):
        pass

class SearchSiteClientPPPSecretsApi(MethodResource, Resource):
    @doc(description='Info Client PPP by Site ID', tags=['Client PPP'], security=[{"ApiKeyAuth": []}])
    @auth.login_required(role=['api','noc', 'superadmin', 'teknisi', 'admin'])
    def get(self):
        pass

class SearchIDClientPPPStatsSecretsApi(MethodResource, Resource):
    @doc(description='Info Client PPP by  ID and stats', tags=['Client PPP'], security=[{"ApiKeyAuth": []}])
    @auth.login_required(role=['api','noc', 'superadmin', 'teknisi', 'admin'])
    def get(self):
        pass

class SearchProfileClientPPPSecretsApi(MethodResource, Resource):
    @doc(description='Info Client PPP by Profile packaga name', tags=['Client PPP'], security=[{"ApiKeyAuth": []}])
    @auth.login_required(role=['api','noc', 'superadmin', 'teknisi', 'admin'])
    def get(self):
        pass

class SearchMikrotikClientPPPSecretsApi(MethodResource, Resource):
    @doc(description='Info Client PPP by Site ID Mikrotik', tags=['Client PPP'], security=[{"ApiKeyAuth": []}])
    @auth.login_required(role=['api','noc', 'superadmin', 'teknisi', 'admin'])
    def get(self):
        pass

class ServerSideClientPPPSchema(Schema):
    current_page = fields.Integer(metadata={"description":"Current page number"})
    data = fields.List(fields.Nested(UpdateClientPPPSchema))
    pages = fields.Integer(metadata={"description":"Total Pages"})
    per_page = fields.Integer(metadata={"description":"Data per page"})
    total = fields.Integer(metadata={"description":"Total Data"})

class ServersideMikrotikClientPPPSecretsApi(MethodResource, Resource):
    @doc(description='Server side Client PPP table', tags=['Client PPP'], security=[{"ApiKeyAuth": []}])
    @marshal_with(ServerSideClientPPPSchema)
    @auth.login_required(role=['api','noc', 'superadmin', 'teknisi', 'admin'])
    def get(self):
        pass
