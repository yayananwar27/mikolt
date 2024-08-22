from config import db

def init_db(app):
    with app.app_context():
        db.create_all()


class SitesModel(db.Model):
    __tablename__ = 'sites'
    site_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    code = db.Column(db.String(255), nullable=True)
    #mikrotik_fk = db.relationship('mmikrotik', backref='sites', cascade="all, delete", passive_deletes=True, lazy=True)

    def __init__(self, name, id=None, code=None):
        if id != None:
            self.site_id = id
        self.name = name
        self.code = code

    def to_dict(self):
        return {
            'id':self.site_id,
            'name':self.name,
            'code':self.code
        }