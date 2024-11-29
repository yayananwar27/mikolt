from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort
import requests

from .models import db,SitesModel
from accessapp.authapp import auth

from dotenv import load_dotenv
import os
load_dotenv()

class SyncSiteApi(MethodResource, Resource):
    @doc(description='Syncs Site Enigma', tags=['Sites'], security=[{"ApiKeyAuth": []}])
    @auth.login_required(role=['api','noc','superadmin'])
    def get(self, **kwargs):
        headers = {"X-SECRET-KEY":os.environ["ENIGMA_KEY"],"Accept":"application/json","Content-Type": "application/json"}
        #SiteUrl = 'locations'
        #url = f"https://staging.idenigma.id/api/v1/{SiteUrl}"
        #url = f"https://idenigma.id/api/v1/{SiteUrl}"
        url = f"{os.environ['ENIGMA_URL']}"


        session = requests.Session()
        response = session.get(url, headers=headers, verify=True)
        api_data = response.json()
        ebillingsiteid = []
        for data in api_data['data']:
            ebillingsiteid.append(data['id'])
            dataid_exists = SitesModel.query.filter_by(site_id=data['id']).first()
            if dataid_exists:
                dataid_exists.name = data['name']
                dataid_exists.code = data['code']
            else:
                new_data = SitesModel(data['name'], data['id'], data['code'])
                db.session.add(new_data)
            
            db.session.commit()

        dataid_exists = SitesModel.query.order_by(SitesModel.site_id.asc()).all()
        for dataid in dataid_exists:
            if dataid.site_id not in  ebillingsiteid:
                db.session.delete(dataid)
        db.session.commit()
        
        return jsonify({'message':'success'})
    
from extensions import scheduler
def SyncSiteJob():
    with scheduler.app.app_context():
        x = int(repr(os.getpid())[-1])
        if x == 2:
            headers = {"X-SECRET-KEY":os.environ["ENIGMA_KEY"],"Accept":"application/json","Content-Type": "application/json"}
            SiteUrl = 'locations'
            #url = f"https://staging.idenigma.id/api/v1/{SiteUrl}"
            #url = f"https://idenigma.id/api/v1/{SiteUrl}"
            url = f"{os.environ['ENIGMA_URL']}"


            session = requests.Session()
            response = session.get(url, headers=headers, verify=True)
            api_data = response.json()
            ebillingsiteid = []
            for data in api_data['data']:
                ebillingsiteid.append(data['id'])
                dataid_exists = SitesModel.query.filter_by(site_id=data['id']).first()
                if dataid_exists:
                    dataid_exists.name = data['name']
                    dataid_exists.code = data['code']
                else:
                    new_data = SitesModel(data['name'], data['id'], data['code'])
                    db.session.add(new_data)
                
                db.session.commit()

            dataid_exists = SitesModel.query.order_by(SitesModel.site_id.asc()).all()
            for dataid in dataid_exists:
                if dataid.site_id not in  ebillingsiteid:
                    db.session.delete(dataid)
            db.session.commit()
            current_app.logger.debug("Sync Site to E-Billing Site")
        else:
            current_app.logger.info('PID {} skipping Site to E-Billing Sites'.format(x))