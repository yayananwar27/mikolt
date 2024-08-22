from config import db
from flask import current_app

from dotenv import load_dotenv
import os
load_dotenv()

def init_db(app):
    with app.app_context():
        db.create_all()

from mmikrotik.models import MmikrotikModel

from datetime import datetime
def created_time():
    dt_now = datetime.now()
    date = dt_now.strftime("%Y-%m-%d %H:%M:%S")
    return str(date)

class ClientPPPModel(db.Model):
    __tablename__ = 'clientppp'
    client_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    password  = db.Column(db.String(255), nullable=True)
    profile  = db.Column(db.String(255), nullable=True)
    service_type  = db.Column(db.String(50), nullable=True)
    mikrotik_id = db.Column(db.Integer, nullable=True)
    #mikrotik_id = db.Column(db.Integer, db.ForeignKey('mmikrotik.mikrotik_id', ondelete='CASCADE'), nullable=True)
    status  = db.Column(db.String(50), nullable=False)
    configuration = db.Column(db.String(50), nullable=False)
    comment = db.Column(db.Text, nullable=True)
    ref_id = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=created_time())
    created_by = db.Column(db.String(50), nullable=True)
    last_update_at = db.Column(db.DateTime, nullable=True)
    last_update_by = db.Column(db.String(50), nullable=True)


    def __init__(self, name, status, configuration='unconfigured' ,password=None, profile=None, service_type=None, mikrotik_id=None, comment=None, ref_id=None, created_by=None, sync=False):
        self.name = name
        self.status = status
        self.configuration = configuration
        self.password = password
        self.profile = profile
        self.service_type = service_type
        self.mikrotik_id = mikrotik_id
        self.comment = comment
        self.ref_id = ref_id
        self.created_at = created_time()
        self.created_by = created_by
        if self.ref_id == None:
            if self.password != None and self.profile != None and self.mikrotik_id != None and sync == False:
                mikrotiknya = MmikrotikModel.query.filter_by(mikrotik_id=self.mikrotik_id).first()
                if mikrotiknya:
                    if status == 'disable':
                        isolir_ready = mikrotiknya._get_profile_ppoe_isolir()
                        if isolir_ready['status'] == True:
                            add_secret = mikrotiknya._add_ppp_secret(self.name, self.service_type, self.password, str(os.environ["PROFILE_ISOLIR_NAME"]), self.comment)
                        else:
                            add_secret = mikrotiknya._add_ppp_secret(self.name, self.service_type, self.password, self.profile, self.comment, 'true')
                    else:
                        add_secret = mikrotiknya._add_ppp_secret(self.name, self.service_type, self.password, self.profile, self.comment)

                    if add_secret == True:
                        id_secret = mikrotiknya._get_ppp_secret(self.name)
                        self.ref_id = id_secret[0]['id']

    def to_dict(self):
        try:
            site_id = None
            if self.mikrotik_id != None:
                mikrotiknya = MmikrotikModel.query.filter_by(mikrotik_id=self.mikrotik_id).first()
                site_id = mikrotiknya.site_id

            data = {
                'client_id' : self.client_id,
                'name':self.name,
                'password':self.password,
                'status':self.status,
                'configuration':self.configuration,
                'profile':self.profile,
                'service_type':self.service_type,
                'mikrotik_id':self.mikrotik_id,
                'comment':self.comment,
                'ref_id':self.ref_id,
                'created_at':str(self.created_at),
                'created_by':self.created_by,
                'last_update_at':str(self.last_update_at),
                'last_update_by':self.last_update_by,
                'site_id':site_id
            }
            return data
        
        except:
            return None
        

    def to_dict_stats(self):
        try:
            data = {
                'client_id' : self.client_id,
                'name':self.name,
                'password':self.password,
                'status':self.status,
                'configuration':self.configuration,
                'profile':self.profile,
                'service_type':self.service_type,
                'mikrotik_id':self.mikrotik_id,
                'comment':self.comment,
                'ref_id':self.ref_id,
                'created_at':str(self.created_at),
                'created_by':self.created_by,
                'last_update_at':str(self.last_update_at),
                'last_update_by':self.last_update_by
            }
            data['last_logged_out'] = None
            data['last_caller_id'] = None
            data['last_disconnect_reason'] = None
            data['disabled'] = None
            data['mikrotik_profile'] = None
            data['interface_name'] = None
            data['service'] = None
            data['uptime'] = None
            data['last_link_up_time'] = None
            data['rx_byte'] = 0
            data['tx_byte'] = 0
            data['rx_packet'] = 0
            data['tx_packet'] = 0
            data['rx_bits_ps'] = 0
            data['tx_bits_ps'] = 0
            data['rx_packet_ps'] = 0
            data['tx_packet_ps'] = 0
            data['caller_id'] = None
            data['interface'] = None
            data['local_address'] = None
            data['remote_address'] = None

            try:
                if self.password != None and self.profile != None and self.mikrotik_id != None:
                    mikrotiknya = MmikrotikModel.query.filter_by(mikrotik_id=self.mikrotik_id).first()
                    if mikrotiknya:
                        info_secret = mikrotiknya._get_ppp_secret(self.name)
                        current_app.logger.debug(info_secret)
                        data['mikrotik_profile'] = info_secret[0]['profile']
                        data['disabled'] = info_secret[0]['disabled']
                        data['last_logged_out'] = info_secret[0]['last-logged-out']
                        try:
                            data['caller_id'] = info_secret[0]['last-caller-id']
                            data['last_disconnect_reason'] = info_secret[0]['last-disconnect-reason']
                        except:
                            pass
                        try:
                            info_int_pppoeserver = mikrotiknya._get_int_pppoeserver(self.name)
                            if len(info_int_pppoeserver)>0:
                                data['interface_name'] = info_int_pppoeserver[0]['name']
                                data['service'] = info_int_pppoeserver[0]['service']
                                data['uptime'] = info_int_pppoeserver[0]['uptime']

                                info_int_stats = mikrotiknya._get_eth_status(data['interface_name'])
                                data['last_link_up_time'] = info_int_stats[0]['last-link-up-time']
                                data['rx_byte'] = info_int_stats[0]['rx-byte']
                                data['tx_byte'] = info_int_stats[0]['tx-byte']
                                data['rx_packet'] = info_int_stats[0]['rx-packet']
                                data['tx_packet'] = info_int_stats[0]['tx-packet']

                                info_int_mon = mikrotiknya._get_mon_traffic(data['interface_name'])
                                data['rx_bits_ps'] = info_int_mon[0]['rx-bits-per-second']
                                data['tx_bits_ps'] = info_int_mon[0]['tx-bits-per-second']
                                data['rx_packet_ps'] = info_int_mon[0]['rx-packets-per-second']
                                data['tx_packet_ps'] = info_int_mon[0]['tx-packets-per-second']

                                info_ip_mon = mikrotiknya._get_mon_ipadress(data['interface_name'])
                                data['caller_id'] = info_ip_mon[0]['caller-id']
                                data['interface'] = info_ip_mon[0]['interface']
                                data['local_address'] = info_ip_mon[0]['local-address']
                                data['remote_address'] = info_ip_mon[0]['remote-address']
                        except Exception as e:
                            print(e)
            except Exception as e:
                print(e)
                return data    
            return data
        
        except:
            return None
    

class ClientPPPStatsModel(db.Model):
    __tablename__ = 'clientpppstats'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    timestamp_unix = db.Column(db.Integer, nullable=False)
    tx_byte = db.Column(db.BigInteger, nullable=True)
    rx_byte = db.Column(db.BigInteger, nullable=True)
    total_tx_byte = db.Column(db.BigInteger, nullable=True)
    total_rx_byte = db.Column(db.BigInteger, nullable=True)
    tx_packet = db.Column(db.BigInteger, nullable=True)
    rx_packet = db.Column(db.BigInteger, nullable=True)
    total_tx_packet = db.Column(db.BigInteger, nullable=True)
    total_rx_packet = db.Column(db.BigInteger, nullable=True)
    time_updated = db.Column(db.Integer, nullable=False)
    
    def __init__(self, client_id, timestamp, timestamp_unix, tx_byte, rx_byte, total_tx_byte, total_rx_byte, tx_packet, rx_packet, total_tx_packet, total_rx_packet, time_upadated=None):
        self.client_id = client_id 
        self.timestamp = timestamp
        self.timestamp_unix = timestamp_unix
        self.tx_byte = tx_byte
        self.rx_byte = rx_byte
        self.total_tx_byte = total_tx_byte
        self.total_rx_byte = total_rx_byte
        self.tx_packet = tx_packet
        self.rx_packet = rx_packet        
        self.total_tx_packet = total_tx_packet
        self.total_rx_packet = total_rx_packet
        self.time_updated = time_upadated

    def to_dict(self):
        data = {
            'id':self.id,
            'client_id':self.client_id,
            'timestamp':str(self.timestamp),
            'timestamp_unix':self.timestamp_unix,
            'tx_byte':self.tx_byte,
            'rx_byte':self.rx_byte,
            'tx_packet':self.tx_packet,
            'rx_packet':self.rx_packet
        }
        return data

    def to_dict_total(self):
        data = {
            'id':self.id,
            'client_id':self.client_id,
            'timestamp':str(self.timestamp),
            'timestamp_unix':self.timestamp_unix,
            'tx_byte':self.tx_byte,
            'rx_byte':self.rx_byte,
            'total_tx_byte':self.total_tx_byte,
            'total_rx_byte':self.total_rx_byte,
            'tx_packet':self.tx_packet,
            'rx_packet':self.rx_packet,       
            'total_tx_packet':self.total_tx_packet,
            'total_rx_packet':self.total_rx_packet
        }
        return data
        

class ClientPPPStatMonthsModel(db.Model):
    __tablename__ = 'clientpppstatsmonth'
    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    client_id = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Date, nullable=False)
    download_byte = db.Column(db.BigInteger, nullable=True)
    upload_byte = db.Column(db.BigInteger, nullable=True)

    def __init__(self, client_id, month, download_byte=0, upload_byte=0):
        self.client_id = client_id
        self.month = month
        self.download_byte = download_byte
        self.upload_byte = upload_byte

    def to_dict(self):
        month = self.month
        _month = month.strftime("%Y-%m")
        data = {
            'id':self.id,
            'client_id':self.client_id,
            'month':_month,
            'upload':self.upload_byte,
            'download':self.download_byte
        }
        return data
