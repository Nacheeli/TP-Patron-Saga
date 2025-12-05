from flask import Blueprint, request
from marshmallow import ValidationError
from app import limiter
from app.mapping import PagosSchema, ResponseSchema
from app.services import PagosService, ResponseBuilder

Pagos = Blueprint('Pagos', __name__)  
service = PagosService()
pagos_schema = PagosSchema()
response_schema = ResponseSchema()

@Pagos.route('/pagos/transaccion', methods=['POST'])
@limiter.limit("5 per minute")
def realizar_transaccion():
    response_builder = ResponseBuilder()
    try:
        json_data = request.json
        if not json_data:
            raise ValidationError("No data provided")
        
        pago = pagos_schema.load(json_data)
        resultado = service.realizar_transaccion(pago)
        
        if resultado['code'] == 409:
            response_builder.add_message("Transacción fallida: Fondos insuficientes").add_status_code(409)
            return response_schema.dump(response_builder.build()), 409
        
        data = pagos_schema.dump(resultado['data'])
        response_builder.add_message("Transacción exitosa").add_status_code(201).add_data(data)
        return response_schema.dump(response_builder.build()), 201
        
    except ValidationError as err:
        response_builder.add_message("Validation error").add_status_code(422).add_data(err.messages)
        return response_schema.dump(response_builder.build()), 422
    except Exception as e:
        response_builder.add_message("Error procesando transacción").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Pagos.route('/pagos/<int:id>/compensacion', methods=['POST'])
@limiter.limit("5 per minute")
def compensar_transaccion(id):
    response_builder = ResponseBuilder()
    try:
        resultado = service.compensar_pago(id)
        
        if not resultado:
            response_builder.add_message("Pago no encontrado").add_status_code(404).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 404
        
        response_builder.add_message("Compensación realizada exitosamente").add_status_code(204).add_data({'id': id})
        return response_schema.dump(response_builder.build()), 204
        
    except Exception as e:
        response_builder.add_message("Error realizando compensación").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Pagos.route('/pagos', methods=['GET'])
@limiter.limit("5 per minute")
def all():
    response_builder = ResponseBuilder()
    try:
        data = pagos_schema.dump(service.all(), many=True)
        response_builder.add_message("Pagos encontrados").add_status_code(200).add_data(data)
        return response_schema.dump(response_builder.build()), 200
    except Exception as e:
        response_builder.add_message("Error obteniendo pagos").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500

@Pagos.route('/pagos/<int:id>', methods=['GET'])
@limiter.limit("5 per minute")
def one(id):
    response_builder = ResponseBuilder()
    try:
        data = service.find(id)
        if data:
            serialized_data = pagos_schema.dump(data)
            response_builder.add_message("Pago encontrado").add_status_code(200).add_data(serialized_data)
            return response_schema.dump(response_builder.build()), 200
        else:
            response_builder.add_message("Pago no encontrado").add_status_code(404).add_data({'id': id})
            return response_schema.dump(response_builder.build()), 404
    except Exception as e:
        response_builder.add_message("Error obteniendo pago").add_status_code(500).add_data(str(e))
        return response_schema.dump(response_builder.build()), 500
