from flask import request, jsonify, current_app, url_for  # Agrega url_for aquí
from . import api_blueprint
from ..database import db
from .models import Factores
from sqlalchemy.exc import IntegrityError
from datetime import datetime
import traceback
from flask_mail import Mail, Message
from sqlalchemy import func

from flask_cors import CORS


# Suponiendo que tu blueprint ya está correctamente registrado
@api_blueprint.route("/factores", methods=["GET"])
def get_factores():
    factores = Factores.query.all()
    return jsonify([factor.to_dict() for factor in factores])

@api_blueprint.route("/factores/<int:id>", methods=["PUT"])
def update_factor(id):
    factor = Factores.query.get_or_404(id)
    data = request.json
    factor.valor_factores = data.get('valor_factores', factor.valor_factores)
    db.session.commit()
    return jsonify(factor.to_dict())