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

if __name__ == "__main__":

    import os
    from dotenv import load_dotenv
    load_dotenv()
    app.run(os.environ['HOST'], port=os.environ['PORT'],debug=True)
