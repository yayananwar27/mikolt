from config import db, event

def init_db(app):
    with app.app_context():
        db.create_all()


class OltCommandShowOltTcontModel(db.Model):
    __tablename__ = 'oltcommandshowolttcont'
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
    showolt_tcont_1 = OltCommandShowOltTcontModel(
        id_software=1, 
        script_python='''
def telnet_to_olt(host, username, password, port_telnet, command_tcont):
    import pexpect
    try:
        def replace_last_line(text, new_line):
            lines = text.splitlines()
            if lines:
                lines[-1] = new_line
            else:
                lines.append(new_line)
            return "\\n".join(lines)
        
        tn = pexpect.spawn(f'telnet {host} {port_telnet}')
        tn.setwinsize(1000, 1000)
        tn.expect('Username:', timeout=10)
        tn.sendline(username)
        tn.expect('Password:', timeout=10)
        tn.sendline(password)
        tn.expect('#', timeout=10)  # Assuming prompt ends with '#'
        output = ""
        tn.sendline(command_tcont)
        tn.expect('#', timeout=10)
        output += tn.before.decode('ascii')
        output = replace_last_line(output, '\\n')
        output += '\\n\\n'
        return output
    except pexpect.TIMEOUT:
        return "Error: Connection timed out."
    
    except pexpect.EOF:
        return "Error: Unexpected end of file encountered."
    
    except Exception as e:
        return str(e)

# Configuration
host = self.host  # Replace with your OLT IP
username = self.telnet_user  # Replace with your username
password = self.telnet_pass # Replace with your password
port_telnet = self.telnet_port  # Telnet port
command_tcont = f'show gpon profile tcont'

raw_data = telnet_to_olt(host, username, password, port_telnet, command_tcont)


# Parsing the data
def parse_tcont_data(raw_data):
    result = [line.split(":")[1].strip() for line in raw_data.splitlines() if line.startswith("Profile name ")]
    return result

# Call the function
output = parse_tcont_data(raw_data)
        '''
    )
    db.session.add(showolt_tcont_1)
    db.session.commit()

# Menghubungkan event listener ke model OltCommandsUptimeModel
event.listen(OltCommandShowOltTcontModel.__table__, 'after_create', insert_initial_data)