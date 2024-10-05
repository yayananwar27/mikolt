def add_vlan_telnet_to_olt(host, username, password, port, interface, vlan):
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
        tn.sendline('interface {}'.format(interface))
        tn.expect('#', timeout=10)
        tn.sendline('switchport vlan {} tag'.format(vlan))
        tn.expect('#', timeout=10)
        tn.sendline('exit')
        tn.expect('#', timeout=10)
        tn.sendline('exit')
        tn.expect('#', timeout=10)
        #tn.sendline('wr')
        #tn.expect('#', timeout=10)
        tn.sendline('exit')
        
        return 'success'
    
    except pexpect.TIMEOUT:
        return "Error: Connection timed out."
    
    except pexpect.EOF:
        return "Error: Unexpected end of file encountered."
    
    except Exception as e:
        return str(e)
    
def delete_vlan_telnet_to_olt(host, username, password, port, interface, vlan):
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
        tn.sendline('interface {}'.format(interface))
        tn.expect('#', timeout=10)
        tn.sendline('no switchport vlan {}'.format(vlan))
        tn.expect('#', timeout=10)
        tn.sendline('exit')
        tn.expect('#', timeout=10)
        tn.sendline('exit')
        tn.expect('#', timeout=10)
        #tn.sendline('wr')
        #tn.expect('#', timeout=10)
        tn.sendline('exit')
        
        return 'success'
    
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
port = 234  # Port Telnet
interface = 'gei_1/3/1'
vlan = 21
output = add_vlan_telnet_to_olt(host, username, password, port, interface, vlan)
print(output)