from config import db, event

def init_db(app):
    with app.app_context():
        db.create_all()


class OltCommandShowVlanModel(db.Model):
    __tablename__ = 'oltcommandshowvlan'
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
    showvlan_software_1 = OltCommandShowVlanModel(
        id_software=1, 
        script_python='''
def list_vlan(host, username, password, port):
    import pexpect
    import re
    try:
        def parse_vlans(vlan_data):
            vlan_section = re.search(r'Details are following:\s+(.+)', vlan_data)
            
            if vlan_section:
                vlan_string = vlan_section.group(1)
                vlan_pattern = re.findall(r'(\d+-\d+|\d+)', vlan_string)    
                vlan_list = []
                for vlan in vlan_pattern:
                    if '-' in vlan:  # Jika rentang VLAN (misal 99-100)
                        start, end = map(int, vlan.split('-'))
                        vlan_list.extend(range(start, end + 1))  # Ekspansi rentang menjadi daftar
                    else:
                        vlan_list.append(int(vlan))  # VLAN tunggal
                        
                return vlan_list
            else:
                return []
            
        def show_vlan(host, username, password, port, vlan):
            tn2 = pexpect.spawn(f'telnet {host} {port}')
            tn2.expect('Username:', timeout=10)
            tn2.sendline(username)
            tn2.expect('Password:', timeout=10)
            tn2.sendline(password)
            tn2.expect('#', timeout=10)
            output = ''
            tn2.sendline('show vlan {}'.format(vlan))
            while True:
                i = tn2.expect(["--More--", "#"], timeout=300)
                output += tn2.before.decode('ascii')
                if i == 0:  
                    tn2.sendline(" ") 
                elif i == 1:
                    break

            tn2.sendline('exit')
            return output

        tn = pexpect.spawn(f'telnet {host} {port}')
        tn.expect('Username:', timeout=10)
        tn.sendline(username)
        tn.expect('Password:', timeout=10)
        tn.sendline(password)
        tn.expect('#', timeout=10)
        tn.sendline('show vlan summary')
        tn.expect("#", timeout=10)
        output = tn.before.decode('ascii')

        #onu profile
        tn.sendline('show gpon onu profile vlan')
        tn.expect("#", timeout=10)
        output2 = tn.before.decode('ascii')

        profile_list = []
        current_profile = {}

        for line in output2.splitlines():
            if line.startswith("Profile name:"):
                if current_profile:
                    profile_list.append(current_profile)
                current_profile = {}
                current_profile['profile_name'] = line.split(":")[1].strip()
            elif line.startswith("CVLAN:"):
                current_profile['cvlan'] = line.split(":")[1].strip()

        if current_profile:
            profile_list.append(current_profile)
        
        #igmp
        igmp_vlan = []
        tn.sendline('show igmp mvlan')
        tn.expect("#", timeout=10)
        output3 = tn.before.decode('ascii')
        lines = [line.strip() for line in output3.split('\\n') if line.strip()]
        headers = lines[2].split()
        rows = lines[4:-1]
        for row in rows:
            values = row.split(maxsplit=len(headers)-1)
            entry = dict(zip(headers, values))
            igmp_vlan.append(entry)

        _list_vlan = parse_vlans(output)
        data = []
        
        for vlan in _list_vlan:
            output = ''
            _vlan = {
                'vlan_id':vlan,
                'name':'',
                'description':'',
                'onu_profile':'',
                'multicast_igmp':False
                }

            output = show_vlan(host, username, password, port, vlan)
            try:
                _vlan['name'] = re.search(r'name\s*:\s*(\S+)', output).group(1)
                _vlan['description'] = re.search(r'description\s*:\s*(.+)', output).group(1).replace('\\r', '').strip()
            except:
                pass

            cvlan_data = [profile for profile in profile_list if profile['cvlan'] == str(vlan)]
            if len(cvlan_data)>0:
                _vlan['onu_profile']=cvlan_data[0]['profile_name']

            igmp_data = [igmp for igmp in igmp_vlan if igmp['VID'] == str(vlan)]
            if len(igmp_data)>0:
                if igmp_data[0]['Status']=='enable':
                    _vlan['multicast_igmp']=True

            data.append(_vlan)
        tn.sendline('exit')

        return data
    
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
output = list_vlan(host, username, password, port)
        '''
    )
    db.session.add(showvlan_software_1)
    db.session.commit()

event.listen(OltCommandShowVlanModel.__table__, 'after_create', insert_initial_data)