from config import db
from flask import current_app
def init_db(app):
    with app.app_context():
        db.create_all()

from datetime import datetime
def created_time():
    dt_now = datetime.now()
    date = dt_now.strftime("%Y-%m-%d %H:%M:%S")
    return str(date)

class OltDevicesModels(db.Model):
    __tablename__ = 'oltdevices'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    host = db.Column(db.String(255), nullable=False)
    telnet_user = db.Column(db.String(255), nullable=False)
    telnet_pass = db.Column(db.String(255), nullable=False)
    telnet_port = db.Column(db.Integer, nullable=False)
    snmp_ro_com = db.Column(db.String(255), nullable=False)
    snmp_wr_com = db.Column(db.String(255), nullable=False)
    snmp_port = db.Column(db.Integer, nullable=False)
    id_site = db.Column(db.Integer, nullable=False)
    id_merk = db.Column(db.Integer, db.ForeignKey('oltmerk.id', ondelete='CASCADE'), nullable=False)
    id_software = db.Column(db.Integer, db.ForeignKey('oltsoftware.id', ondelete='CASCADE'), nullable=False)
    oltdevicecard_fk = db.relationship('OltDevicesCardModels', backref='oltdevicecards', cascade="all, delete", passive_deletes=True, lazy=True)
    
    def __init__(
            self, 
            name, 
            host, 
            telnet_user,
            telnet_pass,
            telnet_port,
            snmp_ro_com,
            snmp_wr_com,
            snmp_port,
            id_site,
            id_merk,
            id_software
            ):
        
        self.name = name
        self.host = host
        self.telnet_user = telnet_user
        self.telnet_pass = telnet_pass
        self.telnet_port = telnet_port
        self.snmp_ro_com = snmp_ro_com
        self.snmp_wr_com = snmp_wr_com
        self.snmp_port = snmp_port
        self.id_site = id_site
        self.id_merk = id_merk
        self.id_software = id_software

    def to_dict(self):
        from ooltmaster.models import OltMerkModels, OltSoftModels
        from sites.models import SitesModel
        info_merk = OltMerkModels.query.filter_by(id=self.id_merk).first()
        info_soft = OltSoftModels.query.filter_by(id=self.id_software).first()
        info_site = SitesModel.query.filter_by(site_id=self.id_site).first()
        try:
            info_site = info_site.to_dict()
        except:
            info_site = None
        return {
            'id':self.id,
            'name':self.name,
            'host':self.host,
            'telnet_user':self.telnet_user,
            'telnet_pass':self.telnet_pass,
            'telnet_port':self.telnet_port,
            'snmp_ro_com':self.snmp_ro_com,
            'snmp_wr_com':self.snmp_wr_com,
            'snmp_port':self.snmp_port,
            'id_site':self.id_site,
            'id_merk':self.id_merk,
            'id_software':self.id_software,
            'info_site':info_site,
            'info_merk':info_merk.to_dict(),
            'info_software':info_soft.to_dict()
        }
    
    def to_dict_info(self):
        from ooltmaster.models import OltMerkModels, OltSoftModels
        from sites.models import SitesModel
        info_merk = OltMerkModels.query.filter_by(id=self.id_merk).first()
        info_soft = OltSoftModels.query.filter_by(id=self.id_software).first()
        info_site = SitesModel.query.filter_by(site_id=self.id_site).first()
        try:
            info_site = info_site.to_dict()
        except:
            info_site = None
        return {
            'id':self.id,
            'name':self.name,
            'host':self.host,
            'telnet_user':self.telnet_user,
            'telnet_pass':self.telnet_pass,
            'telnet_port':self.telnet_port,
            'snmp_ro_com':self.snmp_ro_com,
            'snmp_wr_com':self.snmp_wr_com,
            'snmp_port':self.snmp_port,
            'id_site':self.id_site,
            'id_merk':self.id_merk,
            'id_software':self.id_software,
            'uptime':self.oltdevice_uptime(),
            'info_site':info_site,
            'info_merk':info_merk.to_dict(),
            'info_software':info_soft.to_dict()
        }
    
    def oltdevice_uptime(self):
        from ooltcommands.models_uptime import OltCommandsUptimeModel
        script_python = OltCommandsUptimeModel.query.filter_by(
            id_software = self.id_software
        ).first()
        output = None
        if script_python:
            local_scope = {'self': self}
            exec(script_python.script_python, {}, local_scope)
            output = local_scope.get('output')   
        return output

    def oltdevice_showcard(self):
        from ooltcommands.models_showcard import OltCommandsShowCardModel
        script_python = OltCommandsShowCardModel.query.filter_by(
            id_software = self.id_software
        ).first()
        output = None
        if script_python:
            #print(script_python.script_python)
            local_scope = {'self': self}
            exec(script_python.script_python, {}, local_scope)
            output = local_scope.get('output')   
        return output
    
    def oltdevice_showcardpon(self, frame, slot, pon):
        from ooltcommands.models_showcardpon import OltCommandsPonInfoModel
        script_python = OltCommandsPonInfoModel.query.filter_by(
            id_software = self.id_software
        ).first()
        output = None
        if script_python:
            local_scope = {'self': self,'frame':frame,'slot':slot,'pon':pon}
            exec(script_python.script_python, {}, local_scope)
            output = local_scope.get('output')   
        return output
    
    def oltdevice_showuplink(self, frame, slot, pon):
        from ooltcommands.models_showcarduplink import OltCommandsUplinkInfoModel
        script_python = OltCommandsUplinkInfoModel.query.filter_by(
            id_software = self.id_software
        ).first()
        output = None
        if script_python:
            local_scope = {'self': self,'frame':frame,'slot':slot,'pon':pon}
            exec(script_python.script_python, {}, local_scope)
            output = local_scope.get('output')
        return output


    def oltdevice_showvlanuplinktag(self, name):
        from ooltcommands.models_showuplinkvlan import OltCommandShowVlanTagModel
        script_python = OltCommandShowVlanTagModel.query.filter_by(
            id_software = self.id_software
        ).first()
        output = None
        if script_python:
            local_scope = {'self': self,'name':name}
            exec(script_python.script_python, {}, local_scope)
            output = local_scope.get('output')   
        return output

    def oltdevice_showonutype(self):
        from ooltcommands.models_showcardonutype import OltCommandsOnuTypeModel
        script_python = OltCommandsOnuTypeModel.query.filter_by(
            id_software = self.id_software
        ).first()
        output = None
        if script_python:
            local_scope = {'self': self}
            exec(script_python.script_python, {}, local_scope)
            output = local_scope.get('output')   
        return output
    
    #add addan
    def add_list_card(self):
        card_list = self.oltdevice_showcard()
        for card in card_list:    
            new_card = OltDevicesCardModels(
                id,
                card['Frame'],
                card['Slot'],
                card['Slot'],
                card['CfgType'],
                card['SoftVer'],
                card['Status'],
                card['type_port'],
                created_time()
            )
            db.session.add(new_card)
            db.session.commit()
            new_card.add_list_cardpon()


    #show showann
    def show_list_card(self):
        data = []
        list_card = OltDevicesCardModels.query.filter_by(id_device=self.id).order_by(
            OltDevicesCardModels.type_port.asc()
        ).all()
        for card in list_card:
            data.append(card.to_dict())

        return data
    
    def show_list_portpon(self):
        data = []
        list_card = OltDevicesCardModels.query.filter_by(id_device=self.id, type_port=1).order_by(
            OltDevicesCardModels.type_port.asc()
        ).all()
        
        for card in list_card:
            data.append(card.pon_info())
        
        return data

    def show_list_uplink(self):
        data = []
        list_card = OltDevicesCardModels.query.filter_by(id_device=self.id, type_port=2).order_by(
            OltDevicesCardModels.type_port.asc()
        ).all()
        
        for card in list_card:
            #data.append(card.uplink_info())
            data = data+card.uplink_info()

        return data

    #delete deletan
    def delete_list_card(self):
        list_card = OltDevicesCardModels.query.filter_by(id_device=id).all()
        for card in list_card:
            card.delete_list_pon()
            db.session.delete(card)
            db.session.commit()

class OltDevicesCardModels(db.Model):
    __tablename__ = 'oltdevicecards'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_device = db.Column(db.Integer, db.ForeignKey('oltdevices.id', ondelete='CASCADE'), nullable=False)
    frame = db.Column(db.Integer, nullable=False)
    slot = db.Column(db.Integer, nullable=False)
    jml_port = db.Column(db.Integer, nullable=False)
    cfg_type = db.Column(db.String(255), nullable=False)
    soft_ver = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    type_port = db.Column(db.Integer, nullable=False) #1=GPON CARD,  2=Uplink Card
    last_update = db.Column(db.DateTime, nullable=False)
    oltcardpon_fk = db.relationship('OltDevicesCardPonModels', backref='oltcardpons', cascade="all, delete", passive_deletes=True, lazy=True)
    oltcarduplink_fk = db.relationship('OltDevicesCardUplinkModels', backref='oltcarduplink', cascade="all, delete", passive_deletes=True, lazy=True)
    

    def __init__(self, id_device, frame_number, slot_number, jml_port, cfg_type, soft_ver, status, type_port, last_update):
        self.id_device = id_device
        self.frame = frame_number
        self.slot = slot_number
        self.cfg_type = cfg_type
        self.jml_port = jml_port
        self.soft_ver = soft_ver
        self.status = status
        self.type_port = type_port
        self.last_update = last_update

    def to_dict(self):
        return {
            'id':self.id,
            'id_device':self.id_device,
            'frame':self.frame,
            'slot':self.slot,
            'cfg_type':self.cfg_type,
            'jml_port':self.jml_port,
            'soft_ver':self.soft_ver,
            'status':self.status,
            'type_port':self.type_port,
            'last_update':str(self.last_update)
        }
    
    def pon_info(self):
        data = {
            'id':self.id,
            'slot':self.slot,
            'type':self.cfg_type,
        }
        list_port = []
        if self.type_port == 1:
            list_ports = OltDevicesCardPonModels.query.filter_by(id_card=self.id).all()
            for port in list_ports:
                list_port.append(port.to_dict())

        data['list_port'] = list_port    
        return data
    
    def uplink_info(self):
        list_uplink = []
        if self.type_port == 2:
            list_uplinks = OltDevicesCardUplinkModels.query.filter_by(id_card=self.id).all()
            for uplink in list_uplinks:
                data_uplink = uplink.to_dict()
                oltnya = OltDevicesModels.query.filter_by(id=self.id_device).first()
                data_uplink['vlan_tag'] = oltnya.oltdevice_showvlanuplinktag(data_uplink['name'])
                list_uplink.append(data_uplink)
        return list_uplink

    #add addan
    def add_list_cardpon(self):
        oltdevice = OltDevicesModels.query.filter_by(id=self.id_device).first()
        if self.type_port == 1:
            for num_port in range(int(self.jml_port)):
                output = oltdevice.oltdevice_showcardpon(self.frame, self.slot, num_port)
                exists_pon = OltDevicesCardPonModels.query.filter_by(
                    id_card=self.id,
                    port=output['pon']
                ).first()
                if exists_pon:
                    exists_pon.state=output['state']
                    exists_pon.status=output['status']
                    exists_pon.description=output['description']
                    db.session.commit()
                else:
                    new_pon = OltDevicesCardPonModels(
                        self.id,
                        output['pon'],
                        output['state'],
                        output['status'],
                        output['description']
                    )
                    db.session.add(new_pon)
                    db.session.commit()
        elif self.type_port == 2:
            for num_port in range(int(self.jml_port)):
                output = oltdevice.oltdevice_showuplink(self.frame, self.slot, num_port)
                exists_uplink = OltDevicesCardUplinkModels.query.filter_by(
                    id_card=self.id,
                    port=output['port']
                ).first()
                if exists_uplink:
                    exists_uplink.name=output['name']
                    exists_uplink.port_type=output['port_type']
                    exists_uplink.status=output['status']
                    exists_uplink.description=output['description']
                    db.session.commit()
                else:
                    new_pon = OltDevicesCardUplinkModels(
                        self.id,
                        output['port'],
                        output['name'],
                        output['status'],
                        output['port_type'],
                        output['description']
                    )
                    db.session.add(new_pon)
                    db.session.commit()
        

    #deletetan
    def delete_list_pon(self):
        list_card = OltDevicesCardPonModels.query.filter_by(id_card=self.id).all()
        for card in list_card:
            db.session.delete(card)
            db.session.commit()

class OltDevicesCardPonModels(db.Model):
    __tablename__ = 'oltdevicecardpons'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_card = db.Column(db.Integer, db.ForeignKey('oltdevicecards.id', ondelete='CASCADE'), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    state = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def __init__(self, id_card, port, state, status, description=None):
        self.id_card = id_card
        self.port = port
        self.state = state
        self.status = status
        self.description = description

    def to_dict(self):
        data = {
            'id':self.id,
            'id_card':self.id_card,
            'port':self.port,
            'state':self.state,
            'status':self.status,
            'description':self.description
        }
        data['avg_rx_onu'] = 0
        data['tx_power_olt'] = 0
        data['total_onu'] = 0
        data['total_onu_online'] = 0
        return data

class OltDevicesCardUplinkModels(db.Model):
    __tablename__ = 'oltdevicecarduplink'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_card = db.Column(db.Integer, db.ForeignKey('oltdevicecards.id', ondelete='CASCADE'), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    port_type = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)

    def __init__(self, id_card, port, name, status, port_type, description=None):
        self.id_card = id_card
        self.port = port
        self.name = name
        self.status = status
        self.port_type = port_type
        self.description = description

    def to_dict(self):
        data = {
            'id':self.id,
            'id_card': self.id_card,
            'name':self.name,
            'port':self.port,
            'status':self.status,
            'port_type':self.port_type,
            'description':self.description,
            'vlan_tag':''
        }
        return data