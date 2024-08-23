from config import db
import uuid
from datetime import datetime

def init_db(app):
    with app.app_context():
        db.create_all()

def created_time():
    dt_now = datetime.now()
    date = dt_now.strftime("%Y-%m-%d %H:%M:%S")
    return str(date)

def created_uuid():
    return str(uuid.uuid1)

class MikoltLoggingModel(db.Model):
    __tablename__ = 'mikoltlogging'
    id = db.Column(db.String(255), primary_key=True, unique=True)
    timestamp = db.Column(db.DateTime, nullable=False)
    operator = db.Column(db.String(255), nullabel=False)
    name_modul = db.Column(db.String(255), nullabel=False)
    refrence_id = db.Column(db.String(255), nullabel=False)
    action = db.Column(db.String(255), nullabel=False)
    data = db.Column(db.Text, nullabel=True)

    def __init__(self, operator, name_modul, refrence_id, action, data=None):
        self.id = created_uuid()
        self.timestamp = created_time()
        self.operator = operator
        self.name_modul = name_modul
        self.refrence_id = refrence_id
        self.action = action
        self.data = data

    def to_dict(self):
        return {
            'id':self.id,
            'timestamp':str(self.timestamp),
            'operator':self.operator,
            'name_modul':self.name_modul,
            'refrence_id':self.refrence_id,
            'action':self.action,
            'data':self.data
        }
    