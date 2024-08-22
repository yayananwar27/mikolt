from config import db
from flask import current_app

import routeros_api
from dotenv import load_dotenv
import os
load_dotenv()

def init_db(app):
    with app.app_context():
        db.create_all()

def convert_to_utf8(data):
    for item in data:
        for key, value in item.items():
            if isinstance(value, bytes):
                try:
                    item[key] = value.decode('utf-8')
                except:
                    item[key] = value.decode('latin-1')
    return data

class MmikrotikModel(db.Model):
    __tablename__ = 'mmikrotik'
    mikrotik_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    ipaddress = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(255), nullable=False)
    password  = db.Column(db.String(255), nullable=False)
    apiport = db.Column(db.Integer, nullable=False)
    site_id = db.Column(db.Integer, nullable=True)
    #site_id = db.Column(db.Integer, db.ForeignKey('sites.site_id', ondelete='CASCADE'), nullable=False)
    #clientppp_fk = db.relationship('clientppp', backref='mmikrotik', cascade="all, delete", passive_deletes=True, lazy=True)

    
    def __init__(self, name, ipaddress, username, password, apiport, site_id=None):
        self.name = name
        self.ipaddress = ipaddress
        self.username = username
        self.password = password
        self.apiport = apiport
        self.site_id = site_id
    
    
    def to_dict(self):
        connected = 0
        if self._get_mikrotik_status() != None:
            connected = 1 
        data = {
            'mikrotik_id':self.mikrotik_id,
            'name':self.name,
            'ipaddress':self.ipaddress,
            'username':self.username,
            'password':self.password,
            'apiport':self.apiport,
            'site_id':self.site_id,
            'current_info':self._get_mikrotik_status(),
            'connected':connected
        }
        return data
    
    def _get_routeros_api(self):
        connection = routeros_api.RouterOsApiPool(self.ipaddress, username=self.username, password=self.password, port=self.apiport, plaintext_login=True)
        return connection.get_api()

    def _get_mikrotik_status(self):
        try:
            api = self._get_routeros_api()
            system_resource = api.get_resource('/system/resource').get()
            system_health = api.get_resource('/system/health').get()
            mikrotik_status = system_resource[0]
            try:
                if len(system_health)==1:
                    cpu_temp = {'cpu-temperature':system_health[0]['cpu-temperature']}
                elif len(system_health)>1:
                    for health in system_health:
                        if health['name'] == 'cpu-temperature':
                            cpu_temp = {'cpu-temperature': health['value']}        
                else:
                    if system_health[0]['state'] == 'disabled':
                        cpu_temp = {'cpu-temperature':0}    
                    else:
                        cpu_temp = {'cpu-temperature':system_health[0]['temperature']}
            except Exception as e:
                #current_app.logger.error(e)
                cpu_temp = {'cpu-temperature':0}    
            mikrotik_status.update(cpu_temp)
        except Exception as e:
            #current_app.logger.error(e)
            mikrotik_status = None

        return mikrotik_status

    def _get_profile_ppoe(self, search_name=None):
        try:
            api = self._get_routeros_api()
            if search_name != None:
                list_ppp_profile = api.get_resource('/ppp/profile').get(name=str(search_name))
            else:
                list_ppp_profile = api.get_resource('/ppp/profile').get()
            
            return list_ppp_profile
        except Exception as e:
            current_app.logger.error(e)
            return None
        
    def _get_profile_ppoe_isolir(self):
        try:
            api = self._get_routeros_api()
            list_ppp_profile = api.get_resource('/ppp/profile').get(name=str(os.environ["PROFILE_ISOLIR_NAME"]))
            if len(list_ppp_profile)>0:
                for ppp_profile in list_ppp_profile:
                    status = True
                    data = ppp_profile
            else:
                status = False
                data = None
            
            return {
                'status': status,
                'data': data
            }
        except Exception as e:
            current_app.logger.error(e)
            return None

    def _get_ppp_secret(self, search_name=None):
        try:
            api = self._get_routeros_api()
            if search_name != None:
                list_ppp_secrets = api.get_resource('/ppp/secret').get(name=str(search_name))
            else:
                list_ppp_secrets = api.get_resource('/ppp/secret').get()
            return list_ppp_secrets
        except Exception as e:
            current_app.logger.error(e)
            return None

    def _get_int_pppoeserver(self, search_user=None):
        try:
            api = self._get_routeros_api()
            if search_user != None:
                list_pppoe_interface = api.get_resource('/interface/pppoe-server').get(user=str(search_user))
            else:
                list_pppoe_interface = api.get_resource('/interface/pppoe-server').get()
            return list_pppoe_interface
        except Exception as e:
            current_app.logger.error(e)
            return None

    def _get_eth_status(self, search_name=None):
        #ada bracket <>
        try:
            api = self._get_routeros_api()
            if search_name != None:
                list_eth_stats = api.get_resource('/interface').get(name=search_name)
            else:
                #list_eth_stats = api.get_resource('/interface').get(type='pppoe-in')
                list_eth_stats = api.get_resource('/interface').get()
            return list_eth_stats
        except Exception as e:
            current_app.logger.error(e)
            return None

    def _get_mon_traffic(self, search_name):
        #ada bracket <>
        try:
            api = self._get_routeros_api()
            monitor_eth_stats = convert_to_utf8(api.get_binary_resource('/interface').call('monitor-traffic', {'interface': str(search_name), 'once':''}))          
            return monitor_eth_stats
        except Exception as e:
            current_app.logger.error(e)
            return None
        
    def _get_mon_ipadress(self, search_name):
        #ada bracket <>
        try:
            api = self._get_routeros_api()
            list_pppoe_ip = convert_to_utf8(api.get_binary_resource('/interface/pppoe-server').call('monitor', {'numbers':str(search_name), 'once':''}))
            return list_pppoe_ip
        except Exception as e:
            current_app.logger.error(e)
            return None
        
    def _add_ppp_secret(self, name, service, password, profile, comment=None, disabled=None):
        try:
            api = self._get_routeros_api()
            ppp_secrets = api.get_resource('/ppp/secret')
            if disabled != None and disabled in ['true', 'false']:
                if comment == None:
                    ppp_secrets.add(name=str(name), service=str(service), password=str(password), profile=str(profile), disabled=disabled)
                else:
                    ppp_secrets.add(name=str(name), service=str(service), password=str(password), profile=str(profile), comment=str(comment), disabled=disabled)
            else:
                if comment == None:
                    ppp_secrets.add(name=str(name), service=str(service), password=str(password), profile=str(profile))
                else:
                    ppp_secrets.add(name=str(name), service=str(service), password=str(password), profile=str(profile), comment=str(comment))
            
            return True
        except Exception as e:
            current_app.logger.error(e)
            return None
    
    def change_profile_user(self, usernya, profilenya):
        try:
            api = self._get_routeros_api()
            return_data = {'message':None}
            _data_user = self._get_ppp_secret(search_name=usernya)
            _data_profile = self._get_profile_ppoe(search_name=profilenya)
            if len(_data_user)<1:
                return_data['message'] = 'User Not Found'
            elif len(_data_user)>1:
                return_data['message'] = '{} User To Much Found'.format(len(_data_user))
            elif len(_data_profile)<1:
                return_data['message'] = 'Profile Not Found'
            elif len(_data_profile)>1:
                return_data['message'] = '{} Profile To Much Found'.format(_data_profile)
            else:
                #SET user profile
                user_ppp_secrets = api.get_resource('/ppp/secret')
                user_ppp_secrets.set(id=str(_data_user[0]['id']), profile=str(profilenya))

                _user_intnya = self._get_int_pppoeserver(search_user=_data_user[0]['name'])
                if len(_user_intnya)<1:
                    return_data['dial_interface'] = 'Not Foud'
                elif len(_user_intnya)>1:
                    return_data['dial_interface'] = '{} Found'.format(len(_user_intnya))
                else:
                    return_data['dial_interface'] = 'Foud'
                    list_pppoe = api.get_resource('/interface/pppoe-server')
                    list_pppoe.remove(id=str(_user_intnya[0]['id']))
                    return_data['message'] = 'success'
            return return_data
        except Exception as e:
            current_app.logger.error(e)
            return None
        
    def update_user(self, id, name, service, password, profile, comment=None):
        try:
            api = self._get_routeros_api()
            return_data = {'messages':None}
            user_ppp_secrets = api.get_resource('/ppp/secret')
            if comment != None:
                user_ppp_secrets.set(id=id, name=name, service=service, password=password, profile=profile, comment=comment)
            else:
                user_ppp_secrets.set(id=id, name=name, service=service, password=password, profile=profile)                
            _user_intnya = self._get_int_pppoeserver(search_user=name)
            if len(_user_intnya)<1:
                return_data['dial_interface'] = 'Not Foud'
            elif len(_user_intnya)>1:
                return_data['dial_interface'] = '{} Found'.format(len(_user_intnya))
            else:
                return_data['dial_interface'] = 'Foud'
                current_app.logger.debug(_user_intnya)
                list_pppoe = api.get_resource('/interface/pppoe-server')
                list_pppoe.remove(id=str(_user_intnya[0]['id']))
            return_data['messages'] = 'success'
            return return_data
        except Exception as e:
            current_app.logger.error(return_data)
            current_app.logger.error(e)
            return None
        
    def delete_user(self, id, name):
        try:
            api = self._get_routeros_api()
            user_ppp_secrets = api.get_resource('/ppp/secret')
            user_ppp_secrets.remove(id=id)
            msg = {'secret':True}
            try:
                _user_intnya = self._get_int_pppoeserver(search_user=name)
                list_pppoe = api.get_resource('/interface/pppoe-server')
                list_pppoe.remove(id=str(_user_intnya[0]['id']))
                msg['interface']=True
            except:
                msg['interface']=False
            return msg
        except Exception as e:
            current_app.logger.error(e)
            return None
