from flask import request, jsonify
from . import api_blueprint
from ..database import db
from .models import Payment, Reservation
from sqlalchemy.exc import IntegrityError
from datetime import datetime

@api_blueprint.route('/reservations/<int:reservation_id>/payments', methods=['POST'])
def create_payment(reservation_id):
    data = request.get_json()

    print("datos recibidos en /reservations/<int:reservation_id>/payments", data)

    try:
        # Crear el pago
        payment = Payment(
            reservation_id=reservation_id,
            payment_method=data['payment_method'],
            payment_amount=data['payment_amount'],
            payment_date=datetime.strptime(data['payment_date'], "%Y-%m-%d"),
            card_type=data.get('card_type'),
            card_number=data.get('card_number'),
            account_number=data.get('account_number')
        )

        # Verificar los datos antes de agregar a la base de datos
        print("lo que se envia al pago", payment)

        # Actualizar el total pagado en la reserva
        reservation = Reservation.query.get_or_404(reservation_id)
        reservation.reservation_amount_paid += payment.payment_amount

        # Actualizar el estado de la reserva basado en el total pagado
        if reservation.reservation_amount_paid >= reservation.reservation_total_amount:
            reservation.reservation_payment_status = "Completo"
            reservation.reservation_status = "Reservada"
        elif reservation.reservation_amount_paid > 0:
            reservation.reservation_payment_status = "Parcial"
            reservation.reservation_status = "Apartada"
        else:
            reservation.reservation_payment_status = "Pendiente"

        # Agregar el pago y hacer commit
        db.session.add(payment)
        db.session.commit()

        return jsonify({'message': 'Pago registrado correctamente'}), 201

    except IntegrityError:
        db.session.rollback()
        print("Error de integridad al registrar el pago:", traceback.format_exc())
        return jsonify({'error': 'Error al registrar el pago'}), 400

    except Exception as e:
        db.session.rollback()
        print("Error general al registrar el pago:", traceback.format_exc())  # Imprimir traceback completo
        return jsonify({'error': str(e)}), 500
    
@api_blueprint.route('/reservations/<int:reservation_id>/payments', methods=['GET'])
def get_payments_for_reservation(reservation_id):
    try:
        payments = Payment.query.filter_by(reservation_id=reservation_id).all()
        payments_list = [
            {
                'id_payment': p.id_payment,
                'payment_method': p.payment_method,
                'payment_amount': p.payment_amount,
                'payment_date': p.payment_date.strftime("%Y-%m-%d"),
                'card_type': p.card_type,
                'card_number': p.card_number,
                'account_number': p.account_number
            }
            for p in payments
        ]
        return jsonify({'payments': payments_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_blueprint.route('/payments/<int:payment_id>', methods=['DELETE'])
def delete_payment(payment_id):
    try:
        payment = Payment.query.get_or_404(payment_id)

        # Restar el monto del pago cancelado de la reserva
        reservation = Reservation.query.get_or_404(payment.reservation_id)
        reservation.reservation_amount_paid -= payment.payment_amount

        # Actualizar el estado de la reserva basado en el nuevo total pagado
        if reservation.reservation_amount_paid >= reservation.reservation_total_amount:
            reservation.reservation_payment_status = "Completo"
            reservation.reservation_status = "Reservada"
        elif reservation.reservation_amount_paid > 0:
            reservation.reservation_payment_status = "Parcial"
            reservation.reservation_status = "Apartada"
        else:
            reservation.reservation_payment_status = "Pendiente"

        db.session.delete(payment)
        db.session.commit()

        return jsonify({'message': 'Pago cancelado correctamente'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
