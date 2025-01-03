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

class OltOnuConfiguredModels(db.Model):
    __tablename__ = 'oltonuconfigured'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_device = db.Column(db.Integer, db.ForeignKey('oltdevices.id', ondelete='CASCADE'), nullable=False)
    id_card = db.Column(db.Integer, db.ForeignKey('oltdevicecards.id', ondelete='CASCADE'), nullable=False)
    id_cardpon = db.Column(db.Integer, db.ForeignKey('oltdevicecardpons.id', ondelete='CASCADE'), nullable=False)
    id_cardpononu = db.Column(db.Integer, nullable=False)
    sn = db.Column(db.String(255), nullable=False)
    onu_type = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    oltonuservicevlans_fk = db.relationship('OltOnuServiceVlansModels', backref='oltonuservicevlans', cascade="all, delete", passive_deletes=True, lazy='dynamic')
    oltonuhistory_fk = db.relationship('OltOnuStatusHistoryModels', backref='oltonuhistory', cascade="all, delete", passive_deletes=True, lazy='dynamic')
    oltonuhistory_fk = db.relationship('OltOnuStatusHistoryModels', backref='oltonuhistory', cascade="all, delete", passive_deletes=True, lazy='dynamic')


    def __init__(self, id_device, id_card, id_cardpon, id_cardpononu, sn, onu_type, name, description=None):
        self.id_device = id_device
        self.id_card = id_card
        self.id_cardpon = id_cardpon
        self.id_cardpononu = id_cardpononu
        self.sn = sn
        self.onu_type = onu_type
        self.name = name
        self.description = description

    def to_dict(self):
        from ooltdevices.models import OltDevicesModels
        get_name_device = OltDevicesModels.query.filter_by(id=self.id_device).first()
        name_device = get_name_device.name
        id_site = get_name_device.id_site

        from ooltdevices.models import OltDevicesCardModels
        get_cardframeslot = OltDevicesCardModels.query.filter_by(id=self.id_card).first()

        from ooltdevices.models import OltDevicesCardPonModels
        get_cardponport = OltDevicesCardPonModels.query.filter_by(id=self.id_cardpon).first()

        gpon_onu = 'gpon-onu_{0}/{1}/{2}:{3}'.format(get_cardframeslot.frame, get_cardframeslot.slot, get_cardponport.port, self.id_cardpononu)
        
        from sites.models import SitesModel
        get_site = SitesModel.query.filter_by(site_id=id_site).first()

        data = {
            'id':self.id,
            'id_device':self.id_device,
            'name_device':name_device,
            'id_card':self.id_card,
            'id_cardpon':self.id_cardpon,
            'id_cardpononu':self.id_cardpononu,
            'onu':gpon_onu,
            'sn':self.sn,
            'onu_type':self.onu_type,
            'site_id': id_site,
            'site_name':get_site.name,
            'name':self.name,
            'description':self.description
        }
        return data
    
    def info_to_dict(self):
        from ooltdevices.models import OltDevicesModels
        get_name_device = OltDevicesModels.query.filter_by(id=self.id_device).first()
        name_device = get_name_device.name
        id_site = get_name_device.id_site

        from ooltdevices.models import OltDevicesCardModels
        get_cardframeslot = OltDevicesCardModels.query.filter_by(id=self.id_card).first()

        from ooltdevices.models import OltDevicesCardPonModels
        get_cardponport = OltDevicesCardPonModels.query.filter_by(id=self.id_cardpon).first()

        gpon_onu = 'gpon-onu_{0}/{1}/{2}:{3}'.format(get_cardframeslot.frame, get_cardframeslot.slot, get_cardponport.port, self.id_cardpononu)
        
        from sites.models import SitesModel
        get_site = SitesModel.query.filter_by(site_id=id_site).first()

        list_servicevlan=[]

        _list_spvlans = OltOnuServiceVlansModels.query.filter_by(
            id_onu=self.id
        ).all()
        for spv in _list_spvlans:
            list_servicevlan.append(spv.to_dict())


        data = {
            'id':self.id,
            'id_device':self.id_device,
            'name_device':name_device,
            'id_card':self.id_card,
            'id_cardpon':self.id_cardpon,
            'id_cardpononu':self.id_cardpononu,
            'onu':gpon_onu,
            'sn':self.sn,
            'onu_type':self.onu_type,
            'site_id': id_site,
            'site_name':get_site.name,
            'name':self.name,
            'description':self.description,
            'list_servicevlan':list_servicevlan,
        }

        #info status
        last_info = OltOnuStatusHistoryModels.query.filter_by(
            id_onu=self.id
        ).order_by(OltOnuStatusHistoryModels.timestamp.desc()).first()
        info_data = last_info.to_dict()
        data.update(info_data)
        return data

    def update_status(self):
        from ooltdevices.models import OltDevicesModels
        device = OltDevicesModels.query.filter_by(id=self.id_device).first()
        try:
            if device:
                device.Get_onu_status_history(onu_id=self.id)
                return True
            else:    
                return False
        except:
            return False

class OltOnuServiceVlansModels(db.Model):
    __tablename__ = 'oltonuservicevlans'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_onu = db.Column(db.Integer, db.ForeignKey('oltonuconfigured.id', ondelete='CASCADE'), nullable=False)
    service_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(255), nullable=True)
    profile_tcont = db.Column(db.String(255), nullable=False)
    traffic_upstream = db.Column(db.String(255), nullable=True)
    traffic_downstream = db.Column(db.String(255), nullable=True)
    vlan = db.Column(db.Integer, nullable=False)


    def __init__(self, id_onu, service_id, profile_tcont, vlan, name=None, traffic_upstream=None, traffic_downstream=None):
        self.id_onu = id_onu
        self.service_id = service_id
        self.name = name
        self.profile_tcont = profile_tcont
        self.vlan = vlan
        self.traffic_upstream = traffic_upstream
        self.traffic_downstream = traffic_downstream

    def to_dict(self):
        data = {
            'id':self.id,
            'id_onu':self.id_onu,
            'service_id':self.service_id,
            'name':self.name,
            'profile_tcont':self.profile_tcont,
            'vlan':self.vlan,
            'traffic_upstream':self.traffic_upstream,
            'traffic_downstream':self.traffic_downstream
        }
        return data

class OltOnuStatusHistoryModels(db.Model):
    __tablename__ = 'oltonustatushistory'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    id_onu = db.Column(db.Integer, db.ForeignKey('oltonuconfigured.id', ondelete='CASCADE'), nullable=False)
    olt_rx = db.Column(db.Float(5), nullable=True)
    onu_rx = db.Column(db.Float(5), nullable=True)
    onu_state = db.Column(db.String(50), nullable=True)
    onu_range = db.Column(db.String(50), nullable=True)
    onu_online = db.Column(db.String(50), nullable=True)
    onu_byte_input = db.Column(db.Integer, nullable=True)
    onu_byte_output = db.Column(db.Integer, nullable=True)
    onu_packet_input = db.Column(db.Integer, nullable=True)
    onu_packet_output = db.Column(db.Integer, nullable=True)
    onu_list_mac = db.Column(db.Text, nullable=True)
    show_status_raw = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False)

    def __init__(self, 
            id_onu, 
            olt_rx=None, 
            onu_rx=None, 
            onu_state=None, 
            onu_range=None,
            onu_online=None, 
            onu_byte_input=0, 
            onu_byte_output=0,
            onu_packet_input=0,
            onu_packet_output=0,
            onu_list_mac=None,
            show_status_raw=None
        ):
        self.id_onu = id_onu
        self.olt_rx = olt_rx
        self.onu_rx = onu_rx
        self.onu_state = onu_state
        self.onu_range = onu_range
        self.onu_online = onu_online
        self.onu_byte_input = onu_byte_input
        self.onu_byte_output = onu_byte_output
        self.onu_packet_input = onu_packet_input
        self.onu_packet_output = onu_packet_output
        self.onu_list_mac = onu_list_mac
        self.show_status_raw = show_status_raw
        self.timestamp = created_time()

    def to_dict(self):
        data = {
            #'id':self.id,
            'id_onu':self.id_onu, 
            'olt_rx':self.olt_rx, 
            'onu_rx':self.onu_rx, 
            'onu_state':self.onu_state, 
            'onu_range':self.onu_range,
            'onu_online':self.onu_online, 
            'onu_byte_input':self.onu_byte_input, 
            'onu_byte_output':self.onu_byte_output,
            'onu_packet_input':self.onu_packet_input,
            'onu_packet_output':self.onu_packet_output,
            'onu_list_mac':self.onu_list_mac,
            'timestamp':str(self.timestamp)
        }
        return data
    
    def out_raw(self):
        data = {
            'data':self.show_status_raw
        }
        return data

class OltOnuLoggingModels(db.Model):
    __tablename__ = 'oltonulogging'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    id_onu = db.Column(db.Integer, db.ForeignKey('oltonuconfigured.id', ondelete='CASCADE'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    user = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, nullable=False)

    def __init__(self, id_onu, user, action, description=None):
        self.id_onu = id_onu
        self.user = user
        self.action = action
        self.description = description
        self.timestamp = created_time()

    def to_dict(self):
        data = {
            'id':self.id,
            'id_onu':self.id_onu,
            'action':self.action,
            'user':self.user,
            'description':self.description,
            'timestamp':str(self.timestamp)
        }
        return data