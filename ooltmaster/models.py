from config import db, event

def init_db(app):
    with app.app_context():
        db.create_all()


class OltMerkModels(db.Model):
    __tablename__ = 'oltmerk'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    merk = db.Column(db.String(255), unique=False, nullable=False)
    model = db.Column(db.String(255), unique=False, nullable=False)
    oltmerksoft_fk = db.relationship('OltMerkSoftModels', backref='oltmerk', cascade="all, delete", passive_deletes=True, lazy=True)
    oltmerkdata_fk = db.relationship('OltDevicesModels', backref='oltsoftware', cascade="all, delete", passive_deletes=True, lazy=True)

    def __init__(self, merk, model):
        self.merk = merk
        self.model = model

    def to_dict(self):
        return {
            'id':self.id,
            'merk':self.merk,
            'model':self.model
        }
    
    def soft_avai(self):
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
    oltsoftmerk_fk = db.relationship('OltMerkSoftModels', backref='oltsoftware', cascade="all, delete", passive_deletes=True, lazy=True)
    oltsoftdevice_fk = db.relationship('OltDevicesModels', backref='oltsoftware_device', cascade="all, delete", passive_deletes=True, lazy=True)
    oltsoftdeviceuptime_fk = db.relationship('OltCommandsUptimeModel', backref='oltsoftware_device_uptime', cascade="all, delete", passive_deletes=True, lazy=True)

    def __init__(self, name):
        self.name = name

    def to_dict(self):
        return {
            'id':self.id,
            'name':self.name
        }
    
    def merk_avai(self):
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


def insert_initial_software(*args, **kwargs):
    software_1 = OltSoftModels('V2.1.x')
    db.session.add(software_1)
    db.session.commit()

event.listen(OltSoftModels.__table__, 'after_create', insert_initial_software)