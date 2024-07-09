from flask import Blueprint
api_blueprint = Blueprint('api', __name__)

from . import login, cubicuadraje,users,forecast,enterprise,ocupacion,proyeccion,factores

