from flask import Blueprint
api_blueprint = Blueprint('api', __name__)

from . import login, reservation, users,enterprise,estatus,properties,assettype,assetstatus,asset,client,reservationstatus,reservation,prices,payment

