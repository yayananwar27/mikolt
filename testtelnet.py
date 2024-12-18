def telnet_to_olt(host, username, password, port_telnet, command_power, command_info, command_stats, command_mac):
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
        tn.sendline(command_power)
        tn.expect('#', timeout=10)
        output += tn.before.decode('ascii')
        output = replace_last_line(output, '\n')
        output += '\n\n\n'

        tn.sendline(command_info)
        tn.expect('#', timeout=10)
        output += tn.before.decode('ascii')
        output = replace_last_line(output, '\n')
        output += '\n\n\n'

        tn.sendline(command_stats)
        tn.expect('#', timeout=10)
        output += tn.before.decode('ascii')
        output = replace_last_line(output, '\n')
        output += '\n\n\n'

        tn.sendline(command_mac)
        tn.expect('#', timeout=10)
        output += tn.before.decode('ascii')
        output = replace_last_line(output, '\n')
        output += '\n\n\n'

        tn.sendline("exit")

        return output
    
    except pexpect.TIMEOUT:
        return "Error: Connection timed out."
    
    except pexpect.EOF:
        return "Error: Unexpected end of file encountered."
    
    except Exception as e:
        return str(e)



# Configuration
host = "103.247.21.15"  # Replace with your OLT IP
username = "yayan"  # Replace with your username
password = "Yayan@12345"  # Replace with your password
port_telnet = 234  # Telnet port
onu = 'gpon-onu_1/1/1:1'
command_power = f'show pon power attenuation {onu}'
command_info = f'show gpon onu detail-info {onu}'
command_stats = f'show interface {onu}'
command_mac = f'show mac gpon onu {onu}'

# Telnet to OLT and parse output
raw_data = telnet_to_olt(host, username, password, port_telnet, command_power, command_info, command_stats,  command_mac)

def parse_data(raw_data):
    import re
    data = {}

    # Parse OLT RX
    olt_rx_match = re.search(r"up.+Rx :(-?\d+\.\d+)\(dbm\)", raw_data)
    data['olt_rx'] = float(olt_rx_match.group(1)) if olt_rx_match else None

    # Parse ONU RX
    onu_rx_match = re.search(r"down.*Rx:(-?\d+\.\d+)\(dbm\)", raw_data)
    data['onu_rx'] = float(onu_rx_match.group(1)) if onu_rx_match else None

    # Parse ONU State
    onu_state_match = re.search(r"Phase state:\s*(\w+)", raw_data)
    data['onu_state'] = onu_state_match.group(1) if onu_state_match else None

    # Parse ONU Range
    onu_range_match = re.search(r"ONU Distance:\s*(\w+)", raw_data)
    data['onu_range'] = onu_range_match.group(1) if onu_range_match else None

    # Parse ONU Online Duration
    onu_online_match = re.search(r"Online Duration:\s*(.+?)\n", raw_data)
    data['onu_online'] = onu_online_match.group(1) if onu_online_match else None

    # Parse ONU Bytes Input
    onu_byte_input_match = re.search(r"Input peak rate : +(\d+)", raw_data)
    data['onu_byte_input'] = int(onu_byte_input_match.group(1)) if onu_byte_input_match else None

    # Parse ONU Bytes Output
    onu_byte_output_match = re.search(r"Output peak rate: +(\d+)", raw_data)
    data['onu_byte_output'] = int(onu_byte_output_match.group(1)) if onu_byte_output_match else None

    # Parse ONU Packets Input
    onu_packet_input_match = re.search(r"Input peak rate : +\d+ Bps +(\d+) pps", raw_data)
    data['onu_packet_input'] = int(onu_packet_input_match.group(1)) if onu_packet_input_match else None

    # Parse ONU Packets Output
    onu_packet_output_match = re.search(r"Output peak rate: +\d+ Bps +(\d+) pps", raw_data)
    data['onu_packet_output'] = int(onu_packet_output_match.group(1)) if onu_packet_output_match else None

    # Parse ONU MAC Address List
    mac_addresses = re.findall(r"(\w{4}\.\w{4}\.\w{4})", raw_data)
    data['onu_list_mac'] = mac_addresses if mac_addresses else []

    return data

output = parse_data(raw_data)
output['raw_info'] = raw_data
print(output)