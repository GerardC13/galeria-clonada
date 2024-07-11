from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from pymongo import MongoClient
import os

app = Flask(__name__)

# Configuración de la conexión a MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['fondos_flask']
coleccion = db['fondos']

# Configuración de la carpeta de subida de archivos
UPLOAD_FOLDER = './static/fondos'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
EXTENSIONES = ['png', 'jpg', 'jpeg']

def archivo_permitido(nombre):
    return '.' in nombre and nombre.rsplit('.', 1)[1].lower() in EXTENSIONES
    
@app.route('/')
def index():
    fondos = list(coleccion.find({}))
    for fondo in fondos:
        fondo['_id'] = str(fondo['_id'])
    activo = {
        'todos': 'active',
        'animales': '',
        'naturaleza': '',
        'ciudad': '',
        'deporte': '',
        'personas': ''
    }
    
    return render_template('index.html', lista=fondos,activo=activo)

@app.route('/cancelar', methods=['POST'])
def cancelar():
    fondos = list(coleccion.find({}))
    for fondo in fondos:
        fondo['_id'] = str(fondo['_id'])
    activo = {
        'todos': 'active',
        'animales': '',
        'naturaleza': '',
        'ciudad': '',
        'deporte': '',
        'personas': ''
    }
    
    return render_template('index.html', lista=fondos,activo=activo)

@app.route('/galeria')
def galeria():
    fondos = list(coleccion.find({}))
    for fondo in fondos:
        fondo['_id'] = str(fondo['_id'])
    activo = {
        'todos': 'active',
        'animales': '',
        'naturaleza': '',
        'ciudad': '',
        'deporte': '',
        'personas': ''
    }
    
    return render_template('index.html', lista=fondos,activo=activo)

@app.route('/galeria/<tema>')
def galeria1(tema):
    if tema == 'Animales':
        fondos = list(coleccion.find({'tags': 'Animales'}))
    elif tema == 'Naturaleza':
        fondos = list(coleccion.find({'tags': 'Naturaleza'}))
    elif tema == 'Ciudad':
        fondos = list(coleccion.find({'tags': 'Ciudad'}))
    elif tema == 'Deporte':
        fondos = list(coleccion.find({'tags': 'Deporte'}))
    elif tema == 'Personas':
        fondos = list(coleccion.find({'tags': 'Personas'}))
    else:
        # Manejo de casos donde el tema no coincide con ningún tag
        fondos = list(coleccion.find({}))

    for fondo in fondos:
        fondo['_id'] = str(fondo['_id'])

    activo = {
        'todos': '',
        'animales': 'active' if tema == 'animales' else '',
        'naturaleza': 'active' if tema == 'naturaleza' else '',
        'ciudad': 'active' if tema == 'ciudad' else '',
        'deporte': 'active' if tema == 'deporte' else '',
        'personas': 'active' if tema == 'personas' else ''
    }

    return render_template('index.html', lista=fondos, activo=activo)


@app.route('/aportar', methods=['GET'])
def uploader():
    archivos = list(coleccion.find())
    for archivo in archivos:
        archivo['_id'] = str(archivo['_id'])
    
    activo = {
        'todos': 'active',
        'animales': '',
        'naturaleza': '',
        'ciudad': '',
        'deporte': '',
        'personas': ''
    }
    return render_template('aportar.html', lista=archivos, t='Seleccione una imagen para cargar', activo=activo)

@app.route('/insertar', methods=['POST'])
def insertar():
    mensaje = 'Seleccione una imagen para cargar'
    titulo = request.form.get('titulo')
    descripcion = request.form.get('descripcion')
    tags = []
    if 'animales' in request.form:
        tags.append('Animales')
    if 'naturaleza' in request.form:
        tags.append('Naturaleza')
    if 'ciudad' in request.form:
        tags.append('Ciudad')
    if 'deporte' in request.form:
        tags.append('Deporte')
    if 'personas' in request.form:
        tags.append('Personas')

    archivo = request.files['archivo']
    if archivo.filename == '':
        mensaje = 'Hay que seleccionar un archivo.'
    else:
        if archivo_permitido(archivo.filename):
            nombre_archivo = secure_filename(archivo.filename)
            archivo.save(os.path.join(app.config['UPLOAD_FOLDER'], nombre_archivo))
            mensaje = 'Imagen cargada correctamente.'

            coleccion.insert_one({
                'titulo': titulo,
                'descripcion': descripcion,
                'fondo': nombre_archivo,
                'tags': tags
            })
        else:
            mensaje = 'No ha seleccionado un archivo de imagen válido.'

    return render_template('aportar.html', mensaje=mensaje)

@app.errorhandler(404)
def ruta_no_valida(e):
    return "<h3>Lo siento, no encuentro la página.<br/> Puede <a href='/'>regresar</a> a la pagina principal</h3>"

if __name__ == '__main__':
    app.run(debug=True)