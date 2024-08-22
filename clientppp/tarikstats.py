from flask import current_app
from sqlalchemy import func, select
from concurrent.futures import ThreadPoolExecutor

from .models import db, ClientPPPModel, ClientPPPStatsModel, ClientPPPStatMonthsModel
from mmikrotik.models import MmikrotikModel

from extensions import scheduler

from dotenv import load_dotenv
import os
load_dotenv()

from datetime import datetime
import time
class get_datetime():
    def __init__(self):
        self.now = datetime.now()
    
    def __str__(self):
        dt_string = self.now.strftime("%Y-%m-%d %H:%M:%S")
        return dt_string
    def unix(self):
        unix_time = int(time.mktime(self.now.timetuple()))
        return unix_time
    
    def unix_to_datetime(self, unix: int):
        self.unixnya = unix
        dt_obj = datetime.fromtimestamp(self.unixnya)
        dt_string = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
        return dt_string
    def datetime_to_unix(self, datetiming):
        self.datetimenya = datetiming
        dt_obj = datetime.strptime(self.datetimenya, "%Y-%m-%d %H:%M:%S")
        unix_time = int(time.mktime(dt_obj.timetuple()))
        return unix_time

def TarikStatsJob():
    with scheduler.app.app_context():
        import time
        from datetime import datetime, timedelta
        _time_updated = get_datetime()
        time_updated = _time_updated.unix()
        def generate_data(app, _mikrotik):
            with app.app_context():
                list_eth_status = _mikrotik._get_eth_status()
                list_user_mikrotik = ClientPPPModel.query.filter_by(mikrotik_id=_mikrotik.mikrotik_id).all()
                for _user_mikrotik in list_user_mikrotik:
                    name_interface = '<pppoe-{}>'.format(_user_mikrotik.name)
                    finding_number = None
                    for nomor, cari_stats in enumerate(list_eth_status):
                        if cari_stats['name'] == name_interface:
                            finding_number = nomor
                            break
                    
                    tx_byte = 0
                    rx_byte = 0
                    total_tx_byte = 0
                    total_rx_byte = 0
                    tx_packet = 0
                    rx_packet = 0    
                    total_tx_packet = 0
                    total_rx_packet = 0
                    
                    if finding_number != None:
                        data_stats = list_eth_status[finding_number]
                        last_stats = ClientPPPStatsModel.query.filter_by(client_id=_user_mikrotik.client_id).order_by(ClientPPPStatsModel.id.desc()).first()
                        if last_stats:
                            tx_byte = int(data_stats['tx-byte']) - last_stats.total_tx_byte
                            rx_byte = int(data_stats['rx-byte']) - last_stats.total_rx_byte
                            if tx_byte < 0:
                                tx_byte = int(data_stats['tx-byte'])
                            if rx_byte < 0:
                                rx_byte = int(data_stats['rx-byte'])
                            total_tx_byte = int(data_stats['tx-byte'])
                            total_rx_byte = int(data_stats['rx-byte'])
                            tx_packet = int(data_stats['tx-packet']) - last_stats.total_tx_packet
                            rx_packet = int(data_stats['rx-packet']) - last_stats.total_rx_packet  
                            if tx_packet < 0:
                                tx_packet = int(data_stats['tx-packet'])
                            if rx_packet < 0:
                                rx_packet = int(data_stats['rx-packet'])
                            total_tx_packet = int(data_stats['tx-packet'])
                            total_rx_packet = int(data_stats['rx-packet'])
                        else:
                            tx_byte = int(data_stats['tx-byte'])
                            rx_byte = int(data_stats['rx-byte'])
                            total_tx_byte = int(data_stats['tx-byte'])
                            total_rx_byte = int(data_stats['rx-byte'])
                            tx_packet = int(data_stats['tx-packet'])
                            rx_packet = int(data_stats['rx-packet'])  
                            total_tx_packet = int(data_stats['tx-packet'])
                            total_rx_packet = int(data_stats['rx-packet'])


                    add_clientstats = ClientPPPStatsModel(
                        _user_mikrotik.client_id, 
                        str(_time_updated),
                        time_updated,
                        tx_byte,
                        rx_byte, 
                        total_tx_byte, 
                        total_rx_byte, 
                        tx_packet, rx_packet, 
                        total_tx_packet, 
                        total_rx_packet, 
                        time_updated
                    )
                    db.session.add(add_clientstats)
                    db.session.commit()


        def tarik_datanya():
            app = current_app._get_current_object()
            list_mikrotik = MmikrotikModel.query.order_by(MmikrotikModel.mikrotik_id.asc()).all()
            with ThreadPoolExecutor() as executor:
                executor.map(lambda mikrotik: generate_data(app, mikrotik), list_mikrotik)
                
            #dimari
            current_date = datetime.now()
            start_date = current_date.replace(day=1)
            next_month = start_date + timedelta(days=32)
            end_date = next_month.replace(day=1)

            results = db.session.query(
                ClientPPPStatsModel.client_id,
                db.func.date_format(ClientPPPStatsModel.timestamp, '%Y-%m-01').label('month'),
                db.func.sum(ClientPPPStatsModel.tx_byte).label('total_tx_byte'),
                db.func.sum(ClientPPPStatsModel.rx_byte).label('total_rx_byte')
            ).filter(
                ClientPPPStatsModel.timestamp >= start_date,
                ClientPPPStatsModel.timestamp < end_date
            ).group_by(
                ClientPPPStatsModel.client_id,
                db.func.date_format(ClientPPPStatsModel.timestamp, '%Y-%m-01')
            ).all()

            def masukkan_data(app, result):
                with app.app_context():
                    data_exists = ClientPPPStatMonthsModel.query.filter_by(client_id=result.client_id, month=result.month).first()
                    if data_exists:
                        data_exists.download_byte = result.total_tx_byte
                        data_exists.upload_byte = result.total_rx_byte
                    else:
                        new_data = ClientPPPStatMonthsModel(
                            result.client_id,
                            result.month,
                            result.total_tx_byte,
                            result.total_rx_byte
                        )
                        db.session.add(new_data)
                    db.session.commit()

            app = current_app._get_current_object()
            with ThreadPoolExecutor() as executor:
                executor.map(lambda result: masukkan_data(app, result), results)  

        x = int(repr(os.getpid())[-1])
        if x > 0:
            x+=1
        elif x == 1:
            x+=5
        elif x > 1:
            x+=10
        time.sleep(x)
        last_data = ClientPPPStatsModel.query.order_by(ClientPPPStatsModel.id.desc()).first()
        intervalnya = int(os.environ["INTERVAL_GET_STATS"])
        if last_data:
            nextnya = last_data.time_updated + intervalnya
            if time_updated >= nextnya:
                current_app.logger.info('Jobs tarik stats')
                tarik_datanya()
            else:
                #current_app.logger.info('skipping tarik stats')
                pass
        else:

            current_app.logger.info('Jobs tarik stats')
            tarik_datanya()