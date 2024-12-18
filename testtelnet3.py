import pexpect
import re

def telnet_to_olt(host, username, password, command, port):
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
                tn.sendline("\r")  # Skip the "--More--" prompt
            elif i == 1:
                break
        
        return output
    
    except pexpect.TIMEOUT:
        return "Error: Connection timed out."
    
    except pexpect.EOF:
        return "Error: Unexpected end of file encountered."
    
    except Exception as e:
        return str(e)


def parse_olt_output(output):
    # Pattern untuk menemukan id, type, dan SN
    pattern = r"onu (\d+) type (\S+) sn (\S+)"
    matches = re.findall(pattern, output)
    
    # Membuat list of dict
    onu_list = []
    for match in matches:
        onu_id, onu_type, onu_sn = match
        onu_list.append({
            'id': int(onu_id),
            'type': onu_type,
            'sn': onu_sn
        })
    
    return onu_list


# Konfigurasi
host = "103.247.21.15"  # Ganti dengan IP OLT ZTE Anda
username = "yayan"  # Ganti dengan username Anda
password = "Yayan@12345"  # Ganti dengan password Anda
frame=1
slot=1
port=1
command = "show running-config interface gpon-olt_{0}/{1}/{2}".format(frame, slot, port)
telnet_port = 234  # Port Telnet
# Menjalankan Telnet dan mengambil output
_output = telnet_to_olt(host, username, password, command, telnet_port)
# Parsing output menjadi list of dict
onu_list = parse_olt_output(_output)

def telnet_to_olt2(host, username, password, command, port):
    try:
        tn = pexpect.spawn(f'telnet {host} {port}')
        tn.expect('Username:', timeout=10)
        tn.sendline(username)
        tn.expect('Password:', timeout=10)
        tn.sendline(password)
        tn.expect('#', timeout=10)  # Assuming prompt ends with '#'
        tn.sendline(command)
        output = ""
        while True:
            i = tn.expect(["--More--", "#"], timeout=300)
            output += tn.before.decode('ascii')
            if i == 0:  
                tn.sendline("\r")  # Skip the "--More--" prompt
            elif i == 1:
                break
        
        tn.sendline("exit")
        return output
    
    except pexpect.TIMEOUT:
        return "Error: Connection timed out."
    
    except pexpect.EOF:
        return "Error: Unexpected end of file encountered."
    
    except Exception as e:
        return str(e)

def parse_olt_output2(output):
    parsed_data = {}
    
    # Extract interface name
    interface_match = re.search(r"interface (\S+)", output)
    if interface_match:
        parsed_data["interface"] = interface_match.group(1)

    # Extract name
    name_match = re.search(r"name ([^\n]+)", output)
    if name_match:
        parsed_data["name"] = name_match.group(1).strip()

    # Extract description
    description_match = re.search(r"description ([^\n]+)", output)
    if description_match:
        parsed_data["description"] = description_match.group(1).strip()
    
    # Extract TCONT
    parsed_data["tcont"] = []
    tcont_matches = re.findall(r"tcont (\d+) name ([^\n]+)", output)
    for tcont_id, tcont_name in tcont_matches:
        parsed_data["tcont"].append({"id": int(tcont_id), "name": tcont_name.strip()})
    
    # Extract GEMPORT
    parsed_data["gemport"] = []
    gemport_matches = re.findall(r"gemport (\d+) name ([^\s]+) tcont (\d+)", output)
    for gemport_id, gemport_name, tcont_id in gemport_matches:
        parsed_data["gemport"].append({
            "id": int(gemport_id),
            "name": gemport_name.strip(),
            "tcont_id": int(tcont_id)
        })
    
    # Extract Service-Port
    parsed_data["service_port"] = []
    service_port_matches = re.findall(
        r"service-port (\d+) vport (\d+) user-vlan (\d+) vlan (\d+)", output
    )
    for port_id, vport, user_vlan, vlan in service_port_matches:
        parsed_data["service_port"].append({
            "id": int(port_id),
            "vport": int(vport),
            "user_vlan": int(user_vlan),
            "vlan": int(vlan)
        })
    
    return parsed_data

output = []
for onu in onu_list:
    #print(onu)
    command2 = "show running-config interface gpon-onu_{0}/{1}/{2}:{3}".format(frame, slot, port, onu['id'])
    _output = telnet_to_olt2(host, username, password, command2, telnet_port)
    output2 = parse_olt_output2(_output)
    _data = {
        'onu_id':onu['id'],
        'sn':onu['sn'],
        'onu_type':onu['type'],
        'name':output2['name'],
        'description':output2['description'],
        'raw_runningonu':_output
    }
    output.append(_data)
