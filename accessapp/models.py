from config import db
from .tokenapp import get_datetime
def init_db(app):
    with app.app_context():
        db.create_all()


class ApiTokenAccessModel(db.Model):
    __tablename__ = "apitokenaccess"
    token = db.Column(db.String(255), primary_key=True, unique=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    role = db.Column(db.String(25), nullable=False)
    expired = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, token,username, role, expired=None):
        self.token = token
        self.username = username
        self.role = role
        self.expired = expired
        self.created_at = str(get_datetime())

    def __str__(self):
        return self.username
    
    def __repr__(self):
        return self.username

    def to_dict(self):
        exp = get_datetime()
        expired_date = None
        if self.expired != None:
            expired_date = exp.unix_to_datetime(self.expired)

        return {
            'token':self.token,
            'username':self.username,
            'role':self.role,
            'expired':self.expired,
            'expired_date':expired_date
        }

class ApiTokenRefreshModel(db.Model):
    __tablename__ = "apitokenrefresh"
    token = db.Column(db.String(255), primary_key=True, unique=True)
    username = db.Column(db.String(50), nullable=False)
    expired = db.Column(db.Integer, nullable=False)
    ipaddress = db.Column(db.String(255), nullable=False)
    device = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, token, username, device, ipaddress, expired=None):
        self.token = token
        self.username = username
        self.expired = expired
        self.ipaddress = ipaddress
        self.device = device
        self.created_at = str(get_datetime())
    
    def to_dict(self):
        exp = get_datetime()
        expired_date = None
        if self.expired != None:
          expired_date = exp.unix_to_datetime(self.expired)
          
        return {
            'token':self.token,
            'username':self.username,
            'ipaddress':self.ipaddress,
            'device':self.device,
            'expired':self.expired,
            'expired_date':expired_date
        }