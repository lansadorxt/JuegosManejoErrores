import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_login import LoginManager, login_required
from werkzeug.exceptions import HTTPException, BadRequest, MethodNotAllowed
from extensions import db



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/juegos'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'una_clave_muy_secreta_y_dificil'

db.init_app(app)

file_handler = logging.FileHandler('errors.log')
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter('[%(asctime)s] %(levelname)s en %(module)s: %(message)s')
file_handler.setFormatter(formatter)
app.logger.addHandler(file_handler)

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

import controllers

from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')

from api.routes import api_bp
app.register_blueprint(api_bp, url_prefix='/api')

with app.app_context():
    db.create_all()


@app.errorhandler(HTTPException)
def handle_api_error(e):
    if request.path.startswith('/api/'):
        response = e.get_response()
        response.data = jsonify(code=e.code, name=e.name, description=e.description).data
        response.content_type = 'application/json'
        return response
    return e

@app.errorhandler(BadRequest)
def handle_400(e):
    return render_template('400.html'), 400

@app.errorhandler(404)
def handle_404(e):
    return render_template('404.html'), 404

@app.errorhandler(MethodNotAllowed)
def handle_405(e):
    return render_template('405.html'), 405

@app.errorhandler(500)
def handle_500(e):
    app.logger.error(f"Error 500 detectado: {e}")
    return render_template('500.html'), 500

@app.route('/')
@app.route('/juegos')
@login_required
def juegos():
    lista_juegos = controllers.obtener_juegos()
    return render_template('juegos.html', juegos=lista_juegos)

@app.route('/videogame/<int:id>')
@login_required
def ver_videojuego(id):
    juego = controllers.obtener_juego_por_id(id)
    if not juego:
        abort(404)
    # Ejemplo de validación: si se pasa un argumento invalido en querystring (?test=bad), lanza 400
    if request.args.get('error') == 'bad':
        abort(400)
    return render_template('editar_juego.html', juego=juego)

@app.route('/agregar_juego')
@login_required
def formulario_agregar_juego():
    return render_template('agregar_juego.html')

@app.route('/guardar_juego', methods=['POST'])
@login_required
def guardar_juego():
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    controllers.insertar_juego(nombre, descripcion, precio)
    return redirect('/juegos')

@app.route('/eliminar_juego', methods=['POST'])
@login_required
def eliminar_juego():
    id = request.form['id']
    controllers.eliminar_juego(id)
    return redirect('/juegos')

@app.route('/formulario_editar_juego/<int:id>')
@login_required
def editar_juego(id):
    juego = controllers.obtener_juego_por_id(id)
    if not juego:
        abort(404)
    return render_template('editar_juego.html', juego=juego)

@app.route('/actualizar_juego', methods=['POST'])
@login_required
def actualizar_juego():
    id = request.form['id']
    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    precio = request.form['precio']
    controllers.actualizar_juego(id, nombre, descripcion, precio)
    return redirect('/juegos')

# Ruta de prueba para forzar una excepción no controlada (Error 500 y Logging)
@app.route('/forzar_error_500')
def forzar_error_500():
    try:
        resultado = 1 / 0
    except Exception as ex:
        app.logger.error(f"Excepción forzada en /forzar_error_500: {ex}", exc_info=True)
        raise ex

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)