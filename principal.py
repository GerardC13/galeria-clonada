from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os
from pymongo import MongoClient
from bson.objectid import ObjectId

EXTENSIONES = ['png', 'jpg', 'jpeg']
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = './static/fondos'

# Configuración de la conexión a MongoDB
client = MongoClient('mongodb://localhost:27017/')  # Asegúrate de que MongoDB esté corriendo
db = client['fondos_flask']
coleccion = db['fondos']

def archivo_permitido(nombre):
    return '.' in nombre and nombre.rsplit('.', 1)[1].lower() in EXTENSIONES

@app.route('/')
@app.route('/aportar', methods=['GET', 'POST'])
def uploader():
    texto = 'Seleccione una imagen para cargar'
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')
        tags = request.form.get('tags')
        tags = [tag.strip() for tag in tags.split(',')]  # Convertir los tags en una lista

        f = request.files['archivo']
        if f.filename == '':
            texto = 'Hay que seleccionar un archivo.'
        else:
            if archivo_permitido(f.filename):
                archivo = secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'], archivo))
                texto = 'Imagen Cargada.'

                # Guardar los datos en MongoDB
                coleccion.insert_one({
                    'titulo': titulo,
                    'descripcion': descripcion,
                    'fondo': archivo,
                    'tags': tags
                })
            else:
                texto = 'No ha seleccionado un archivo de imagen.'

    archivos = list(coleccion.find())
    # Convertir _id a cadena
    for archivo in archivos:
        archivo['_id'] = str(archivo['_id'])
    
    # Inicializa las variables 'activo'
    activo = {
        'todos': 'active',
        'animales': '',
        'naturaleza': '',
        'ciudad': '',
        'deporte': '',
        'personas': ''
    }

    return render_template('index.html', lista=archivos, t=texto, activo=activo)

@app.route('/galeria')
def galeria():
    tema = request.args.get('tema')
    if tema:
        archivos = list(coleccion.find({'tags': tema}))
    else:
        archivos = list(coleccion.find())
    
    # Convertir _id a cadena
    for archivo in archivos:
        archivo['_id'] = str(archivo['_id'])
    
    # Inicializa las variables 'activo'
    activo = {
        'todos': 'active' if not tema else '',
        'animales': 'active' if tema == 'animales' else '',
        'naturaleza': 'active' if tema == 'naturaleza' else '',
        'ciudad': 'active' if tema == 'ciudad' else '',
        'deporte': 'active' if tema == 'deporte' else '',
        'personas': 'active' if tema == 'personas' else ''
    }

    return render_template('galeria.html', lista=archivos, activo=activo)

@app.route('/aportar', methods=['POST'])
def aportar():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        desc = request.form.get('descripcion')
        
        # Manejo del archivo subido
        if 'archivo' in request.files:
            archivo = request.files['archivo']
            if archivo.filename != '':
                # Guardar el archivo en tu directorio de archivos estáticos
                archivo.save('./static/fondos/' + archivo.filename)

                # Insertar los datos en MongoDB
                coleccion.insert_one({
                    'titulo': titulo,
                    'descripcion': desc,
                    'archivo': archivo.filename  # Guardamos solo el nombre del archivo
                })

                # Redireccionar a una página de confirmación o aportar.html nuevamente
                return render_template('aportar.html', mensaje='Imagen cargada correctamente.')
    
    # Si hay un problema, renderiza el formulario de aportar.html con un mensaje de error
    return render_template('aportar.html', mensaje='Error al cargar la imagen.')

@app.errorhandler(404)
def ruta_no_valida(e):
    return "<h3>Lo siento, no encuentro la página.<br/> Puede <a href='/'>regresar</a> a la pagina principal</h3>"

if __name__ == '__main__':
    app.run(debug=True)
