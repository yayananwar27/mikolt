def telnet_to_olt(host, username, password, command, port):
    import pexpect
    import re
    try:
        tn = pexpect.spawn(f'telnet {host} {port}')
        tn.expect('Username:', timeout=10)
        tn.sendline(username)
        tn.expect('Password:', timeout=10)
        tn.sendline(password)
        print('masukkin password')
        tn.expect('#', timeout=10)  # Asumsikan prompt akan berakhir dengan '#'
        print('masukkin command')
        print(command)
        tn.sendline(command)
        output = ""
        while True:
            print(output)
            i = tn.expect(["--More--", "#"], timeout=300)
            output += tn.before.decode('ascii')
            if i == 0:  
                
                tn.sendline(" ") 
            elif i == 1:
                break
        

        tn.sendline('exit')
        pattern = r"is (\S+),line protocol is (\S+)"
        pattern2 = r"Description is (\S+)"
        
        match = re.search(pattern, output.strip())
        match2 = re.search(pattern2, output.strip())
        data = {
            'state' : '',
            'status':'',
            'description':''
        }

        if match:
            data['state'] = match.group(1)
            data['status'] = match.group(2)
            data['description'] = match2.group(1)
        
        return data
    
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
command = "show interface gpon-olt_1/1/1"
port = 234  # Port Telnet
output = telnet_to_olt(host, username, password, command, port)
print(output)