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
    #oltonutcont_fk = db.relationship('OltOnuTcontModels', backref='oltonutcont', cascade="all, delete", passive_deletes=True, lazy=True)
    #oltonugemport_fk = db.relationship('OltOnuGemportModels', backref='oltonugemport', cascade="all, delete", passive_deletes=True, lazy=True)
    #oltonuserviceport_fk = db.relationship('OltOnuServicePortModels', backref='oltonuserviceport', cascade="all, delete", passive_deletes=True, lazy=True)
    #oltonuhistory_fk = db.relationship('OltOnuHistoryRawRunningModels', backref='oltonuhistoryrawrunning', cascade="all, delete", passive_deletes=True, lazy=True)
    oltonuservicevlans_fk = db.relationship('OltOnuServiceVlansModels', backref='oltonuservicevlans', cascade="all, delete", passive_deletes=True, lazy=True)
    

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
    
    # def info_to_dict(self):
    #     from ooltdevices.models import OltDevicesModels
    #     get_name_device = OltDevicesModels.query.filter_by(id=self.id_device).first()
    #     name_device = get_name_device.name
    #     id_site = get_name_device.id_site

    #     from ooltdevices.models import OltDevicesCardModels
    #     get_cardframeslot = OltDevicesCardModels.query.filter_by(id=self.id_card).first()

    #     from ooltdevices.models import OltDevicesCardPonModels
    #     get_cardponport = OltDevicesCardPonModels.query.filter_by(id=self.id_cardpon).first()

    #     gpon_onu = 'gpon-onu_{0}/{1}/{2}:{3}'.format(get_cardframeslot.frame, get_cardframeslot.slot, get_cardponport.port, self.id_cardpononu)
        
    #     from sites.models import SitesModel
    #     get_site = SitesModel.query.filter_by(site_id=id_site).first()

    #     list_tcont=[]
    #     list_gemport=[]
    #     list_service_port=[]

    #     _list_tcont = OltOnuTcontModels.query.filter_by(
    #         id_onu=self.id
    #     ).all()
    #     for tcont in _list_tcont:
    #         list_tcont.append(tcont.to_dict())


    #     _list_gemport = OltOnuGemportModels.query.filter_by(
    #         id_onu=self.id
    #     ).all()
    #     for gem in _list_gemport:
    #         list_gemport.append(gem.to_dict())

    #     _list_sp = OltOnuServicePortModels.query.filter_by(
    #         id_onu=self.id
    #     ).all()
    #     for sp in _list_sp:
    #         list_service_port.append(sp.to_dict())

    #     data = {
    #         'id':self.id,
    #         'id_device':self.id_device,
    #         'name_device':name_device,
    #         'id_card':self.id_card,
    #         'id_cardpon':self.id_cardpon,
    #         'id_cardpononu':self.id_cardpononu,
    #         'onu':gpon_onu,
    #         'sn':self.sn,
    #         'onu_type':self.onu_type,
    #         'site_id': id_site,
    #         'site_name':get_site.name,
    #         'name':self.name,
    #         'description':self.description,
    #         'list_tcont':list_tcont,
    #         'list_gemport':list_gemport,
    #         'list_service_port':list_service_port
    #     }
    #     return data

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
            'list_servicevlan':list_servicevlan
        }
        return data


# class OltOnuTcontModels(db.Model):
#     __tablename__ = 'oltonutcont'
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     id_onu = db.Column(db.Integer, db.ForeignKey('oltonuconfigured.id', ondelete='CASCADE'), nullable=False)
#     tcont_id = db.Column(db.Integer, nullable=False)
#     name = db.Column(db.String(255), nullable=False)
#     profile = db.Column(db.String(255), nullable=False)

#     def __init__(self, id_onu, tcont_id, name, profile):
#         self.id_onu = id_onu
#         self.tcont_id = tcont_id
#         self.name = name
#         self.profile = profile

#     def to_dict(self):
#         data = {
#             'id':self.id, 
#             'id_onu':self.id_onu,
#             'tcont_id':self.tcont_id,
#             'name':self.name,
#             'profile':self.profile
#         }
#         return data

# class OltOnuGemportModels(db.Model):
#     __tablename__ = 'oltonugemport'  
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     id_onu = db.Column(db.Integer, db.ForeignKey('oltonuconfigured.id', ondelete='CASCADE'), nullable=False)
#     gemport_id = db.Column(db.Integer, nullable=False)
#     name = db.Column(db.String(255), nullable=False)
#     tcont_id = db.Column(db.Integer, nullable=False)
#     upstream = db.Column(db.Integer, nullable=True)
#     downstream = db.Column(db.Integer, nullable=True)

#     def __init__(self, id_onu, gemport_id, name, tcont_id, upstream=None, downstream=None):
#         self.id_onu = id_onu
#         self.gemport_id = gemport_id
#         self.name = name
#         self.tcont_id = tcont_id
#         self.upstream = upstream
#         self.downstream = downstream

#     def to_dict(self):
#         data = {
#             'id':self.id,
#             'id_onu':self.id_onu,
#             'gemport_id':self.gemport_id,
#             'name':self.name,
#             'tcont_id':self.tcont_id,
#             'upstream':self.upstream,
#             'downstream':self.downstream
#         }
#         return data

# class OltOnuServicePortModels(db.Model):
#     __tablename__ = 'oltonuserviceport'
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     id_onu = db.Column(db.Integer, db.ForeignKey('oltonuconfigured.id', ondelete='CASCADE'), nullable=False)
#     service_id = db.Column(db.Integer, nullable=False)
#     vport = db.Column(db.Integer, nullable=False)
#     vlan = db.Column(db.Integer, nullable=False)
#     description = db.Column(db.String(255), nullable=True)

#     def __init__(self, id_onu, service_id, vport, vlan, desc=None):
#         self.id_onu = id_onu
#         self.service_id = service_id
#         self.vport = vport
#         self.vlan = vlan
#         self.description = desc

#     def to_dict(self):
#         data = {
#             'id':self.id,
#             'id_onu':self.id_onu,
#             'service_id':self.service_id,
#             'vport':self.vport,
#             'vlan':self.vlan,
#             'description':self.description
#         }
#         return data

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

# class OltOnuHistoryRawRunningModels(db.Model):
#     __tablename__ = 'oltonuhistoryrawrunning'
#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     id_onu = db.Column(db.Integer, db.ForeignKey('oltonuconfigured.id', ondelete='CASCADE'), nullable=False)
#     status = 
#     duration = 
#     distance = 
#     olt_rx = 
#     onu_rx = 
#     input_rate = 
#     output_rate =
#     mac_list = 
#     running_int_config_history = 
#     running_pon_config_history = 
#     running_uptime_history = 
#     running_power_history =
#     running_bw_history = 
#     running_mac_history = 
#     timestamp =