from flask import Flask, request, jsonify, session, redirect, url_for, render_template, flash
from flask.scaffold import setupmethod

from setupOracle import *
from setupPostgreSQL import *
import os
import webbrowser
import dynamic_html
import diccionarioInyecciones

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secreto para sesiones seguras



# Ruta para la página de índice del laboratorio
@app.route('/index')
def index():
    return render_template('index.html', sql_injections=diccionarioInyecciones.sql_injections)

# Rutas dinámicas para inicio de sesión de SQL Injection en Oracle y PostgreSQL
@app.route('/login/oracle/<tipo_sqli>', methods=['GET', 'POST'])
def login_oracle(tipo_sqli):
    return login_sqli(tipo_sqli, database="Oracle")

@app.route('/login/postgres/<tipo_sqli>', methods=['GET', 'POST'])
def login_postgres(tipo_sqli):
    return login_sqli(tipo_sqli, database="Postgres")

# Función de inicio de sesión común para manejar explicaciones dinámicas y autenticación
def login_sqli(tipo_sqli, database):
    sqli_info = diccionarioInyecciones.sql_injections.get(tipo_sqli)
    if not sqli_info:
        return "Tipo de SQL Injection no encontrado.", 404

    # Selecciona la función de autenticación insegura según el tipo de SQL Injection y la base de datos
    auth_function = sqli_info["function_oracle"] if database == "Oracle" else sqli_info["function_postgres"]

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Llama a la función de autenticación insegura
        result = auth_function(username, password)
        print("result en app.py",result)
        if result:



            # Creamos card para mostrar la sentencia
            cardSentencia = dynamic_html.generarTarjetaInformacion("Sentencia SQL", result['sentencia'])
            print("cardSentencia",cardSentencia)
            flash(cardSentencia,category='Sentencia')

            # Enviamos el resultado de la sentencia (no existe resultado en caso de error en las blind)
            if 'resultado' in result:
                if 'auth' in result:
                    flash("Bienvenido, sesión iniciada con éxito", category='welcome')
                flash(str(result['resultado']), category='Resultado')
            else:
                flash("Usuario o contraseñas incorrectos", "error")



            #return resultado_sentencia
        else:
            flash(str(result), "error")
            return redirect(url_for(f'login_{database.lower()}', tipo_sqli=tipo_sqli))

    # Renderiza login.html con el contenido dinámico del SQL Injection
    return render_template('login.html', title=sqli_info["title"], description=sqli_info["description"], database=database, credenciales=sqli_info["credenciales"])

# Ruta protegida de ejemplo
@app.route('/home')
def home():
    if 'user' in session:
        return jsonify({"message": f"Bienvenido, {session['user']}"})
    return redirect(url_for('login_oracle', tipo_sqli="database_error"))

# Inicialización de la conexión a Oracle y configuración de tablas
def initialize_databaseOracle():
    print("Inicializando base de datos Oracle...")
    conexionOracle = dbConectarOracle()
    if conexionOracle:
        configuracionTablas_oracle(conexionOracle)
        dbDesconectar(conexionOracle)
    else:
        print("Error al conectar con la base de datos Oracle")

# Inicialización de la conexión a PostgreSQL y configuración de tablas
def initialize_databasePostgreSQL():
    conexionPostgreSQL = dbConectarPostgreSQL()
    if conexionPostgreSQL:
        configuracion_tablas_postgresql(conexionPostgreSQL)
        dbDesconectar(conexionPostgreSQL)
    else:
        print("Error al conectar con la base de datos PostgreSQL")

if __name__ == '__main__':
    # Inicializa las bases de datos
    initialize_databaseOracle()
    initialize_databasePostgreSQL()
    # Abre la página de inicio automáticamente en el navegador
    webbrowser.open("http://127.0.0.1:5000/index")
    app.run()