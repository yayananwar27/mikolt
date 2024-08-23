from marshmallow import Schema, fields
from flask_restful import Resource
from flask_apispec.views import MethodResource
from flask_apispec import marshal_with, doc, use_kwargs
from flask import jsonify, current_app, request, abort

from accessapp.authapp import auth

from .models import TcontSpeedProfileModel
from userlogin.models import AllowedSiteUserModel

class CreateTcontSpeedProfileSchema(Schema):
    name = fields.String(required=True, metadata={"description":"Name Tcont Profile"})
    type = fields.Integer(required=True, metadata={"description":"Type Tcont 1-5"})
    fixed = fields.Integer(required=True, metadata={"description":"Fixed Bandwidth"})
    assured = fields.Integer(required=True, metadata={"description":"Assured Bandwidth"})
    maximum = fields.Integer(required=True, metadata={"description":"Maximum Bandwidth"})
    
class TcontSpeedProfileSchema(Schema):
    id = fields.Integer(required=True, metadata={"description":"Fixed Bandwidth"})
    name = fields.String(required=False, metadata={"description":"Name Tcont Profile"})
    type = fields.Integer(required=False, metadata={"description":"Type Tcont 1-5"})
    fixed = fields.Integer(required=False, metadata={"description":"Fixed Bandwidth"})
    assured = fields.Integer(required=False, metadata={"description":"Assured Bandwidth"})
    maximum = fields.Integer(required=False, allow_metadata={"description":"Maximum Bandwidth"})

class ListTcontSpeedProfileSchema(Schema):
    data = fields.List(fields.Nested(TcontSpeedProfileModel))

