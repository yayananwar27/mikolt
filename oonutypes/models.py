from config import db

def init_db(app):
    with app.app_context():
        db.create_all()


class OnuTypesModel(db.Model):
    __tablename__ = 'onutypes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)
    pon_type = db.Column(db.String(255), nullable=False)
    max_tcont = db.Column(db.Integer, nullable=False)
    max_gemport = db.Column(db.Integer, nullable=False)
    max_switch = db.Column(db.Integer, nullable=False)
    max_flow = db.Column(db.Integer, nullable=False)
    max_iphost = db.Column(db.Integer, nullable=False)
    max_pots = db.Column(db.Integer, nullable=False)
    max_eth = db.Column(db.Integer, nullable=False)
    max_wifi = db.Column(db.Integer, nullable=False)

    def __init__(
            self, 
            name, 
            pon_type, 
            description=None, 
            max_tcont=40, 
            max_gemport=200,
            max_switch=32,
            max_flow=200,
            max_iphost=5,
            max_pots=0,
            max_eth=1,
            max_wifi=0
            ):
        self.name = name
        self.pon_type = pon_type
        self.description = description
        self.max_tcont = max_tcont
        self.max_gemport = max_gemport
        self.max_switch = max_switch
        self.max_flow = max_flow
        self.max_iphost = max_iphost
        self.max_pots = max_pots
        self.max_eth = max_eth
        self.max_wifi = max_wifi

    def to_dict(self):
        # if self.pon_type == 'epon':
        #     return {
        #         'id':self.id,
        #         'name':self.name,
        #         'pon_type':self.pon_type,
        #         'description':self.description,
        #         'max_pots':self.max_pots,
        #         'max_eth':self.max_eth,
        #         'max_wifi':self.max_wifi
        #     }
        return {
            'id':self.id,
            'name':self.name,
            'pon_type':self.pon_type,
            'description':self.description,
            'max_tcont':self.max_tcont,
            'max_gemport':self.max_gemport,
            'max_switch':self.max_switch,
            'max_flow':self.max_flow,
            'max_iphost':self.max_iphost,
            'max_pots':self.max_pots,
            'max_eth':self.max_eth,
            'max_wifi':self.max_wifi
        }