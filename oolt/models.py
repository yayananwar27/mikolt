from config import db

def init_db(app):
    with app.app_context():
        db.create_all()

class OltMerkModels(db.Model):
    __tablename__ = 'oltmerk'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    merk = db.Column(db.String(255), unique=False, nullable=False)
    model = db.Column(db.String(255), unique=False, nullable=False)
    oltmerksoft_fk = db.relationship('oltmerksoft', backref='oltmerk', cascade="all, delete", passive_deletes=True, lazy=True)
    oltmerkdata_fk = db.relationship('oltdata', backref='oltsoftware', cascade="all, delete", passive_deletes=True, lazy=True)

    def __init__(self, merk, model):
        self.merk = merk
        self.model = model

    def to_dict(self):
        return {
            'id':self.id,
            'merk':self.merk,
            'model':self.model
        }
    
    def soft_aval(self):
        data = []
        list_soft = OltMerkSoftModels.query.filter_by(id_merk=self.id).all()
        
        for list in list_soft:
            software = OltSoftModels.query.filter_by(id=list.id_software).first()
            data.append(software.to_dict())

        return data


class OltSoftModels(db.Model):
    __tablename__ = 'oltsoftware'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    oltsoftmerk_fk = db.relationship('oltmerksoft', backref='oltsoftware', cascade="all, delete", passive_deletes=True, lazy=True)
    oltsoftdata_fk = db.relationship('oltdata', backref='oltsoftware', cascade="all, delete", passive_deletes=True, lazy=True)
    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return {
            'id':self.id,
            'name':self.name
        }
    
    def merk_aval(self):
        data = []
        list_soft = OltMerkSoftModels.query.filter_by(id_software=self.id).all()
        
        for list in list_soft:
            merk = OltMerkModels.query.filter_by(id=list.id_merk).first()
            data.append(merk.to_dict())

        return data
    
class OltMerkSoftModels(db.Model):
    __tablename__ = 'oltmerksoft'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_merk = db.Column(db.Integer, db.ForeignKey('oltmerk.id', ondelete='CASCADE'), nullable=False)
    id_software = db.Column(db.Integer, db.ForeignKey('oltsoftware.id', ondelete='CASCADE'), nullable=False)
    def __init__(self, id_merk, id_software):
        self.id_merk = id_merk
        self.id_software = id_software
        
    def to_dict(self):
        return {
            'id':self.id,
            'id_merk':self.id_merk,
            'id_software':self.id_software
        }

class OltDataModels(db.Model):
    __tablename__ = 'oltdata'
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
            'id_software':self.id_software
        }
        