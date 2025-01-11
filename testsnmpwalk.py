import logging
from easysnmp import Session
import pandas as pd

# Setup logging
logging.basicConfig(filename='snmp_walk_debug1.log', level=logging.DEBUG, format='%(asctime)s - %(message)s')

def snmp_walk_to_excel(target_ip, community, version, port, output_file):
    """
    Melakukan SNMP Walk dan menyimpan hasilnya ke dalam file Excel serta menulis log.
    
    Args:
        target_ip (str): IP address perangkat.
        community (str): Community string SNMP.
        version (int): Versi SNMP (1, 2, atau 3).
        port (int): Port SNMP perangkat.
        output_file (str): Nama file output (format .xlsx).
    """
    try:
        # Membuat sesi SNMP
        session = Session(
            hostname=f"{target_ip}:{port}",  # Tambahkan port ke hostname
            community=community,
            version=version
        )
        
        # Melakukan SNMP Walk untuk semua data
        logging.info(f"Melakukan SNMP Walk pada {target_ip}:{port}...")
        print(f"Melakukan SNMP Walk pada {target_ip}:{port}...")
        results = session.walk('.1.3.6.1.4.1.3902.1012.3.28.1.1.2')  # '.1' untuk memulai dari root
        
        # Mengolah data hasil SNMP Walk
        data = []
        for result in results:
            # Log setiap hasil SNMP Walk
            logging.debug(f"OID: {result.oid}.{result.oid_index} - Value: {result.value} - Type: {result.snmp_type}")
            print(f"OID: {result.oid}.{result.oid_index} - Value: {result.value} - Type: {result.snmp_type}")
            
            data.append({
                "OID": f"{result.oid}.{result.oid_index}",
                "Value": result.value,
                "Type": result.snmp_type
            })
        
        # Membuat DataFrame
        df = pd.DataFrame(data)
        
        # Menyimpan ke file Excel
        df.to_excel(output_file, index=False)
        logging.info(f"Hasil SNMP Walk telah disimpan ke {output_file}")
        print(f"Hasil SNMP Walk telah disimpan ke {output_file}")
    
    except Exception as e:
        logging.error(f"Error: {e}")
        print(f"Error: {e}")

# Contoh penggunaan
if __name__ == "__main__":
    target_ip = "103.247.21.15"  # Ganti dengan IP perangkat
    community = "arenjayaro"       # Ganti dengan community string
    version = 2                # Versi SNMP (1, 2, atau 3)
    port = 2167                 # Port SNMP non-standar
    output_file = "snmp_walk_output_name.xlsx"

    snmp_walk_to_excel(target_ip, community, version, port, output_file)
