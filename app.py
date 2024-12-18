from flask import Flask, jsonify, request
from config import ApplicationConfig
from flask_apispec.extension import FlaskApiSpec
from flask_cors import CORS
from extensions import scheduler
import logging
import time

app = Flask(__name__)
CORS(app, supports_credentials=True, resources=r'*', origins="*", methods=['GET','POST','PUT','DELETE'])
app.config.from_object(ApplicationConfig)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("access_logger")

# Create a handler for writing logs to a file
handler = logging.FileHandler("log/access.log")
handler.setLevel(logging.INFO)

# Define the log format
formatter = logging.Formatter(
    "%(asctime)s - %(remote_addr)s - %(method)s - %(url)s - %(status)s - %(response_time)s ms"
)
handler.setFormatter(formatter)
logger.addHandler(handler)

app.logger.setLevel(logging.DEBUG)

from config import db
from accessapp.models import init_db as init_db_accessapp
from userlogin.models import init_db as init_db_userlogin
from sites.models import init_db as init_db_sites
from mmikrotik.models import init_db as init_db_mmikrotik
from clientppp.models import init_db as init_db_clientppp
from logmikolt.model import init_db as init_db_logmikolt
from ospeedprofile.models import init_db as init_db_speedprofile
from oonutypes.models import init_db as init_db_onutypes
from ooltmaster.models import init_db as init_db_oltmaster
from ooltdevices.models import init_db as init_db_oltdevices
from ooltonu.models import init_db as init_db_oltonu

from ooltcommands.models_uptime import init_db as init_db_oltcommand_uptime
from ooltcommands.models_showcard import init_db as init_db_oltcommand_showcard
from ooltcommands.models_showcardpon import init_db as init_db_oltcommand_showcardpon
from ooltcommands.models_showcarduplink import init_db as init_db_oltcommand_showcarduplink
from ooltcommands.models_showuplinkvlan import init_db as init_db_oltcommand_showuplinkvlan
from ooltcommands.models_showcardonutype import init_db as init_db_oltcommand_showcardonutype
from ooltcommands.models_showvlan import init_db as init_db_oltcommand_showvlan
from ooltcommands.models_showlistonu import init_db as init_db_oltcommand_showlistonu
from ooltcommands.models_showonustatus import init_db as init_db_oltcommand_showonustatus

from ooltcommands.models_adddevicevlan import init_db as init_db_adddevicevlan
from ooltcommands.models_adduplinkvlan import init_db as init_db_adduplinkvlan
from ooltcommands.models_updatedevicevlan import init_db as init_db_updatedevicevlan
from ooltcommands.models_deletedevicevlan import init_db as init_db_deletedevicevlan
from ooltcommands.models_deleteuplinkvlan import init_db as init_db_deleteuplinkvlan


scheduler.init_app(app)
db.init_app(app)
init_db_accessapp(app)
init_db_userlogin(app)
init_db_sites(app)
init_db_mmikrotik(app)
init_db_clientppp(app)
init_db_logmikolt(app)
init_db_speedprofile(app)
init_db_onutypes(app)
init_db_oltmaster(app)
init_db_oltdevices(app)
init_db_oltonu(app)

init_db_oltcommand_uptime(app)
init_db_oltcommand_showcard(app)
init_db_oltcommand_showcardpon(app)
init_db_oltcommand_showcarduplink(app)
init_db_oltcommand_showuplinkvlan(app)
init_db_oltcommand_showcardonutype(app)
init_db_oltcommand_showvlan(app)
init_db_oltcommand_showlistonu(app)
init_db_oltcommand_showonustatus(app)

init_db_adddevicevlan(app)
init_db_adduplinkvlan(app)

init_db_updatedevicevlan(app)

init_db_deletedevicevlan(app)
init_db_deleteuplinkvlan(app)
# Middleware to log the request processing time
@app.before_request
def start_timer():
    request.start_time = time.time()

@app.after_request
def log_request(response):
    # Calculate response time
    response_time = (time.time() - request.start_time) * 1000  # Convert to milliseconds

    # Log the details
    logger.info(
        "",
        extra={
            "remote_addr": request.remote_addr,
            "method": request.method,
            "url": request.url,
            "status": response.status_code,
            "response_time": f"{response_time:.2f}",
        },
    )

    return response

from werkzeug.exceptions import HTTPException

@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    app.logger.error(str(e))
    return jsonify(error=str(e)), code

with app.app_context():
    docs = FlaskApiSpec(app)
    scheduler.start()

    #Token
    from accessapp.app import init_docs as init_docs_accessapp, accessapp_api
    app.register_blueprint(accessapp_api, url_prefix='/token')
    init_docs_accessapp(docs)

    #User Login
    from userlogin.app import init_docs as init_docs_userlogin, userlogin_api
    app.register_blueprint(userlogin_api, url_prefix='/userlogin')
    init_docs_userlogin(docs)

    #Sites
    from sites.app import init_docs as init_docs_sites, sites_api
    app.register_blueprint(sites_api, url_prefix='/sites')
    init_docs_sites(docs)

    #mmikrotik
    from mmikrotik.app import init_docs as init_docs_mmikrotik, mmikrotik_api
    app.register_blueprint(mmikrotik_api, url_prefix='/mikrotik')
    init_docs_mmikrotik(docs)

    #mppprofile
    from mpppprofile.app import init_docs as init_docs_mppprofile, mpppprofile_api
    app.register_blueprint(mpppprofile_api, url_prefix='/profile')
    init_docs_mppprofile(docs)

    #clientppp
    from clientppp.app import init_docs as init_docs_clientppp, clientppp_api
    app.register_blueprint(clientppp_api, url_prefix='/clientppp')
    init_docs_clientppp(docs)

    #dashboard
    from dashboard.app import init_docs as init_docs_dashboard, dashboard_api
    app.register_blueprint(dashboard_api, url_prefix='/dashboard')
    init_docs_dashboard(docs)
    
    #speed profile
    from ospeedprofile.app import init_docs as init_docs_speedprofile, speedprofile_api
    app.register_blueprint(speedprofile_api, url_prefix='/olt/speedprofile')
    init_docs_speedprofile(docs)
    
    #onu types
    from oonutypes.app import init_docs as init_docs_onutypes, onutypes_api
    app.register_blueprint(onutypes_api, url_prefix='/olt/onutypes')
    init_docs_onutypes(docs)

    #Olt Master
    from ooltmaster.app import init_docs as init_docs_oltmaster, oltmaster_api
    app.register_blueprint(oltmaster_api, url_prefix='/olt/oltmaster')
    init_docs_oltmaster(docs)

    #olt Device
    from ooltdevices.app import init_docs as init_docs_oltdevices, oltdevices_api
    app.register_blueprint(oltdevices_api, url_prefix='/olt/devices')
    init_docs_oltdevices(docs)

    #olt Onu
    from ooltonu.app import init_docs as init_docs_oltonu, oltonu_api
    app.register_blueprint(oltonu_api, url_prefix='/olt/onu')
    init_docs_oltonu(docs)

if __name__ == "__main__":

    import os
    from dotenv import load_dotenv
    load_dotenv()
    app.run(os.environ['HOST'], port=os.environ['PORT'],debug=True)
