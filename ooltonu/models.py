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