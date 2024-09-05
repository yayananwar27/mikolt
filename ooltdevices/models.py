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
    id_merk = db.Column(db.Integer, db.ForeignKey('oltmerk.id', ondelete='CASCADE'), nullable=False)
    id_software = db.Column(db.Integer, db.ForeignKey('oltsoftware.id', ondelete='CASCADE'), nullable=False)
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
        self.id_merk = id_merk
        self.id_software = id_software

    def to_dict(self):
        from ooltmaster.models import OltMerkModels, OltSoftModels
        info_merk = OltMerkModels.query.filter_by(id=self.id_merk).first()
        info_soft = OltSoftModels.query.filter_by(id=self.id_software).first()
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
            'id_merk':self.id_merk,
            'id_software':self.id_software,
            'info_merk':info_merk.to_dict(),
            'info_software':info_soft.to_dict()
        }
    
    def to_dict_info(self):
        from ooltmaster.models import OltMerkModels, OltSoftModels
        info_merk = OltMerkModels.query.filter_by(id=self.id_merk).first()
        info_soft = OltSoftModels.query.filter_by(id=self.id_software).first()
        
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
            'id_merk':self.id_merk,
            'id_software':self.id_software,
            'uptime':self.oltdevice_uptime(),
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
            exec(script_python.script_python)

        return output