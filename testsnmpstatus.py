def snmp_walk_to_excel(target_ip, community, version, port):
    from easysnmp import Session
    try:
        # Membuat sesi SNMP
        session = Session(
            hostname=f"{target_ip}:{port}",  
            community=community,
            version=version
        )
        
        # Melakukan SNMP Walk untuk semua data
        results_name = session.walk('.1.3.6.1.4.1.3902.1012.3.28.1.1.2')  
        results_status = session.walk('.1.3.6.1.4.1.3902.1012.3.28.2.1.4') 
        results_online = session.walk('.1.3.6.1.4.1.3902.1012.3.28.2.1.5')
        results_offline = session.walk('.1.3.6.1.4.1.3902.1012.3.28.2.1.5') 
        

        # Mengolah data hasil SNMP Walk
        data = []
        for no,result in enumerate(results_name):
            # Log setiap hasil SNMP Walk
            status_num = int(results_status[no].value)
            stats_datetime = str(results_offline[no].value)

            if status_num == 3:
                status = "working"
                stats_datetime = str(results_online[no].value)
            elif status_num == 2:
                status = "synMib"
            elif status_num == 1:
                status = "los"
            elif status_num == 0:
                status = "logging"
            elif status_num == 4:
                status = "dyingGasp"
            elif status_num == 5:
                status = "autFailed"
            elif status_num == 6:
                status = "OffLine"

            data.append({
                "name": str(results_name[no].value),
                "status": status,
                "datetime": stats_datetime,
            })
        
        return data
    except Exception as e:
        print(f"Error: {e}")

target_ip = "103.247.21.15"  # Ganti dengan IP perangkat
community = "arenjayaro"       # Ganti dengan community string
version = 2                # Versi SNMP (1, 2, atau 3)
port = 2167                 # Port SNMP non-standar

output = snmp_walk_to_excel(target_ip, community, version, port)
print(output)