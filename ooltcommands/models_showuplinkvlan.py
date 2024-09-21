from config import db, event

def init_db(app):
    with app.app_context():
        db.create_all()


class OltCommandShowVlanTagModel(db.Model):
    __tablename__ = 'oltcommandshowvlantag'
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
    uptime_software_1 = OltCommandShowVlanTagModel(
        id_software=1, 
        script_python='''
def telnet_to_olt(host, username, password, command, port):
    import pexpect
    import re
    try:
        tn = pexpect.spawn(f'telnet {host} {port}')
        tn.expect('Username:', timeout=10)
        tn.sendline(username)
        tn.expect('Password:', timeout=10)
        tn.sendline(password)
        tn.expect('#', timeout=10)  # Asumsikan prompt akan berakhir dengan '#'
        tn.sendline(command)
        tn.expect('#', timeout=10)
        output = tn.before.decode('ascii')
        tn.sendline('exit')
        
        vlan_pattern = r"switchport vlan ([\d,-]+) tag"
        vlans = re.findall(vlan_pattern, config_output)

        vlan_list = ",".join(vlans)

        return vlan_list
    
    except pexpect.TIMEOUT:
        return "Error: Connection timed out."
    
    except pexpect.EOF:
        return "Error: Unexpected end of file encountered."
    
    except Exception as e:
        return str(e)
host = self.host  
username = self.telnet_user
password = self.telnet_pass
command = "show run inter {}".format(name)
port = self.telnet_port
output = telnet_to_olt(host, username, password, command, port)
        '''
    )
    db.session.add(uptime_software_1)
    db.session.commit()

event.listen(OltCommandShowVlanTagModel.__table__, 'after_create', insert_initial_data)