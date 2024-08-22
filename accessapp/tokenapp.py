from jwt import encode, decode, InvalidTokenError
from flask import current_app
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

class create_token_jwt():
    def __init__(self, payload):
        self.payload = payload
    
    def get_token(self):
        return encode(
            self.payload, current_app.config['SECRET_KEY'], algorithm='HS256'
        )
    
class verify_token_jwt():
    def __init__(self, token):
        self.token = token
    def verify_token(self):
        try:
            data = decode(self.token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            time_now = get_datetime()
            if data['role'] == 'api':
                return True
            if time_now.unix() <= data['expired']:
                return True
            else:
                return False
        except InvalidTokenError:
            return False
    def payload_token(self):
        try:
            data = decode(self.token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            return data
        except InvalidTokenError:
            return False
