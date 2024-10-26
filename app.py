from flask import Flask, request, jsonify, session, redirect, url_for, render_template, flash
from setupOracle import dbConectar, dbDesconectar, configuracionTablas, login_seguro
import os
import webbrowser  # Para abrir la página automáticamente

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secreto para sesiones seguras


# Lista de diccionarios para cada tipo de SQL Injection
sql_injections = [
    {
        "name": "SQL Injection Básico",
        "description": "Práctica básica de SQL Injection.",
        "route_oracle": "sqli_basico_oracle",
        "route_postgres": "sqli_basico_postgres"
    },
    {
        "name": "SQL Injection con UNION",
        "description": "Inyección SQL utilizando el operador UNION.",
        "route_oracle": "sqli_union_oracle",
        "route_postgres": "sqli_union_postgres"
    },
    {
        "name": "SQL Injection Blindado",
        "description": "Práctica de inyección SQL blindada.",
        "route_oracle": "sqli_blind_oracle",
        "route_postgres": "sqli_blind_postgres"
    },
    # Agrega más tipos de SQL Injection según sea necesario
]

# Ruta para la página de índice del laboratorio
@app.route('/index')
def index():
    return render_template('index.html', sql_injections=sql_injections)

# Ruta de inicio de sesión
@app.route('/login', methods=['GET', 'POST'])
def login_route():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Llamada a la función de login (de setupOracle) que verifica las credenciales
        if login_seguro(username, password):
            session['user'] = username
            return redirect(url_for('home'))
        else:
            flash("Usuario o contraseña incorrectos", "error")  # Envía el mensaje de error a la plantilla
            return redirect(url_for('login_route'))  # Redirige a la misma página de login
    return render_template('login.html')


# Ruta de login inseguro
@app.route('/login_inseguro_base', methods=['GET','POST'])
def login_inseguro_base():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # Llamada a la función de login (de setupOracle) que verifica las credenciales
        if login_seguro(username, password):
            session['user'] = username
            return redirect(url_for('home'))
        else:
            flash("Usuario o contraseña incorrectos", "error")  # Envía el mensaje de error a la plantilla
            return redirect(url_for('login_route'))  # Redirige a la misma página de login

    return render_template('login.html')


# Ruta protegida de ejemplo
@app.route('/home')
def home():
    if 'user' in session:
        return jsonify({"message": f"Bienvenido, {session['user']}"})
    return redirect(url_for('login_route'))


# Inicialización de la conexión a la BD y configuración de tablas
@app.before_first_request
def initialize_database():
    conexion = dbConectar()
    if conexion:
        configuracionTablas(conexion)
        dbDesconectar(conexion)
    else:
        print("Error al conectar con la base de datos")


if __name__ == '__main__':
    # Abre la página de inicio automáticamente en el navegador
    webbrowser.open("http://127.0.0.1:5000/index")  # Redirige a la página de login en lugar de home
    app.run()
