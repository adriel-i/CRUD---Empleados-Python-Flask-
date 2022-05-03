from flask import Flask
from flask import render_template, request, redirect, url_for, flash
from flaskext.mysql import MySQL
from flask import send_from_directory
from datetime import datetime
import os

app = Flask(__name__)
# flash sirve para enviar mensajes
# llave secreta
app.secret_key = "development"

mysql = MySQL()
# datos de la base de datos
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'sistema_empleados'
# crear conexion de bd
mysql.init_app(app)

CARPETA = os.path.join('uploads')
app.config['CARPETA'] = CARPETA

# acceso a la carpeta uploads para las imagenes
@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
	return send_from_directory(app.config['CARPETA'],nombreFoto)

# - - - (pagina principal)
@app.route('/')
def index():

	sql = "SELECT * FROM empleados;"
	
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.execute(sql)
	# trae todo los datos
	empleados = cursor.fetchall()
	# muestra los datos
	print(empleados)
	conn.commit()

	return render_template('empleados/index.html', empleados = empleados)

# - - - ruta eliminar empleado (decimos que reecibimos un entero que es un id)
@app.route('/destroy/<int:id>')
def destroy(id):

	conn = mysql.connect()
	cursor = conn.cursor()
	# buscamos los datos
	cursor.execute('SELECT foto FROM empleados WHERE id_empleado = %s', id)
	# seleccionamos la fila
	fila = cursor.fetchall()
	# removemos la imagen
	os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))

	cursor.execute("DELETE FROM empleados WHERE id_empleado=%s",(id))
	conn.commit()
	# redirecciona (a la pagina anterior en este caso)
	return redirect('/')

# - - - formulario editar
@app.route('/edit/<int:id>')
def edit(id):
	
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.execute("SELECT * FROM empleados WHERE id_empleado = %s",(id))
	empleados = cursor.fetchall()
	conn.commit()
	print(empleados)

	return render_template('empleados/edit.html', empleados = empleados)

# - - - procesar modificacion
@app.route('/update', methods=['POST'])
def update():

	_nombre = request.form['txtNombre']
	_nombre = request.form['txtNombre']
	_apellido = request.form['txtApellido']
	_correo = request.form['txtCorreo']
	_foto = request.files['txtFoto']
	id = request.form['txtId']

	sql = "UPDATE empleados SET nombre = %s, apellido = %s, correo = %s WHERE id_empleado = %s;"
	
	datos = (_nombre, _apellido, _correo, id)
	conn = mysql.connect()
	cursor = conn.cursor()

	now = datetime.now()
	tiempo = now.strftime("%Y%H%M%S")

	if _foto.filename != '':
		nuevoNombreFoto = tiempo + _foto.filename
		_foto.save("uploads/"+nuevoNombreFoto)
		# buscamos como se llama la foto
		cursor.execute('SELECT foto FROM empleados WHERE id_empleado = %s', id)
		fila = cursor.fetchall()

		os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
		cursor.execute("UPDATE empleados SET foto = %s WHERE id_empleado = %s", (nuevoNombreFoto, id))
		conn.commit()


	cursor.execute(sql, datos)
	conn.commit()

	return redirect('/')


# - - - formulario crear
@app.route('/create')
def create():
	return render_template('empleados/create.html')

# - - - ruta guardar empleado
@app.route('/store', methods=['POST'])
def storage():

	_nombre = request.form['txtNombre']
	_apellido = request.form['txtApellido']
	_correo = request.form['txtCorreo']
	_foto = request.files['txtFoto']

	if _nombre =='' or _apellido =='' or _correo =='':
		# envia el mensaje al template 'create'
		flash('Rellene los datos de los campos')
		return redirect(url_for('create'))

	now = datetime.now()
	tiempo = now.strftime("%Y%H%M%S")

	if _foto.filename != '':
		nuevoNombreFoto = tiempo + _foto.filename
		_foto.save("uploads/"+nuevoNombreFoto)

	sql = "INSERT INTO `empleados` (`id_empleado`, `nombre`, `apellido`, `correo`, `foto`) VALUES (NULL, %s, %s, %s, %s);"
	
	datos = (_nombre, _apellido, _correo, nuevoNombreFoto)
	# conexion
	conn = mysql.connect()
	# lugar donde vamos a almacenar toda la informacion
	cursor = conn.cursor()
	# ejecucion de datos
	cursor.execute(sql, datos)
	# cierre de conexion
	conn.commit()

	return redirect('/')


if  __name__ == '__main__':
	app.run(debug=True)