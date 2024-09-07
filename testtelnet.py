import pexpect
import re
def telnet_to_olt(host, username, password, command, port):
    try:
        # Mulai koneksi Telnet
        tn = pexpect.spawn(f'telnet {host} {port}')
        
        # Tangkap dan cetak output awal sebelum prompt login
        tn.expect('Username:', timeout=10)
        #initial_output = tn.before.decode('ascii')
        #print("Initial Output:")
        #print(initial_output)
        
        # Kirim username
        tn.sendline(username)
        
        # Tunggu prompt Password dan kirim password
        tn.expect('Password:', timeout=10)
        tn.sendline(password)
        
        # Tunggu prompt dan kirim perintah
        tn.expect('#', timeout=10)  # Asumsikan prompt akan berakhir dengan '#'
        tn.sendline(command)
        
        # Tangkap output dari command
        tn.expect('#', timeout=10)
        output = tn.before.decode('ascii')
        
        # Akhiri sesi Telnet
        tn.sendline('exit')
        pattern = r"Started before:\s+(\d+ days, \d+ hours, \d+ minutes)"
        match = re.search(pattern, output.strip())

        if match:
            started_before = match.group(1)
        else:
            started_before = None

        return started_before
    
    except pexpect.TIMEOUT:
        return "Error: Connection timed out."
    
    except pexpect.EOF:
        return "Error: Unexpected end of file encountered."
    
    except Exception as e:
        return str(e)

# Konfigurasi
host = "103.247.22.229"  # Ganti dengan IP OLT ZTE Anda
username = "yayan"  # Ganti dengan username Anda
password = "Yayan@12345"  # Ganti dengan password Anda
command = "show system-group"
port = 234  # Port Telnet

# Eksekusi fungsi telnet
output = telnet_to_olt(host, username, password, command, port)
print("Command Output:")
print(output)


# (venv) root@WebMailSSO:/opt/be-webmail# pip install pexpect
# Collecting pexpect
#   Downloading pexpect-4.9.0-py2.py3-none-any.whl.metadata (2.5 kB)
# Collecting ptyprocess>=0.5 (from pexpect)
#   Downloading ptyprocess-0.7.0-py2.py3-none-any.whl.metadata (1.3 kB)
# Downloading pexpect-4.9.0-py2.py3-none-any.whl (63 kB)
# Downloading ptyprocess-0.7.0-py2.py3-none-any.whl (13 kB)
# Installing collected packages: ptyprocess, pexpect
# Successfully installed pexpect-4.9.0 ptyprocess-0.7.0
# (venv) root@WebMailSSO:/opt/be-webmail# nano testelnet.py
# (venv) root@WebMailSSO:/opt/be-webmail# python testelnet.py
# Initial Output:
# Trying 103.247.22.229...
# Connected to 103.247.22.229.
# Escape character is '^]'.
# ************************************************
# Welcome to Arenjaya ZXAN product C320 of ZTE Corporation
# ************************************************

# Last login time is 08.31.2024-11:00:54-Asia/Jakarta, 0 authentication failures h
# appened since that time.

# Command Output:
# show system-group
# System Description: C320 Version V2.1.0 Software, Copyright (c) by ZTE Corporati
# on Compiled
# System ObjectId: .1.3.6.1.4.1.3902.1082.1001.320.2.1
# Started before: 141 days, 15 hours, 25 minutes
# Contact with: noc@wifian.id
# System name:  OLT-C320-ARENJAYA
# Location: Bekasi, Indonesia
# System Info:  165  56d41deb
# This system primarily offers a set of 78 services
# OLT-C320-ARENJAYA
# (venv) root@WebMailSSO:/opt/be-webmail# nano testelnet.py

def telnet_to_olt(host, username, password, command, port):
    import pexpect
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
        headers = lines[1].split()
        parsed_data = []

        for line in lines[3:-1]:
            fields = line.split()
            # Isi elemen yang kosong dengan string kosong
            while len(fields) < 9:
                if len(fields) < 7:
                    fields.insert(-2, "")    
                fields.insert(-1, "")

            print(fields)
            row = {
                'Rack': fields[0],
                'Frame': fields[1],
                'Slot': fields[2],
                'CfgType': fields[3],
                'RealType': fields[4],
                'Port': fields[5],
                'HardVer': fields[6],
                'SoftVer': fields[7],
                'Status': fields[8]
            }
            parsed_data.append(row)

        return parsed_data

    except pexpect.TIMEOUT:
        return {'Error': 'Connection timed out.'}

    except pexpect.EOF:
        return {'Error': 'Unexpected end of file encountered.'}

    except Exception as e:
        return str(e)

# Konfigurasi
host = "103.247.22.229"  # Ganti dengan IP OLT ZTE Anda
username = "yayan"  # Ganti dengan username Anda
password = "Yayan@12345"  # Ganti dengan password Anda
command = "show card"
port = 234  # Port Telnet

# Eksekusi fungsi telnet
output = telnet_to_olt(host, username, password, command, port)
print("Command Output:")
print(output)
