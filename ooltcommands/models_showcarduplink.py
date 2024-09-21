from config import db, event

def init_db(app):
    with app.app_context():
        db.create_all()


class OltCommandsUplinkInfoModel(db.Model):
    __tablename__ = 'oltcommandshowuplink'
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
    uptime_software_1 = OltCommandsUplinkInfoModel(
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
        output = ""
        while True:
            i = tn.expect(["--More--", "#"], timeout=300)
            output += tn.before.decode('ascii')
            if i == 0:  
                
                tn.sendline(" ") 
            elif i == 1:
                break
        
        tn.sendline('exit')
        pattern = r"line protocol is (\S+),"
        pattern2 = r"The port is (\S+)"
        pattern3 = r"Description is (\S+)"
        
        match = re.search(pattern, output.strip())
        match2 = re.search(pattern2, output.strip())
        match3 = re.search(pattern3, output.strip())
        data = {
            'status':'',
            'port_type' : '',
            'description':''
        }

        if match:
            data['status'] = match.group(1)
            data['port_type'] = match2.group(1)
            data['description'] = match3.group(1)
        
        return data
    
    except pexpect.TIMEOUT:
        return "Error: Connection timed out."
    
    except pexpect.EOF:
        return "Error: Unexpected end of file encountered."
    
    except Exception as e:
        return str(e)
pon = pon+1        
host = self.host
name = "gei_{0}/{1}/{2}".format(frame,slot,pon)
username = self.telnet_user
password = self.telnet_pass
command = "show interface {0}".format(name)
port = self.telnet_port
output = telnet_to_olt(host, username, password, command, port)
output['port']=pon
output['name']=name
        '''
    )
    db.session.add(uptime_software_1)
    db.session.commit()

# Menghubungkan event listener ke model OltCommandsUptimeModel
event.listen(OltCommandsUplinkInfoModel.__table__, 'after_create', insert_initial_data)