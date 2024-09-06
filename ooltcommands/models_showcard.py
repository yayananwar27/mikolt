from config import db, event

def init_db(app):
    with app.app_context():
        db.create_all()


class OltCommandsShowCardModel(db.Model):
    __tablename__ = 'oltcommandshowcard'
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
    uptime_software_1 = OltCommandsShowCardModel(
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
        lines = output.strip().split("\n")
        headers = lines[0].split()
        parsed_data = []
        
        for line in lines[2:]:
            fields = line.split()
            row = {}
            #row['Rack'] = fields[0]
            row['Shelf'] = fields[1]
            row['Slot'] = fields[2]
            row['CfgType'] = fields[3]
            #row['RealType'] = fields[4] if len(fields) > 4 else ""
            row['Port'] = fields[5] if len(fields) > 5 else ""
            #row['HardVer'] = fields[6] if len(fields) > 6 else ""
            row['SoftVer'] = fields[7] if len(fields) > 7 else ""
            row['Status'] = fields[8] if len(fields) > 8 else ""
            parsed_data.append(row)

        return parsed_data
    
    except pexpect.TIMEOUT:
        return {'Error': 'Connection timed out.'}
    
    except pexpect.EOF:
        return {'Error': 'Unexpected end of file encountered.'}
    
    except Exception as e:
        return str(e)
host = self.host  
username = self.telnet_user
password = self.telnet_pass
command = "show card"
port = self.telnet_port
output = telnet_to_olt(host, username, password, command, port)
        '''
    )
    db.session.add(uptime_software_1)
    db.session.commit()

# Menghubungkan event listener ke model OltCommandsUptimeModel
event.listen(OltCommandsShowCardModel.__table__, 'after_create', insert_initial_data)