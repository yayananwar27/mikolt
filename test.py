def telnet_to_olt(host, username, password, port_telnet, command_tcont):
    import pexpect
    try:
        def replace_last_line(text, new_line):
            lines = text.splitlines()
            if lines:
                lines[-1] = new_line
            else:
                lines.append(new_line)
            return "\n".join(lines)
        
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
        output = replace_last_line(output, '\n')
        output += '\n\n'
        return output
    except pexpect.TIMEOUT:
        return "Error: Connection timed out."
    
    except pexpect.EOF:
        return "Error: Unexpected end of file encountered."
    
    except Exception as e:
        return str(e)

# Configuration
host = '103.247.21.15'  # Replace with your OLT IP
username = 'yayan'  # Replace with your username
password = 'Yayan@12345' # Replace with your password
port_telnet = 234  # Telnet port
command_tcont = f'show gpon profile tcont'

raw_data = telnet_to_olt(host, username, password, port_telnet, command_tcont)

# Parsing the data
def parse_tcont_data(raw_data):
    result = [line.split(":")[1].strip() for line in raw_data.splitlines() if line.startswith("Profile name ")]
    return result

# Call the function
output = parse_tcont_data(raw_data)
print(output)