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
command = "show running-config interface gpon-olt_1/1/1"
port = 234  # Port Telnet

# Menjalankan Telnet dan mengambil output
output = telnet_to_olt(host, username, password, command, port)
print(output)

# Parsing output menjadi list of dict
onu_list = parse_olt_output(output)

# Menampilkan hasil
for onu in onu_list:
    print(onu)
