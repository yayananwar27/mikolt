from config import db, event

def init_db(app):
    with app.app_context():
        db.create_all()


class OltCommandaddDeviceVlanModel(db.Model):
    __tablename__ = 'oltcommandadddevicevlan'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_software = db.Column(db.Integer, db.ForeignKey('oltsoftware.id', ondelete='CASCADE'), nullable=False)
    script_python = db.Column(db.Text, nullable=False)

    def __init__(self, id_software, script_python):
        self.id_software = id_software
        self.script_python = script_python

    def to_dict(self):
        return {
            'id':self.id,
            'id_software':self.id_software,
            'script_python':self.script_python
        }
    
# Fungsi untuk memasukkan data awal
def insert_initial_data(*args, **kwargs):
    data_1 = OltCommandaddDeviceVlanModel(
        id_software=1, 
        script_python='''
def add_vlan_telnet_to_olt(host, username, password, port, data):
    import pexpect
    import re
    try:
        tn = pexpect.spawn(f'telnet {host} {port}')
        tn.expect('Username:', timeout=10)
        tn.sendline(username)
        tn.expect('Password:', timeout=10)
        tn.sendline(password)
        tn.expect('#', timeout=10)  # Asumsikan prompt akan berakhir dengan '#'
        tn.sendline('conf t')
        tn.expect('#', timeout=10)  # Asumsikan prompt akan berakhir dengan '#'
        tn.sendline('vlan {}'.format(data['vlan_id']))
        tn.expect('#', timeout=10)
        
        if data['vlan_name'] != None:
            tn.sendline('name {}'.format(data['vlan_name']))
            tn.expect('#', timeout=10)
        
        if data['vlan_desc'] != None:
            tn.sendline('description {}'.format(data['vlan_desc']))
            tn.expect('#', timeout=10)
        
        tn.sendline('exit')
        tn.expect('#', timeout=10)
        tn.sendline('exit')
        tn.expect('#', timeout=10)
        tn.sendline('write')
        tn.expect('#', timeout=10)
        tn.sendline('exit')
        
        return 'success'

    except pexpect.TIMEOUT:
        return "Error: Connection timed out."
    
    except pexpect.EOF:
        return "Error: Unexpected end of file encountered."
    
    except Exception as e:
        return str(e)
        
host = self.host  
username = self.telnet_user
password = self.telnet_pass
port = self.telnet_port
output = add_vlan_telnet_to_olt(host, username, password, port, data)
        '''
    )
    db.session.add(data_1)
    db.session.commit()

event.listen(OltCommandaddDeviceVlanModel.__table__, 'after_create', insert_initial_data)