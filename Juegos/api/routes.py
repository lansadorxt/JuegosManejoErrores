from flask import Blueprint
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort  # <-- Se agregó 'abort' aquí
from extensions import db
from models import Juego

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Esquema de datos para JSON
juego_fields = {
    'id': fields.Integer,
    'nombre': fields.String,
    'descripcion': fields.String,
    'precio': fields.Float
}

# Parser para validaciones de entrada
juego_parser = reqparse.RequestParser()
juego_parser.add_argument('nombre', type=str, required=True, help="El campo 'nombre' es obligatorio.")
juego_parser.add_argument('descripcion', type=str, required=True, help="El campo 'descripcion' es obligatorio.")
juego_parser.add_argument('precio', type=float, required=True, help="El campo 'precio' es obligatorio.")

class JuegoList(Resource):
    @marshal_with(juego_fields)
    def get(self):
        juegos = Juego.query.all()
        return juegos, 200

    @marshal_with(juego_fields)
    def post(self):
        args = juego_parser.parse_args()
        nuevo_juego = Juego(
            nombre=args['nombre'],
            descripcion=args['descripcion'],
            precio=args['precio']
        )
        db.session.add(nuevo_juego)
        db.session.commit()
        return nuevo_juego, 201

class JuegoResource(Resource):
    @marshal_with(juego_fields)
    def get(self, id):
        juego = Juego.query.get(id)
        if not juego:
            abort(404, message=f"El juego con ID {id} no existe.")  # <-- Corregido sin 'api.'
        return juego, 200

    @marshal_with(juego_fields)
    def put(self, id):
        juego = Juego.query.get(id)
        if not juego:
            abort(404, message=f"El juego con ID {id} no existe.")  # <-- Corregido sin 'api.'
        args = juego_parser.parse_args()
        juego.nombre = args['nombre']
        juego.descripcion = args['descripcion']
        juego.precio = args['precio']
        db.session.commit()
        return juego, 200

    def delete(self, id):
        juego = Juego.query.get(id)
        if not juego:
            abort(404, message=f"El juego con ID {id} no existe.")  # <-- Corregido sin 'api.'
        db.session.delete(juego)
        db.session.commit()
        return '', 204

api.add_resource(JuegoList, '/juegos')
api.add_resource(JuegoResource, '/juegos/<int:id>')