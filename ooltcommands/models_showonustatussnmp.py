from config import db, event

def init_db(app):
    with app.app_context():
        db.create_all()


class OltCommandShowOnuStatusSnmpModel(db.Model):
    __tablename__ = 'oltcommandshowonustatussnmp'
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
    showonustatus_software_1 = OltCommandShowOnuStatusSnmpModel(
        id_software=1, 
        script_python='''
def snmp_walk_to_excel(target_ip, community, version, port):
    from easysnmp import Session
    from datetime import datetime
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
            _stats_datetime = str(results_offline[no].value)

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

            hari = 0
            detik_sisa = 0
            jam = 0
            menit = 0
            detik = 0
            if _stats_datetime != '0000-00-00 00:00:00':
                format_waktu = "%Y-%m-%d %H:%M:%S"
                waktu_terakhir = datetime.strptime(_stats_datetime, format_waktu)
                waktu_sekarang = datetime.now()
                selisih = waktu_sekarang - waktu_terakhir
                hari = selisih.days
                detik_sisa = selisih.seconds
                jam = (detik_sisa // 3600) + (hari * 24 * 3600)
                menit = (detik_sisa % 3600) // 60
                detik = (detik_sisa % 3600) % 60

            data.append({
                "name": str(results_name[no].value),
                "status": status,
                "duration": f"{jam}h {menit}m {detik}s",
            })
        
        return data
    except Exception as e:
        print(f"Error: {e}")

target_ip = self.host
community = self.snmp_ro_com
version = 2 
port = self.snmp_port

output = snmp_walk_to_excel(target_ip, community, version, port)
''')
    
    db.session.add(showonustatus_software_1)
    db.session.commit()

event.listen(OltCommandShowOnuStatusSnmpModel.__table__, 'after_create', insert_initial_data)