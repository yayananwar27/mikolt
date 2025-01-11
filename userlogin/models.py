from config import db, event

def init_db(app):
    with app.app_context():
        db.create_all()

from sites.models import SitesModel

class UserLoginModel(db.Model):
    __tablename__ = "userlogin"
    username = db.Column(db.String(50), primary_key=True, unique=True)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(25), nullable=False)

    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        if role in ['superadmin', 'teknisi', 'admin', 'noc']:
            self.role = role
        else:
            self.role = None            

    def to_dict(self):
        return {
            'username':self.username,
            'password':self.password,
            'role':self.role
        }
    
class AllowedSiteUserModel(db.Model):
    __tablename__ = "usersite"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), nullable=False)
    site_id = db.Column(db.Integer, nullable=False)

    def __init__(self, username, site_id):
        self.username = username
        self.site_id = site_id
    
    def to_dict(self):
        return {
            'id':self.id,
            'username':self.username,
            'site_id':self.site_id
        }
    
    def to_dict_info(self):
        site_info = SitesModel.query.filter_by(site_id=self.site_id).first()

        return {
            'id':self.id,
            'username':self.username,
            'site_id':self.site_id,
            'site_info':site_info.to_dict()
        }
    
def insert_initial_data(*args, **kwargs):
    from werkzeug.security import generate_password_hash
    encrypt_pass = generate_password_hash('nocjuga')
    data_superadmin = UserLoginModel('noc', encrypt_pass, 'superadmin')
    db.session.add(data_superadmin)
    db.session.commit()

event.listen(UserLoginModel.__table__, 'after_create', insert_initial_data)