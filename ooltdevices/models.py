from config import db

def init_db(app):
    with app.app_context():
        db.create_all()


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
            local_scope = {'self': self}
            exec(script_python.script_python, {}, local_scope)
            output = local_scope.get('output')   
        return output



class OltDevicesCardModels(db.Model):
    __tablename__ = 'oltdevicecards'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_device = db.Column(db.Integer, db.ForeignKey('oltdevices.id', ondelete='CASCADE'), nullable=False)
    shelf = db.Column(db.integer, nullable=False)
    slot = db.Column(db.integer, nullable=False)
    jml_port = db.Column(db.integer, nullable=False)
    soft_ver = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    type_port = db.Column(db.integer, nullable=False) #1=GPON CARD,  2=Uplink Card
    last_update = soft_ver = db.Column(db.DateTime, nullable=False)

    def __init__(self, id_device, shelf_number, slot_number, jml_port, soft_ver, status, type_port, last_update):
        self.id_device = id_device
        self.shelf = shelf_number
        self.slot = slot_number
        self.jml_port = jml_port
        self.soft_ver = soft_ver
        self.status = status
        self.type_port = type_port
        self.last_update = last_update

    def to_dict(self):
        return {
            'id':self.id,
            'id_device':self.id_device,
            'shelf':self.shelf,
            'slot':self.slot,
            'jml_port':self.jml_port,
            'soft_ver':self.soft_ver,
            'status':self.status,
            'type_port':self.type_port,
            'last_update':str(self.last_update)
        }
    
    