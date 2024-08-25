from flask import request, jsonify, current_app
from . import api_blueprint
from ..database import db
from .models import Price, Asset
from sqlalchemy.exc import IntegrityError
from datetime import datetime
from sqlalchemy.sql import func


@api_blueprint.route('/prices', methods=['POST'])
def add_price():
    data = request.get_json()
    try:
        # Asegurarse de que el asset exista
        asset = Asset.query.get(data['asset_id'])
        if not asset:
            return jsonify({'message': 'Asset no encontrado'}), 404

        # Crear un nuevo precio para el asset
        price = Price(
            asset_id=data['asset_id'],
            rental_price=data['rental_price'],
            deposit_type=data['deposit_type'],
            deposit_value=data['deposit_value'],
            deposit_amount=data['deposit_amount'],
            currency=data['currency']
        )

        db.session.add(price)
        db.session.commit()

        return jsonify({'message': 'Precio creado correctamente', 'id_price': price.id_price}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Error al guardar el precio. Datos inválidos o duplicados'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Error al procesar la solicitud', 'details': str(e)}), 500

@api_blueprint.route('/prices/<int:asset_id>/latest', methods=['GET'])
def get_latest_price(asset_id):
    try:
        # Obtener el último precio para el asset
        latest_price = Price.query.filter_by(asset_id=asset_id).order_by(Price.created_at.desc()).first()
        if not latest_price:
            return jsonify({'message': 'No hay precios disponibles para este asset'}), 404

        return jsonify({
            'asset_id': latest_price.asset_id,
            'rental_price': latest_price.rental_price,
            'deposit_type': latest_price.deposit_type,
            'deposit_value': latest_price.deposit_value,
            'deposit_amount': latest_price.deposit_amount,
            'currency': latest_price.currency,
            'created_at': latest_price.created_at
        }), 200
    except Exception as e:
        return jsonify({'message': 'Error al obtener el último precio', 'details': str(e)}), 500


@api_blueprint.route('/prices', methods=['GET'])
def get_prices():
    try:
        # Recoge los parámetros de búsqueda desde la consulta GET
        asset_id = request.args.get('asset_id', type=int)
        currency = request.args.get('currency')
        price_min = request.args.get('price_min', type=float)
        price_max = request.args.get('price_max', type=float)
        
        # Subquery to get the latest price for each asset
        subquery = db.session.query(
            Price.asset_id,
            func.max(Price.created_at).label('max_created_at')
        ).group_by(Price.asset_id).subquery()

        # Filtros base para la consulta
        query = Price.query.join(subquery, (Price.asset_id == subquery.c.asset_id) & (Price.created_at == subquery.c.max_created_at))
        
        if asset_id:
            query = query.filter(Price.asset_id == asset_id)
        
        if currency:
            query = query.filter(Price.currency == currency)
        
        if price_min is not None:
            query = query.filter(Price.rental_price >= price_min)
        
        if price_max is not None:
            query = query.filter(Price.rental_price <= price_max)

        prices = query.all()
        
        # Serializa los datos de los precios
        prices_list = [{
            "id_price": p.id_price,
            "asset_name": p.asset.asset_name,  # Accedes al nombre del asset desde la relación
            "rental_price": p.rental_price,
            "currency": p.currency,
            "created_at": p.created_at  # Agregar la fecha de creación
        } for p in prices]
        
        return jsonify(prices_list), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Error interno del servidor"}), 500