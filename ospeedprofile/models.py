from config import db

def init_db(app):
    with app.app_context():
        db.create_all()


class TcontSpeedProfileModel(db.Model):
    __tablename__ = 'tcontspeedprofile'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    type = db.Column(db.Integer, nullable=False)
    fixed = db.Column(db.Integer, nullable=False)
    assured = db.Column(db.Integer, nullable=False)
    maximum = db.Column(db.Integer, nullable=False)

    def __init__(self, name, type, fixed=0, assured=0, maximum=0):
        self.name = name
        self.type = type
        self.fixed = fixed
        self.assured = assured
        self.maximum = maximum

    def to_dict(self):
        return {
            'id':self.id,
            'name':self.name,
            'type':self.type,
            'fixed':self.fixed,
            'assured':self.assured,
            'maximum':self.maximum
        }

class TrafficSpeedProfileModel(db.Model):
    __tablename__ = 'trafficspeedprofile'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    sir = db.Column(db.Integer, nullable=False)
    pir = db.Column(db.Integer, nullable=False)
    cbs = db.Column(db.Integer, nullable=False)
    pbs = db.Column(db.Integer, nullable=False)

    def __init__(self, name, sir=0, pir=0, cbs=0, pbs=0):
        self.name = name
        self.sir = sir
        self.pir = pir
        self.cbs = cbs
        self.pbs = pbs
        
    def to_dict(self):
        return {
            'id':self.id,
            'name':self.name,
            'sir':self.sir,
            'pir':self.pir,
            'cbs':self.cbs,
            'pbs':self.pbs
        }