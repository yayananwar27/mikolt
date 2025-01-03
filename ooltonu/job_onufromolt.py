import os
from extensions import scheduler
from ooltdevices.models import OltDevicesModels
from flask import current_app
from concurrent.futures import ThreadPoolExecutor

def SyncOnuFromOlt():
    with scheduler.app.app_context():
        x = int(repr(os.getpid())[-1])
        if x == 3:
            app = current_app._get_current_object()
            device_list = OltDevicesModels.query.all()

            def syncing(app, device):
                with app.app_context():
                    device.sync_onu_configured_from_olt()

            with ThreadPoolExecutor() as executor:
                executor.map(lambda device: syncing(app, device), device_list)

def GetOnuStatusFromOlt():
    with scheduler.app.app_context():
        x = int(repr(os.getpid())[-1])
        if x == 3:
            app = current_app._get_current_object()
            device_list = OltDevicesModels.query.all()

            def historying(app, device):
                with app.app_context():
                    device.Get_onu_status_history()

            with ThreadPoolExecutor() as executor:
                executor.map(lambda device: historying(app, device), device_list)